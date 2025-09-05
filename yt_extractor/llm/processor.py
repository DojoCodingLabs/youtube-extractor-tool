"""LLM processing functionality."""
import json
from typing import Any, Dict, List

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
            temperature=0.3,
            max_tokens=2500
        )
        
        # Ensure required keys exist
        analysis.setdefault("summary", "")
        analysis.setdefault("key_insights", [])
        analysis.setdefault("frameworks", [])
        analysis.setdefault("timestamps", [])
        
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
            temperature=0.2,
            max_tokens=2500
        )
        
        return markdown
    
    @llm_retry
    def _run_llm_json(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.2, 
        max_tokens: int = 1200
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
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response["choices"][0]["message"]["content"]
            
            # Try to parse JSON
            try:
                result = json.loads(content)
            except json.JSONDecodeError as json_err:
                console.print(f"[yellow]JSON parsing failed. Raw content: {content[:200]}...[/yellow]")
                # Try to extract JSON substring
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1 and end > start:
                    json_content = content[start:end + 1]
                    console.print(f"[dim]Trying extracted JSON: {json_content[:100]}...[/dim]")
                    try:
                        result = json.loads(json_content)
                    except json.JSONDecodeError as extract_err:
                        console.print(f"[red]Extracted JSON also failed: {extract_err}[/red]")
                        raise LLMProcessingError(f"Failed to parse LLM JSON response. Original error: {json_err}, Content: {content[:300]}")
                else:
                    raise LLMProcessingError(f"No JSON found in LLM response. Content: {content[:300]}")
            
            # Cache the result
            cache.set_llm_response(prompt_hash, result)
            return result
                
        except Exception as e:
            raise LLMProcessingError(f"LLM JSON processing failed: {e}")
    
    @llm_retry
    def _run_llm_text(
        self, 
        system_prompt: str, 
        user_prompt: str, 
        temperature: float = 0.2, 
        max_tokens: int = 1600
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
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            result = response["choices"][0]["message"]["content"]
            
            # Cache the result
            cache.set_llm_response(prompt_hash, result)
            return result
            
        except Exception as e:
            raise LLMProcessingError(f"LLM text processing failed: {e}")