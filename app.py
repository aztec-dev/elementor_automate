from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import requests 
import logging
from requests.auth import HTTPBasicAuth
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import tempfile
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our custom modules
from wp_client import WordPressClient
from markdown_parser import MarkdownParser, create_sample_markdown
from ai_generator import AIContentGenerator

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Allowed file extensions
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
ALLOWED_MD_EXTENSIONS = {'md', 'markdown'}

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route("/")
def index():
    """Homepage with navigation"""
    logging.warning("")
    return render_template('index.html')


@app.route("/upload")
def upload_form():
    """Display the markdown/image upload form"""
    return render_template('upload.html')


@app.route("/sample-markdown")
def sample_markdown():
    """Download a sample markdown template"""
    sample_content = create_sample_markdown()
    
    return send_file(
        io.BytesIO(sample_content.encode('utf-8')),
        mimetype='text/markdown',
        as_attachment=True,
        download_name='sample-blog-post.md'
    )


@app.route("/generate-ai", methods=["GET", "POST"])
def generate_ai():
    """Generate blog post content using OpenAI and optionally upload to WordPress"""
    if request.method == "GET":
        return render_template('generate_ai.html')
    
    try:
        # Get form data
        prompt = request.form.get('prompt', '').strip()
        tone = request.form.get('tone', 'professional')
        length = request.form.get('length', 'medium')
        categories_input = request.form.get('categories', '').strip()
        tags_input = request.form.get('tags', '').strip()
        include_seo = request.form.get('include_seo') == 'yes'
        download_only = request.form.get('download_only') == 'yes'
        
        # WordPress credentials
        site = request.form.get('site', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('account_password', '').strip()
        post_status = request.form.get('post_status', 'draft')
        use_elementor = request.form.get('use_elementor') == 'yes'
        
        if not prompt:
            flash('Please enter a prompt or topic', 'error')
            return redirect(url_for('generate_ai'))
        
        # Check if OpenAI API key is configured
        if not os.getenv('OPENAI_API_KEY'):
            flash('OpenAI API key not configured. Please set OPENAI_API_KEY in .env file', 'error')
            return redirect(url_for('generate_ai'))
        
        # Generate content with AI
        ai_gen = AIContentGenerator()
        markdown_content = ai_gen.generate_blog_post(
            prompt=prompt,
            tone=tone,
            length=length,
            include_seo=include_seo,
            categories=categories_input,
            tags=tags_input
        )
        
        # If download only, return the markdown file
        if download_only:
            return send_file(
                io.BytesIO(markdown_content.encode('utf-8')),
                mimetype='text/markdown',
                as_attachment=True,
                download_name='ai-generated-post.md'
            )
        
        # Otherwise, upload to WordPress
        if not all([site, username, password]):
            flash('WordPress credentials are required for upload', 'error')
            return redirect(url_for('generate_ai'))
        
        # Ensure site URL has protocol
        if not site.startswith(('http://', 'https://')):
            site = 'https://' + site
        
        # Initialize WordPress client and validate credentials
        wp_client = WordPressClient(site, username, password)
        auth_result = wp_client.validate_credentials()
        
        if not auth_result['success']:
            return render_template('result.html', result={
                'success': False,
                'error': 'WordPress authentication failed',
                'details': auth_result.get('error', 'Invalid credentials')
            })
        
        # Parse the AI-generated markdown
        parser = MarkdownParser(markdown_content=markdown_content)
        metadata = parser.get_all_metadata()
        
        # Convert markdown to HTML
        html_content = parser.to_html()
        
        # Process categories and tags
        category_ids = []
        for cat_name in metadata['categories']:
            cat_id = wp_client.get_or_create_category(cat_name)
            if cat_id:
                category_ids.append(cat_id)
        
        tag_ids = []
        for tag_name in metadata['tags']:
            tag_id = wp_client.get_or_create_tag(tag_name)
            if tag_id:
                tag_ids.append(tag_id)
        
        # Prepare SEO meta fields
        seo_meta = metadata['seo']
        post_meta = {}
        
        if seo_meta.get('title'):
            post_meta['_yoast_wpseo_title'] = seo_meta['title']
        if seo_meta.get('description'):
            post_meta['_yoast_wpseo_metadesc'] = seo_meta['description']
        if seo_meta.get('keywords'):
            post_meta['_yoast_wpseo_focuskw'] = seo_meta.get('focus_keyword', seo_meta['keywords'])
        
        # Prepare Elementor data (if enabled)
        import json
        elementor_data = None
        if use_elementor:
            elementor_data = [
                {
                    "id": "content",
                    "elType": "section",
                    "elements": [
                        {
                            "id": "column",
                            "elType": "column",
                            "elements": [
                                {
                                    "id": "text",
                                    "elType": "widget",
                                    "widgetType": "text-editor",
                                    "settings": {
                                        "editor": html_content
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        
        # Create the WordPress post
        post_result = wp_client.create_post(
            title=metadata['title'],
            content=html_content,
            status=post_status,
            categories=category_ids if category_ids else None,
            tags=tag_ids if tag_ids else None,
            excerpt=metadata.get('excerpt'),
            meta=post_meta if post_meta else None,
            elementor_data=elementor_data
        )
        
        if post_result['success']:
            return render_template('result.html', result={
                'success': True,
                'title': post_result['title'],
                'status': post_result['status'],
                'post_id': post_result['id'],
                'post_url': post_result['url'],
                'uploaded_images': [],
                'ai_generated': True
            })
        else:
            return render_template('result.html', result={
                'success': False,
                'error': 'Failed to create post',
                'details': post_result.get('error', 'Unknown error')
            })
    
    except Exception as e:
        logging.exception("Error generating AI content")
        return render_template('result.html', result={
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        })


@app.route("/check_wp_cred", methods=["POST"])
def check_wp_cred():
    """
    Validate WordPress credentials and display basic info
    (Original endpoint - preserved for backward compatibility)
    """
    site = request.form['site']
    username = request.form['username']
    account_password = request.form['account_password']

    endpoint = f"{site}/wp-json/wp/v2/posts?_embed"

    response = requests.get(
        endpoint,
        auth=HTTPBasicAuth(username, account_password)
    )
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({
            "status": response.reason,
            "code": response.status_code
        }), response.status_code


@app.route("/upload_post", methods=["POST"])
def upload_post():
    """
    Main endpoint: Upload markdown file and images to WordPress
    Steps:
    1. Validate credentials
    2. Parse markdown file
    3. Upload all images to WP media library
    4. Replace image references in markdown
    5. Convert markdown to HTML
    6. Create WordPress post with metadata, SEO, and optional Elementor support
    """
    try:
        # 1. Get form data
        site = request.form.get('site', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('account_password', '').strip()
        post_status = request.form.get('post_status', 'draft')
        use_elementor = request.form.get('use_elementor') == 'yes'
        
        if not all([site, username, password]):
            return render_template('result.html', result={
                'success': False,
                'error': 'WordPress credentials are required'
            })
        
        # Ensure site URL has protocol
        if not site.startswith(('http://', 'https://')):
            site = 'https://' + site
        
        # 2. Validate markdown file
        if 'markdown_file' not in request.files:
            return render_template('result.html', result={
                'success': False,
                'error': 'No markdown file uploaded'
            })
        
        md_file = request.files['markdown_file']
        if md_file.filename == '':
            return render_template('result.html', result={
                'success': False,
                'error': 'No markdown file selected'
            })
        
        if not allowed_file(md_file.filename, ALLOWED_MD_EXTENSIONS):
            return render_template('result.html', result={
                'success': False,
                'error': 'Invalid file type. Please upload a .md or .markdown file'
            })
        
        # 3. Initialize WordPress client and validate credentials
        wp_client = WordPressClient(site, username, password)
        auth_result = wp_client.validate_credentials()
        
        if not auth_result['success']:
            return render_template('result.html', result={
                'success': False,
                'error': 'WordPress authentication failed',
                'details': auth_result.get('error', 'Invalid credentials')
            })
        
        # 4. Parse markdown file
        md_content = md_file.read().decode('utf-8')
        parser = MarkdownParser(markdown_content=md_content)
        metadata = parser.get_all_metadata()
        
        # 5. Handle image uploads
        uploaded_images = []
        image_map = {}  # Map local paths to WP URLs
        
        # Get uploaded image files
        image_files = request.files.getlist('images')
        
        # Also check for featured image in markdown metadata
        featured_image_id = None
        featured_image_path = parser.get_featured_image()
        
        # Upload all images
        for img_file in image_files:
            if img_file.filename == '':
                continue
            
            if not allowed_file(img_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                logging.warning(f"Skipping invalid image file: {img_file.filename}")
                continue
            
            # Determine alt text from filename or markdown references
            filename = secure_filename(img_file.filename)
            alt_text = filename.rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ')
            
            # Upload to WordPress
            upload_result = wp_client.upload_media(
                file_obj=img_file.stream,
                filename=filename,
                alt_text=alt_text
            )
            
            if upload_result['success']:
                uploaded_images.append({
                    'filename': filename,
                    'id': upload_result['id'],
                    'url': upload_result['url']
                })
                
                # Map various possible references to this image
                image_map[filename] = upload_result['url']
                image_map[f"images/{filename}"] = upload_result['url']
                image_map[f"./images/{filename}"] = upload_result['url']
                
                # Check if this is the featured image
                if featured_image_path and filename in featured_image_path:
                    featured_image_id = upload_result['id']
            else:
                logging.error(f"Failed to upload {filename}: {upload_result.get('error')}")
        
        # 6. Replace image references in content
        if image_map:
            updated_content = parser.replace_image_references(image_map)
            parser.content = updated_content
        
        # 7. Convert markdown to HTML
        html_content = parser.to_html()
        
        # 8. Process categories and tags
        category_ids = []
        for cat_name in metadata['categories']:
            cat_id = wp_client.get_or_create_category(cat_name)
            if cat_id:
                category_ids.append(cat_id)
        
        tag_ids = []
        for tag_name in metadata['tags']:
            tag_id = wp_client.get_or_create_tag(tag_name)
            if tag_id:
                tag_ids.append(tag_id)
        
        # 9. Prepare SEO meta fields (for Yoast/RankMath)
        seo_meta = metadata['seo']
        post_meta = {}
        
        if seo_meta.get('title'):
            post_meta['_yoast_wpseo_title'] = seo_meta['title']
        if seo_meta.get('description'):
            post_meta['_yoast_wpseo_metadesc'] = seo_meta['description']
        if seo_meta.get('keywords'):
            post_meta['_yoast_wpseo_focuskw'] = seo_meta.get('focus_keyword', seo_meta['keywords'])
        
        # 10. Prepare Elementor data (if enabled)
        elementor_data = None
        if use_elementor:
            # Basic Elementor structure - user can edit in Elementor afterward
            elementor_data = [
                {
                    "id": "content",
                    "elType": "section",
                    "elements": [
                        {
                            "id": "column",
                            "elType": "column",
                            "elements": [
                                {
                                    "id": "text",
                                    "elType": "widget",
                                    "widgetType": "text-editor",
                                    "settings": {
                                        "editor": html_content
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        
        # 11. Create the WordPress post
        post_result = wp_client.create_post(
            title=metadata['title'],
            content=html_content,
            status=post_status,
            featured_media=featured_image_id,
            categories=category_ids if category_ids else None,
            tags=tag_ids if tag_ids else None,
            excerpt=metadata.get('excerpt'),
            meta=post_meta if post_meta else None,
            elementor_data=elementor_data
        )
        
        if post_result['success']:
            return render_template('result.html', result={
                'success': True,
                'title': post_result['title'],
                'status': post_result['status'],
                'post_id': post_result['id'],
                'post_url': post_result['url'],
                'uploaded_images': uploaded_images
            })
        else:
            return render_template('result.html', result={
                'success': False,
                'error': 'Failed to create post',
                'details': post_result.get('error', 'Unknown error')
            })
    
    except Exception as e:
        logging.exception("Error during upload")
        return render_template('result.html', result={
            'success': False,
            'error': 'An unexpected error occurred',
            'details': str(e)
        })


if __name__ == "__main__":
    app.run(debug=True)