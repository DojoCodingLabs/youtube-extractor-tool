"""LLM prompt templates."""


class PromptTemplates:
    """Collection of prompt templates for different processing stages."""
    
    FULL_ANALYSIS_PROMPT = (
        "You are analyzing a complete YouTube video transcript to extract the most valuable insights. "
        "The user wants structured, actionable content with full context understanding.\n\n"
        
        "Return strict JSON with these keys:\n"
        "- 'summary': 2-3 paragraph executive summary of the core message and value\n"
        "- 'key_insights': 8-12 most important insights as detailed paragraphs (not bullet points)\n"
        "- 'frameworks': actionable frameworks/methods with step-by-step breakdowns\n"
        "- 'key_moments': chronological sequence of important events/topics discussed\n\n"
        
        "Guidelines:\n"
        "- Focus on practical, actionable insights that provide real value\n"
        "- Each key insight should be a structured paragraph (3-5 sentences) explaining the concept fully\n"
        "- Include specific examples, strategies, and reasoning from the video\n"
        "- Use the full context to identify overarching themes and connections\n"
        "- Frameworks should be detailed with clear steps and context\n"
        "- Present key moments in chronological order as they appear in the video\n\n"
        
        "Example format:\n"
        '{{\n'
        '  "summary": "Comprehensive 2-3 paragraph overview...",\n'
        '  "key_insights": [\n'
        '    "Detailed paragraph explaining first major insight with context and examples...",\n'
        '    "Another structured paragraph about second key concept..."\n'
        '  ],\n'
        '  "frameworks": [{{"name": "Framework Name", "description": "What it does", "steps": ["Step 1 with details", "Step 2 with context"]}}],\n'
        '  "key_moments": ["First major topic introduced", "Key transition or development", "Important conclusion or call to action"]\n'
        '}}\n\n'
        "Full transcript:\n\n{transcript}"
    )
    
    FINAL_MD_PROMPT = (
        "Create a comprehensive Markdown report for a YouTube video using the analyzed content. "
        "Focus on providing maximum value with structured, detailed insights.\n\n"
        "Video metadata (JSON):\n{meta}\n\n"
        "Analysis results (JSON):\n{analysis}\n\n"
        "Format as Markdown with these sections:\n"
        "# {{title}}\n"
        "- Channel: {{channel}}\n"
        "- Published: {{published}}\n"
        "- Duration: {{duration}}\n"
        "- URL: {{url}}\n\n"
        "## Executive Summary\n"
        "Use the 'summary' from analysis - present as 2-3 well-structured paragraphs.\n\n"
        "## Key Insights\n"
        "Present each insight from 'key_insights' as:\n"
        "### Insight Title\n"
        "Full paragraph content with context, examples, and actionable details.\n\n"
        "## Frameworks & Methods\n"
        "For each framework, format as:\n"
        "### Framework Name\n"
        "Description of what it does and why it's valuable.\n"
        "**Steps:**\n"
        "1. Step with detailed explanation\n"
        "2. Step with context and examples\n"
        "\n\n"
        "## Key Moments\n"
        "Chronological flow of important topics:\n"
        "- Description of key moment or topic\n\n"
        "Return only the Markdown body."
    )
    
    @staticmethod
    def format_full_analysis_prompt(transcript_text: str) -> str:
        """Format the full analysis prompt with complete transcript."""
        return PromptTemplates.FULL_ANALYSIS_PROMPT.format(transcript=transcript_text)
    
    @staticmethod
    def format_final_md_prompt(meta_json: str, analysis_json: str) -> str:
        """Format the final markdown prompt."""
        return PromptTemplates.FINAL_MD_PROMPT.format(
            meta=meta_json, 
            analysis=analysis_json
        )