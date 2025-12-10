# Quick Start Guide

## Installation & Setup (5 minutes)

### 1. Install Dependencies

```powershell
# Activate your virtual environment if not already active
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 2. Run the Application

```powershell
# Option 1: Using Flask CLI (recommended for development)
flask --app app --debug run

# Option 2: Direct Python execution
python app.py
```

The app will start on `http://localhost:5000`

### 3. Create WordPress Application Password

**IMPORTANT:** You need an application password, NOT your regular WordPress password.

1. Log into your WordPress admin panel
2. Navigate to: **Users → Profile** (or **Users → Your Profile**)
3. Scroll down to **Application Passwords** section
4. Enter a name like "Blog Automation Tool"
5. Click **Add New Application Password**
6. Copy the generated password (format: `xxxx xxxx xxxx xxxx xxxx`)
7. **Save it** - you won't see it again!

### 4. Upload Your First Post

1. Open `http://localhost:5000/upload` in your browser
2. Fill in WordPress credentials:
   - **Site URL**: `https://yourblog.com` (include https://)
   - **Username**: Your WordPress username
   - **Password**: The application password from step 3
3. Upload a markdown file (or download the sample from the page)
4. Optionally upload images referenced in the markdown
5. Choose post status (Draft recommended for first try)
6. Click **Upload to WordPress**
7. View the result page with your post URL!

## Sample Markdown File

See `examples/sample-blog-post.md` for a complete example, or click "Download Sample Markdown" on the homepage.

Minimum required frontmatter:

```yaml
---
title: "My First Automated Post"
---
# Content goes here

This is my first automated WordPress post!
```

Full-featured frontmatter:

```yaml
---
title: "Complete Guide to WordPress Automation"
excerpt: "Learn how to automate your WordPress blog"
categories:
  - Tutorial
  - Technology
tags:
  - wordpress
  - automation
  - python
featured_image: images/hero.jpg
status: draft
seo_title: "WordPress Automation Guide | YourBrand"
seo_description: "Complete guide to automating WordPress with Python and REST API"
keywords: wordpress automation, python, blogging
---
```

## Troubleshooting

### "Authentication failed"

- ✅ Use **application password**, not your regular WordPress password
- ✅ Ensure site URL includes `https://` or `http://`
- ✅ Check that the WordPress user has permission to create posts

### "Module not found" errors

- ✅ Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- ✅ Install dependencies: `pip install -r requirements.txt`

### Images not uploading

- ✅ Check file extensions (jpg, png, gif, webp allowed)
- ✅ Ensure filenames match references in markdown
- ✅ File size must be under 50MB

### Categories/tags not created

- ✅ Ensure WordPress user has permission to manage categories
- ✅ Check spelling in frontmatter

## Tips

💡 **Start with drafts** - Set `status: draft` and review in WordPress before publishing

💡 **Test credentials first** - Use the "Test Connection" form on the homepage

💡 **Use descriptive image filenames** - They become alt text automatically

💡 **Compress images** - Use tools like TinyPNG before uploading

💡 **Version control** - Keep your markdown files in Git for history

## Next Steps

- Try the example markdown file
- Explore Elementor support
- Add SEO metadata to optimize your posts
- Bulk create posts by repeating the upload process

## Support

For detailed documentation, see `README.md`

For issues, check:

1. Browser console (F12) for client errors
2. Terminal/Flask output for server errors
3. WordPress admin → Posts to verify post creation

---

Happy automating! 🚀
