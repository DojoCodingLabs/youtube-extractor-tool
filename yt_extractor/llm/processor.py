"""LLM processing functionality."""
import json
from typing import Any, Dict, List

from litellm import completion
from rich.console import Console
from rich.progress import track

from ..core.config import config
from ..core.exceptions import LLMProcessingError
from ..core.models import ExtractedContent, TranscriptLine, VideoMeta
from ..utils.chunking import add_timestamps_to_chunk, chunk_transcript
from ..utils.cache import cache
from ..utils.retry import llm_retry, is_api_rate_limit, is_temporary_api_error
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
        
        # Chunk transcript
        chunks = chunk_transcript(transcript, config.default_chunk_chars)
        console.print(f"[dim]Split into {len(chunks)} chunks[/dim]")
        
        # Map phase - extract from each chunk
        partials = self._map_phase(chunks)
        
        # Reduce phase - merge all extractions
        merged = self._reduce_phase(partials)
        
        # Generate final markdown
        markdown = self._generate_markdown(meta, merged)
        
        return markdown
    
    def _map_phase(self, chunks: List[List[TranscriptLine]]) -> List[Dict[str, Any]]:
        """Extract content from each transcript chunk."""
        partials: List[Dict[str, Any]] = []
        
        for chunk in track(chunks, description="Extracting from chunks..."):
            chunk_text = add_timestamps_to_chunk(chunk)
            prompt = PromptTemplates.format_map_prompt(chunk_text)
            
            result = self._run_llm_json(
                system_prompt="You extract JSON-only analyses from transcripts.",
                user_prompt=prompt,
                temperature=0.1,
                max_tokens=900
            )
            partials.append(result)
        
        return partials
    
    def _reduce_phase(self, partials: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge and deduplicate extracted content."""
        console.print("[dim]Merging and deduplicating content...[/dim]")
        
        user_prompt = (
            PromptTemplates.REDUCE_PROMPT + 
            "\n\nHere is the JSON array to merge:\n" + 
            json.dumps(partials, ensure_ascii=False)
        )
        
        merged = self._run_llm_json(
            system_prompt="You merge JSON partials into a clean, deduplicated result.",
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=1200
        )
        
        # Ensure required keys exist
        merged.setdefault("bullets", [])
        merged.setdefault("frameworks", [])
        
        return merged
    
    def _generate_markdown(self, meta: VideoMeta, merged: Dict[str, Any]) -> str:
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
        
        merged_json = json.dumps(merged, ensure_ascii=False)
        
        prompt = PromptTemplates.format_final_md_prompt(meta_json, merged_json)
        
        markdown = self._run_llm_text(
            system_prompt="You write crisp, skimmable Markdown for operators.",
            user_prompt=prompt,
            temperature=0.2,
            max_tokens=1800
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