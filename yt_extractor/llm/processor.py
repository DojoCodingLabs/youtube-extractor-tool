"""LLM processing functionality."""
import json
from typing import Any, Dict, List, Optional

from litellm import completion
from rich.console import Console

from ..core.config import config
from ..core.exceptions import LLMProcessingError
from ..core.models import TranscriptLine, VideoMeta
from ..utils.transcript import join_transcript_lines
from ..utils.cache import cache
from ..utils.retry import llm_retry
from .prompts import PromptTemplates

console = Console()


class LLMProcessor:
    """Handles all LLM interactions for content extraction."""
    
    def __init__(self):
        """Initialize the LLM processor."""
        self.model = config.llm_model
    
    def process_video(self, meta: VideoMeta, transcript: List[TranscriptLine]) -> str:
        """
        Process a video through the complete pipeline.
        
        Returns formatted markdown content.
        """
        console.print(f"[blue]Processing video: {meta.title}[/blue]")
        
        # Process full transcript at once
        transcript_text = join_transcript_lines(transcript)
        console.print(f"[dim]Processing full transcript ({len(transcript_text)} characters)[/dim]")
        
        # Analyze complete transcript
        analysis = self._analyze_full_transcript(transcript_text)
        
        # Generate final markdown
        markdown = self._generate_markdown(meta, analysis)
        
        return markdown
    
    def _analyze_full_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """Analyze the complete transcript for insights and structure."""
        console.print("[dim]Analyzing full transcript for insights...[/dim]")
        
        prompt = PromptTemplates.format_full_analysis_prompt(transcript_text)
        
        analysis = self._run_llm_json(
            system_prompt="You are an expert content analyst extracting valuable insights from complete video transcripts.",
            user_prompt=prompt,
            temperature=0.3
        )
        
        # Ensure required keys exist
        analysis.setdefault("summary", "")
        analysis.setdefault("key_insights", [])
        analysis.setdefault("frameworks", [])
        analysis.setdefault("key_moments", [])
        
        return analysis
    
    def _generate_markdown(self, meta: VideoMeta, analysis: Dict[str, Any]) -> str:
        """Generate final markdown report."""
        console.print("[dim]Generating markdown report...[/dim]")
        
        meta_json = json.dumps({
            "title": meta.title,
            "channel": meta.channel,
            "published": meta.published_at,
            "duration_sec": meta.duration_sec,
            "url": meta.url,
            "tags": meta.tags,
        }, ensure_ascii=False)
        
        analysis_json = json.dumps(analysis, ensure_ascii=False)
        
        prompt = PromptTemplates.format_final_md_prompt(meta_json, analysis_json)
        
        markdown = self._run_llm_text(
            system_prompt="You create comprehensive, well-structured Markdown reports from video analysis data.",
            user_prompt=prompt,
            temperature=0.2
        )
        
        return markdown
    
    @llm_retry
    def _run_llm_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Call LLM and parse JSON response with caching."""
        # Check cache first
        prompt_hash = cache.hash_prompt(system_prompt, user_prompt, self.model)
        cached_response = cache.get_llm_response(prompt_hash)
        
        if cached_response:
            console.print("[dim]Using cached LLM response[/dim]")
            return cached_response
        
        # Adjust temperature for GPT-5 models (they only support temperature=1)
        if "gpt-5" in self.model.lower():
            temperature = 1.0
        
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            }
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            response = completion(**kwargs)
            
            content = response["choices"][0]["message"]["content"]

            # Debug GPT-5 response issues
            if not content or content.strip() == "":
                console.print(f"[red]GPT-5 returned empty content. Response type: {type(response)}[/red]")
                raise LLMProcessingError("GPT-5 returned empty content - possible rate limit or model issue")

            # Try to parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as json_err:
                console.print(f"[yellow]JSON parsing failed. Raw content: {content[:200]}...[/yellow]")

                # Try to clean and extract JSON for GPT-5 responses
                cleaned_content = content.strip()

                # Remove markdown code blocks if present
                if cleaned_content.startswith("```json"):
                    cleaned_content = cleaned_content[7:]
                if cleaned_content.startswith("```"):
                    cleaned_content = cleaned_content[3:]
                if cleaned_content.endswith("```"):
                    cleaned_content = cleaned_content[:-3]

                # Try parsing cleaned content
                try:
                    result = json.loads(cleaned_content.strip())
                except json.JSONDecodeError:
                    # Try to extract JSON substring
                    start = cleaned_content.find("{")
                    end = cleaned_content.rfind("}")
                    if start != -1 and end != -1 and end > start:
                        json_content = cleaned_content[start:end + 1]
                        console.print(f"[dim]Trying extracted JSON: {json_content[:100]}...[/dim]")

                        # Try to fix common JSON issues
                        try:
                            result = json.loads(json_content)
                        except json.JSONDecodeError as extract_err:
                            console.print(f"[yellow]JSON has errors, attempting to fix: {extract_err}[/yellow]")

                            # Fix trailing commas - common GPT-5 issue
                            import re
                            fixed_json = re.sub(r',\s*}', '}', json_content)  # Remove trailing commas before }
                            fixed_json = re.sub(r',\s*]', ']', fixed_json)    # Remove trailing commas before ]

                            try:
                                result = json.loads(fixed_json)
                                console.print("[green]✅ Fixed JSON trailing commas[/green]")
                            except json.JSONDecodeError as final_err:
                                console.print(f"[red]Final JSON parsing failed: {final_err}[/red]")
                                raise LLMProcessingError(f"Failed to parse LLM JSON response. Original error: {json_err}, Content: {content[:300]}")
                    else:
                        raise LLMProcessingError(f"No JSON found in LLM response. Content: {content[:300]}")
            
            # Cache the result
            cache.set_llm_response(prompt_hash, result)
            return result
                
        except Exception as e:
            # If GPT-5 fails consistently, suggest fallback
            if "gpt-5" in self.model.lower():
                console.print(f"[yellow]GPT-5 failed: {e}[/yellow]")
                console.print("[yellow]Consider using GPT-4o-mini for more reliable processing[/yellow]")
            raise LLMProcessingError(f"LLM JSON processing failed: {e}")
    
    @llm_retry
    def _run_llm_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None
    ) -> str:
        """Call LLM and return text response with caching."""
        # Check cache first
        prompt_hash = cache.hash_prompt(system_prompt, user_prompt, self.model)
        cached_response = cache.get_llm_response(prompt_hash)
        
        if cached_response and isinstance(cached_response, str):
            console.print("[dim]Using cached LLM response[/dim]")
            return cached_response
        
        # Adjust temperature for GPT-5 models (they only support temperature=1)
        if "gpt-5" in self.model.lower():
            temperature = 1.0
        
        try:
            kwargs = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": temperature,
            }
            if max_tokens is not None:
                kwargs["max_tokens"] = max_tokens

            response = completion(**kwargs)
            
            result = response["choices"][0]["message"]["content"]
            
            # Cache the result
            cache.set_llm_response(prompt_hash, result)
            return result
            
        except Exception as e:
            raise LLMProcessingError(f"LLM text processing failed: {e}")