"""LLM prompt templates."""


class PromptTemplates:
    """Collection of prompt templates for different processing stages."""
    
    MAP_PROMPT = (
        "You are extracting value from a YouTube transcript chunk. "
        "Return strict JSON with keys: 'bullets' (list of 5-10 short points, each include a mm:ss timestamp in [t=mm:ss] form), "
        "'frameworks' (list of objects with 'name', 'steps', and 'timestamp' fields). "
        "Only use the transcript text. No speculation. Keep items atomic and non-overlapping.\n\n"
        "Example format:\n"
        '{{\n'
        '  "bullets": ["Point 1 [t=05:30]", "Point 2 [t=08:15]"],\n'
        '  "frameworks": [{{"name": "Framework Name", "steps": ["Step 1", "Step 2"], "timestamp": "t=10:20"}}]\n'
        '}}\n\n'
        "Transcript chunk:\n\n{chunk}"
    )
    
    REDUCE_PROMPT = (
        "You will merge multiple JSON partial analyses from a single video into a final structured result. "
        "Input is a JSON array where each element has 'bullets' and 'frameworks'. "
        "Your job: deduplicate, keep the strongest items, ensure each has a timestamp. "
        "Return strict JSON with keys: 'bullets' (<=15), 'frameworks' (<=8). "
        "Prefer concise wording."
    )
    
    FINAL_MD_PROMPT = (
        "Create a crisp Markdown report for a YouTube video using the following inputs. "
        "Be clear, skimmable, and executable. Avoid fluff.\n\n"
        "Video meta (JSON):\n{meta}\n\n"
        "Merged analysis (JSON):\n{merged}\n\n"
        "Format as Markdown with these sections:\n"
        "# {{title}}\n"
        "- Channel: {{channel}}\n"
        "- Published: {{published}}\n"
        "- Duration: {{duration}}\n"
        "- URL: {{url}}\n\n"
        "## TL;DR\n"
        "One paragraph summary of the core idea and value.\n\n"
        "## Key Takeaways\n"
        "Bullet list with timestamps like [t=mm:ss]. 8-15 bullets.\n\n"
        "## Frameworks & Models\n"
        "For each framework: **Name** — 3-6 steps as a list. Include source [t=mm:ss].\n\n"
        "## Chapters\n"
        "Infer a simple chapter outline from timestamps present. 5-10 lines of 'mm:ss Title'.\n\n"
        "Return only the Markdown body."
    )
    
    @staticmethod
    def format_map_prompt(chunk_text: str) -> str:
        """Format the map prompt with transcript chunk."""
        return PromptTemplates.MAP_PROMPT.format(chunk=chunk_text)
    
    @staticmethod
    def format_final_md_prompt(meta_json: str, merged_json: str) -> str:
        """Format the final markdown prompt."""
        return PromptTemplates.FINAL_MD_PROMPT.format(
            meta=meta_json, 
            merged=merged_json
        )