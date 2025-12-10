# WordPress Elementor Blog Automation

A Flask web application that automates WordPress blog post creation from Markdown files with full support for images, SEO metadata, and Elementor page builder.

## Features

✅ **Markdown to WordPress** - Write posts in Markdown with YAML frontmatter  
✅ **Automatic Image Upload** - Upload images to WordPress media library automatically  
✅ **SEO Metadata** - Full support for Yoast SEO and RankMath plugins  
✅ **Featured Images** - Automatically set featured images from frontmatter  
✅ **Categories & Tags** - Auto-create categories and tags if they don't exist  
✅ **Elementor Support** - Optional Elementor page builder compatibility  
✅ **Draft/Publish Control** - Choose post status (draft, publish, pending)  
✅ **Credential Security** - Uses WordPress application passwords (never stored)

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- A WordPress site with REST API enabled (WP 4.7+)
- WordPress application password (create in Users → Profile → Application Passwords)

### 2. Installation

```powershell
# Clone or download this repository
cd elementor_automate

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```powershell
# Make sure venv is activated
flask --app app --debug run
```

Or run directly with Python:

```powershell
python app.py
```

Open your browser to `http://localhost:5000`

## Usage

### Creating a Blog Post

1. **Prepare your markdown file** with YAML frontmatter:

```markdown
---
title: "Your Amazing Blog Post"
excerpt: "A compelling summary"
categories:
  - Technology
  - Tutorial
tags:
  - python
  - wordpress
featured_image: images/hero.jpg
status: draft
seo_title: "SEO Optimized Title | Your Brand"
seo_description: "Meta description for search engines (150-160 chars)"
keywords: wordpress, automation, python
---

# Your Content Here

Write your blog post in markdown...

![Example Image](images/screenshot.png)
```

2. **Navigate to `/upload`** in the web interface

3. **Fill in WordPress credentials:**

   - Site URL (e.g., `https://yourblog.com`)
   - WordPress username
   - Application password

4. **Upload files:**

   - Select your `.md` file
   - Upload any referenced images

5. **Choose options:**

   - Post status (draft/publish/pending)
   - Enable Elementor support (optional)

6. **Submit** and view the result with post URL and uploaded media

### Frontmatter Fields

**Required:**

- `title` - Post title

**Optional:**

- `excerpt` - Post excerpt/summary
- `categories` - Array or comma-separated list
- `tags` - Array or comma-separated list
- `featured_image` - Path to featured image file
- `status` - `draft`, `publish`, or `pending` (default: `draft`)
- `seo_title` - SEO title for Yoast/RankMath
- `seo_description` - Meta description
- `keywords` - Keywords for SEO
- `focus_keyword` - Primary focus keyword

### Example Markdown Files

See `examples/sample-blog-post.md` for a complete example, or download a template from the web interface at `/sample-markdown`.

## Project Structure

```
elementor_automate/
├── app.py                    # Main Flask application
├── wp_client.py              # WordPress REST API client
├── markdown_parser.py        # Markdown parsing with frontmatter
├── requirements.txt          # Python dependencies
├── static/
│   └── styles.css           # Responsive CSS styles
├── templates/
│   ├── index.html           # Homepage
│   ├── upload.html          # Upload form
│   └── result.html          # Upload result page
└── examples/
    └── sample-blog-post.md  # Sample markdown file
```

## API Endpoints

- `GET /` - Homepage with navigation
- `GET /upload` - Upload form
- `POST /upload_post` - Process markdown and images, create WP post
- `POST /check_wp_cred` - Validate WordPress credentials
- `GET /sample-markdown` - Download sample markdown template

## WordPress Setup

### Create Application Password

1. Log into WordPress admin
2. Go to **Users → Profile**
3. Scroll to **Application Passwords**
4. Enter a name (e.g., "Blog Automation")
5. Click **Add New Application Password**
6. Copy the generated password (format: `xxxx xxxx xxxx xxxx`)
7. Use this password in the upload form (NOT your regular password)

### Required WordPress Permissions

The WordPress user must have:

- Permission to create posts
- Permission to upload media
- Permission to create/assign categories and tags

### Compatible Plugins

- ✅ Yoast SEO (SEO metadata automatically populated)
- ✅ RankMath (SEO fields supported)
- ✅ Elementor (optional page builder mode)
- ✅ Classic Editor / Gutenberg (both supported)

## Development

### Running in Debug Mode

```powershell
$Env:FLASK_DEBUG = "1"
flask --app app run
```

Or set `debug=True` in `app.py` when using `python app.py`.

### Installing Additional Dependencies

```powershell
pip install <package-name>
pip freeze > requirements.txt
```

### Code Structure

**`wp_client.py`** - WordPress REST API wrapper

- `validate_credentials()` - Test WordPress authentication
- `upload_media()` - Upload images/files to media library
- `create_post()` - Create post with metadata, SEO, Elementor support
- `get_or_create_category()` - Find or create category
- `get_or_create_tag()` - Find or create tag

**`markdown_parser.py`** - Markdown processing

- Parse YAML frontmatter
- Extract metadata (title, categories, tags, SEO)
- Convert markdown to HTML
- Identify and map image references
- Generate excerpts

**`app.py`** - Flask routes and request handling

- Form rendering
- File upload handling
- Credential validation
- Image upload orchestration
- Post creation workflow

## Troubleshooting

### Import Errors (frontmatter, markdown modules)

Make sure you've installed dependencies and activated the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Authentication Failed

- Use an **application password**, not your regular WordPress password
- Ensure the WordPress user has sufficient permissions
- Check that REST API is enabled (default in WP 4.7+)
- Verify site URL includes `https://` or `http://`

### Image Upload Fails

- Check file extensions (allowed: png, jpg, jpeg, gif, webp, svg)
- Verify file size is under 50MB
- Ensure WordPress media upload limits aren't exceeded
- Check file permissions on WordPress uploads folder

### Categories/Tags Not Created

- Ensure WordPress user has `manage_categories` capability
- Check for typos in category/tag names
- Verify REST API endpoints are accessible

### Post Not Appearing in Elementor

- Check "Enable Elementor support" checkbox in upload form
- Ensure Elementor plugin is installed and activated
- Note: Post will be in basic Elementor structure; further editing in Elementor UI may be needed

## Security Notes

- ✅ Credentials are **never stored** on the server
- ✅ Uses WordPress application passwords (more secure than account passwords)
- ✅ File type validation prevents malicious uploads
- ✅ All requests use HTTPS (when WordPress site uses HTTPS)
- ⚠️ Run this tool locally or on a trusted network
- ⚠️ Don't expose this app to the public internet without additional authentication

## Contributing

Contributions welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## License

MIT License - feel free to use for personal or commercial projects.

## Support

For issues or questions:

1. Check this README and example files
2. Review WordPress REST API documentation
3. Test credentials with the "Test Connection" form
4. Check browser console and Flask logs for error details

## Roadmap

Potential future enhancements:

- [ ] Bulk upload (multiple markdown files at once)
- [ ] Custom post types support
- [ ] ACF (Advanced Custom Fields) integration
- [ ] Scheduled publishing
- [ ] Draft preview before upload
- [ ] Media library browser
- [ ] Category/tag selection from existing WordPress taxonomy
- [ ] Multi-site support

---

**Built with ❤️ for WordPress content creators**
