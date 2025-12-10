"""
Markdown Parser with Frontmatter Support
Extracts metadata, images, and converts markdown to HTML for WordPress
"""
import frontmatter
import markdown
import re
from typing import Dict, List, Optional
from pathlib import Path


class MarkdownParser:
    """Parse markdown files with YAML frontmatter for WordPress posts"""
    
    def __init__(self, markdown_content: str = None, markdown_file: str = None):
        """
        Initialize parser with markdown content or file
        
        Args:
            markdown_content: Raw markdown string
            markdown_file: Path to markdown file
        """
        if markdown_file:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                self.raw_content = f.read()
        elif markdown_content:
            self.raw_content = markdown_content
        else:
            raise ValueError("Either markdown_content or markdown_file must be provided")
        
        # Parse frontmatter
        self.post = frontmatter.loads(self.raw_content)
        self.metadata = self.post.metadata
        self.content = self.post.content
        
    def get_title(self) -> str:
        """Extract post title from frontmatter or first H1"""
        if 'title' in self.metadata:
            return self.metadata['title']
        
        # Try to extract from first H1
        h1_match = re.search(r'^#\s+(.+)$', self.content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1)
        
        return "Untitled Post"
    
    def get_excerpt(self) -> Optional[str]:
        """Extract excerpt from frontmatter or generate from content"""
        if 'excerpt' in self.metadata:
            return self.metadata['excerpt']
        
        if 'description' in self.metadata:
            return self.metadata['description']
        
        # Generate excerpt from first paragraph (limit 200 chars)
        first_para = re.search(r'^(?!#)(.+?)(?:\n\n|\Z)', self.content, re.MULTILINE | re.DOTALL)
        if first_para:
            excerpt = first_para.group(1).strip()
            if len(excerpt) > 200:
                excerpt = excerpt[:197] + '...'
            return excerpt
        
        return None
    
    def get_categories(self) -> List[str]:
        """Extract categories from frontmatter"""
        categories = self.metadata.get('categories', [])
        if isinstance(categories, str):
            return [cat.strip() for cat in categories.split(',')]
        return categories if isinstance(categories, list) else []
    
    def get_tags(self) -> List[str]:
        """Extract tags from frontmatter"""
        tags = self.metadata.get('tags', [])
        if isinstance(tags, str):
            return [tag.strip() for tag in tags.split(',')]
        return tags if isinstance(tags, list) else []
    
    def get_featured_image(self) -> Optional[str]:
        """Extract featured image path from frontmatter"""
        return self.metadata.get('featured_image') or self.metadata.get('image')
    
    def get_seo_metadata(self) -> Dict:
        """
        Extract SEO metadata for Yoast/RankMath plugins
        
        Returns:
            dict with SEO fields (title, description, keywords, etc.)
        """
        seo = {}
        
        # SEO Title
        if 'seo_title' in self.metadata:
            seo['title'] = self.metadata['seo_title']
        elif 'meta_title' in self.metadata:
            seo['title'] = self.metadata['meta_title']
        
        # SEO Description
        if 'seo_description' in self.metadata:
            seo['description'] = self.metadata['seo_description']
        elif 'meta_description' in self.metadata:
            seo['description'] = self.metadata['meta_description']
        elif 'description' in self.metadata:
            seo['description'] = self.metadata['description']
        
        # Keywords
        if 'keywords' in self.metadata:
            keywords = self.metadata['keywords']
            if isinstance(keywords, list):
                seo['keywords'] = ', '.join(keywords)
            else:
                seo['keywords'] = keywords
        
        # Focus keyword (Yoast)
        if 'focus_keyword' in self.metadata:
            seo['focus_keyword'] = self.metadata['focus_keyword']
        
        return seo
    
    def get_status(self) -> str:
        """Get post status (draft, publish, etc.)"""
        return self.metadata.get('status', 'draft')
    
    def get_image_references(self) -> List[Dict[str, str]]:
        """
        Find all image references in markdown content
        
        Returns:
            List of dicts with 'alt', 'path', and 'markdown_syntax'
        """
        images = []
        
        # Match markdown image syntax: ![alt](path "optional title")
        pattern = r'!\[([^\]]*)\]\(([^\)]+?)(?:\s+"([^"]*)")?\)'
        
        for match in re.finditer(pattern, self.content):
            alt_text = match.group(1)
            image_path = match.group(2)
            title = match.group(3)
            
            images.append({
                'alt': alt_text,
                'path': image_path,
                'title': title,
                'markdown_syntax': match.group(0)
            })
        
        return images
    
    def to_html(self, extensions: Optional[List[str]] = None) -> str:
        """
        Convert markdown content to HTML
        
        Args:
            extensions: List of markdown extensions to use
            
        Returns:
            HTML string
        """
        if extensions is None:
            # Default extensions for better formatting
            extensions = [
                'extra',           # Tables, fenced code, etc.
                'codehilite',      # Syntax highlighting
                'nl2br',           # Newline to <br>
                'sane_lists',      # Better list handling
                'toc'              # Table of contents
            ]
        
        md = markdown.Markdown(extensions=extensions)
        html_content = md.convert(self.content)
        
        return html_content
    
    def replace_image_references(self, image_map: Dict[str, str]) -> str:
        """
        Replace local image paths with WordPress URLs
        
        Args:
            image_map: Dict mapping local paths to WordPress media URLs
            
        Returns:
            Markdown content with updated image URLs
        """
        updated_content = self.content
        
        for local_path, wp_url in image_map.items():
            # Replace the path in markdown syntax
            updated_content = updated_content.replace(local_path, wp_url)
        
        return updated_content
    
    def get_all_metadata(self) -> Dict:
        """Get all parsed metadata in one dict"""
        return {
            'title': self.get_title(),
            'excerpt': self.get_excerpt(),
            'categories': self.get_categories(),
            'tags': self.get_tags(),
            'featured_image': self.get_featured_image(),
            'status': self.get_status(),
            'seo': self.get_seo_metadata(),
            'custom_fields': {k: v for k, v in self.metadata.items() 
                            if k not in ['title', 'excerpt', 'categories', 'tags', 
                                       'featured_image', 'status', 'seo_title', 
                                       'seo_description', 'keywords']}
        }


def create_sample_markdown() -> str:
    """Create a sample markdown file template"""
    return """---
title: "Your Awesome Blog Post Title"
excerpt: "A compelling excerpt that summarizes your post"
categories:
  - Technology
  - Tutorial
tags:
  - Python
  - WordPress
  - Automation
featured_image: images/featured.jpg
status: draft
seo_title: "SEO Optimized Title | Your Brand"
seo_description: "Meta description for search engines, 150-160 characters recommended"
keywords: python, wordpress, automation, tutorial
focus_keyword: wordpress automation
---

# Your Awesome Blog Post Title

This is the introduction paragraph. It sets the context for your readers.

## Why This Matters

Here's why this topic is important:

- **Point one**: Explanation here
- **Point two**: More details
- **Point three**: Even more insights

## Step-by-Step Guide

### Step 1: Getting Started

![Screenshot of the interface](images/screenshot1.png "Interface Screenshot")

Follow these instructions carefully...

### Step 2: Configuration

```python
# Sample code block
def hello_world():
    print("Hello, WordPress!")
```

## Conclusion

Wrap up your post with key takeaways and a call to action.

![Final result](images/result.png)
"""
