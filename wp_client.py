"""
WordPress REST API Client
Handles authentication, media uploads, and post creation with SEO/Elementor support
"""
import requests
from requests.auth import HTTPBasicAuth
import mimetypes
import os
import json
from typing import Dict, List, Optional, BinaryIO


class WordPressClient:
    """Client for interacting with WordPress REST API"""
    
    def __init__(self, site_url: str, username: str, password: str):
        """
        Initialize WordPress client
        
        Args:
            site_url: WordPress site URL (e.g., 'https://example.com')
            username: WordPress admin username
            password: WordPress application password
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)
        
    def validate_credentials(self) -> Dict:
        """
        Validate WordPress credentials by fetching current user info
        
        Returns:
            dict with status and user info or error message
        """
        endpoint = f"{self.site_url}/wp-json/wp/v2/users/me"
        try:
            response = requests.get(endpoint, auth=self.auth, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'success': True,
                    'user': user_data.get('name'),
                    'id': user_data.get('id')
                }
            else:
                return {
                    'success': False,
                    'error': f"Authentication failed: {response.status_code} - {response.reason}"
                }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Connection error: {str(e)}"
            }
    
    def upload_media(self, file_path: str = None, file_obj: BinaryIO = None, 
                     filename: str = None, alt_text: str = "") -> Dict:
        """
        Upload an image/media file to WordPress media library
        
        Args:
            file_path: Path to file on disk (optional if file_obj provided)
            file_obj: File-like object (optional if file_path provided)
            filename: Filename to use (required if using file_obj)
            alt_text: Alt text for accessibility
            
        Returns:
            dict with media ID, URL, and metadata or error
        """
        endpoint = f"{self.site_url}/wp-json/wp/v2/media"
        
        # Determine file source
        if file_path:
            if not os.path.exists(file_path):
                return {'success': False, 'error': f'File not found: {file_path}'}
            filename = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                file_data = f.read()
        elif file_obj:
            if not filename:
                return {'success': False, 'error': 'filename required when using file_obj'}
            file_data = file_obj.read()
        else:
            return {'success': False, 'error': 'Either file_path or file_obj must be provided'}
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = 'application/octet-stream'
        
        headers = {
            'Content-Type': mime_type,
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=file_data,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 201:
                media_data = response.json()
                
                # Update alt text if provided
                if alt_text:
                    self._update_media_alt_text(media_data['id'], alt_text)
                
                return {
                    'success': True,
                    'id': media_data['id'],
                    'url': media_data['source_url'],
                    'title': media_data['title']['rendered'],
                    'mime_type': media_data['mime_type']
                }
            else:
                return {
                    'success': False,
                    'error': f"Upload failed: {response.status_code} - {response.text}"
                }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Upload error: {str(e)}"
            }
    
    def _update_media_alt_text(self, media_id: int, alt_text: str) -> bool:
        """Update alt text for a media item"""
        endpoint = f"{self.site_url}/wp-json/wp/v2/media/{media_id}"
        try:
            response = requests.post(
                endpoint,
                json={'alt_text': alt_text},
                auth=self.auth,
                timeout=10
            )
            return response.status_code == 200
        except:
            return False
    
    def create_post(self, title: str, content: str, 
                   status: str = 'draft',
                   featured_media: Optional[int] = None,
                   categories: Optional[List[int]] = None,
                   tags: Optional[List[int]] = None,
                   excerpt: Optional[str] = None,
                   meta: Optional[Dict] = None,
                   elementor_data: Optional[List] = None) -> Dict:
        """
        Create a WordPress post with full metadata support
        
        Args:
            title: Post title
            content: Post HTML content
            status: 'draft', 'publish', 'pending', etc.
            featured_media: Media ID for featured image
            categories: List of category IDs
            tags: List of tag IDs
            excerpt: Post excerpt/summary
            meta: Custom meta fields (for SEO plugins like Yoast)
            elementor_data: Elementor page builder JSON data
            
        Returns:
            dict with post ID, URL, and status or error
        """
        endpoint = f"{self.site_url}/wp-json/wp/v2/posts"
        
        post_data = {
            'title': title,
            'content': content,
            'status': status
        }
        
        # Optional fields
        if featured_media:
            post_data['featured_media'] = featured_media
        if categories:
            post_data['categories'] = categories
        if tags:
            post_data['tags'] = tags
        if excerpt:
            post_data['excerpt'] = excerpt
        
        # Meta fields (SEO, custom fields, Elementor)
        if meta or elementor_data:
            post_data['meta'] = meta or {}
            
            # Add Elementor data if provided (must be JSON string)
            if elementor_data:
                post_data['meta']['_elementor_data'] = json.dumps(elementor_data)
                post_data['meta']['_elementor_edit_mode'] = 'builder'
                post_data['meta']['_elementor_template_type'] = 'wp-post'
        
        try:
            response = requests.post(
                endpoint,
                json=post_data,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 201:
                post_response = response.json()
                return {
                    'success': True,
                    'id': post_response['id'],
                    'url': post_response['link'],
                    'status': post_response['status'],
                    'title': post_response['title']['rendered']
                }
            else:
                return {
                    'success': False,
                    'error': f"Post creation failed: {response.status_code} - {response.text}"
                }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Post creation error: {str(e)}"
            }
    
    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """
        Get category ID by name, or create if doesn't exist
        
        Args:
            category_name: Category name
            
        Returns:
            Category ID or None if error
        """
        # Search for existing category
        search_endpoint = f"{self.site_url}/wp-json/wp/v2/categories?search={category_name}"
        try:
            response = requests.get(search_endpoint, auth=self.auth, timeout=10)
            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat['name'].lower() == category_name.lower():
                        return cat['id']
            
            # Create new category
            create_endpoint = f"{self.site_url}/wp-json/wp/v2/categories"
            response = requests.post(
                create_endpoint,
                json={'name': category_name},
                auth=self.auth,
                timeout=10
            )
            if response.status_code == 201:
                return response.json()['id']
        except:
            pass
        return None
    
    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """
        Get tag ID by name, or create if doesn't exist
        
        Args:
            tag_name: Tag name
            
        Returns:
            Tag ID or None if error
        """
        # Search for existing tag
        search_endpoint = f"{self.site_url}/wp-json/wp/v2/tags?search={tag_name}"
        try:
            response = requests.get(search_endpoint, auth=self.auth, timeout=10)
            if response.status_code == 200:
                tags = response.json()
                for tag in tags:
                    if tag['name'].lower() == tag_name.lower():
                        return tag['id']
            
            # Create new tag
            create_endpoint = f"{self.site_url}/wp-json/wp/v2/tags"
            response = requests.post(
                create_endpoint,
                json={'name': tag_name},
                auth=self.auth,
                timeout=10
            )
            if response.status_code == 201:
                return response.json()['id']
        except:
            pass
        return None
