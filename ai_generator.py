"""
OpenAI Content Generator
Uses OpenAI API to generate blog post content from prompts
"""
import os
from openai import OpenAI
from typing import Optional, Dict
import logging


class AIContentGenerator:
    """Generate blog post content using OpenAI"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    def generate_blog_post(self, 
                          prompt: str,
                          tone: str = "professional",
                          length: str = "medium",
                          include_seo: bool = True,
                          categories: Optional[str] = None,
                          tags: Optional[str] = None) -> str:
        """
        Generate a complete blog post with frontmatter from a prompt
        
        Args:
            prompt: User's content request/topic
            tone: Writing tone (professional, casual, technical, friendly)
            length: Post length (short ~500 words, medium ~1000 words, long ~2000 words)
            include_seo: Whether to generate SEO metadata
            categories: Suggested categories (comma-separated)
            tags: Suggested tags (comma-separated)
            
        Returns:
            Markdown string with YAML frontmatter
        """
        # Build the system prompt
        system_prompt = self._build_system_prompt(tone, length, include_seo)
        
        # Build user prompt with additional context
        user_prompt = self._build_user_prompt(prompt, categories, tags)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content
            return content
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise
    
    def generate_image_prompt(self, post_content: str) -> str:
        """
        Generate a DALL-E image prompt based on blog post content
        
        Args:
            post_content: The blog post markdown content
            
        Returns:
            Image generation prompt
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating detailed, visually descriptive prompts for AI image generation. Create prompts that are suitable for blog post featured images - professional, clean, and relevant to the content."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this blog post, create a detailed image generation prompt for a featured image (max 100 words):\n\n{post_content[:1000]}"
                    }
                ],
                temperature=0.8,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"OpenAI API error generating image prompt: {str(e)}")
            return "Professional blog post featured image, modern design, clean background"
    
    def _build_system_prompt(self, tone: str, length: str, include_seo: bool) -> str:
        """Build the system prompt based on settings"""
        
        length_guide = {
            "short": "approximately 500-700 words",
            "medium": "approximately 1000-1500 words",
            "long": "approximately 2000-3000 words"
        }
        
        word_count = length_guide.get(length, "approximately 1000-1500 words")
        
        prompt = f"""You are an expert blog post writer. Generate high-quality, engaging blog posts in Markdown format with YAML frontmatter.

Writing Style:
- Tone: {tone}
- Length: {word_count}
- Use clear headings (##, ###) for structure
- Include bullet points and lists where appropriate
- Write engaging introductions and conclusions
- Use examples and explanations

Format Requirements:
1. Start with YAML frontmatter between --- markers
2. Include these frontmatter fields:
   - title: Compelling, SEO-friendly title
   - excerpt: 1-2 sentence summary
   - categories: Array of 2-3 relevant categories
   - tags: Array of 5-7 relevant tags
   - status: draft"""

        if include_seo:
            prompt += """
   - seo_title: SEO-optimized title (50-60 chars)
   - seo_description: Meta description (150-160 chars)
   - keywords: Comma-separated keywords
   - focus_keyword: Primary keyword"""

        prompt += """

3. After frontmatter, write the blog post in Markdown
4. Use proper heading hierarchy (# for title, ## for sections, ### for subsections)
5. Include code blocks with language tags if technical content
6. Use **bold** and *italic* for emphasis

Example structure:
```
---
title: "Your Title Here"
excerpt: "Brief summary"
categories:
  - Category1
  - Category2
tags: [tag1, tag2, tag3]
status: draft
---

# Main Title

Introduction paragraph...

## Section 1

Content...

### Subsection

More content...

## Conclusion

Wrap up...
```

Generate a complete, ready-to-publish blog post."""

        return prompt
    
    def _build_user_prompt(self, prompt: str, categories: Optional[str], tags: Optional[str]) -> str:
        """Build the user prompt with additional context"""
        
        user_prompt = f"Topic/Request: {prompt}\n\n"
        
        if categories:
            user_prompt += f"Suggested categories: {categories}\n"
        if tags:
            user_prompt += f"Suggested tags: {tags}\n"
        
        user_prompt += "\nGenerate the complete blog post with frontmatter now."
        
        return user_prompt
    
    def enhance_existing_content(self, content: str, instruction: str) -> str:
        """
        Enhance or modify existing content
        
        Args:
            content: Existing markdown content
            instruction: What to do (e.g., "make it more technical", "add examples")
            
        Returns:
            Enhanced markdown content
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert blog post editor. Modify the content according to the user's instructions while maintaining markdown format and frontmatter."
                    },
                    {
                        "role": "user",
                        "content": f"Instruction: {instruction}\n\nCurrent content:\n{content}"
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI API error: {str(e)}")
            raise
