# AI Content Generation Setup

## Quick Setup (3 Steps)

### 1. Install Dependencies

```powershell
.\venv\Scripts\python.exe -m pip install openai python-dotenv
```

### 2. Get Your OpenAI API Key

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. **Save it somewhere safe** - you won't see it again!

### 3. Configure the App

Create a `.env` file in the project root:

```powershell
# Copy the example file
copy .env.example .env

# Edit .env with your text editor and add your API key
notepad .env
```

Add your API key to `.env`:

```
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
FLASK_SECRET_KEY=your-random-secret-key
```

**Generate a secret key:**

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Restart Flask

Stop the Flask server (Ctrl+C) and restart it:

```powershell
python app.py
```

## Using AI Content Generation

1. Navigate to `http://localhost:5000/generate-ai`
2. Enter your topic/prompt (be specific!)
3. Choose tone (professional, casual, technical, friendly)
4. Select length (short ~500 words, medium ~1000 words, long ~2000 words)
5. Optionally add categories and tags
6. Click "Generate Blog Post"
7. The markdown file will download
8. Upload it to WordPress using the `/upload` form!

## Example Prompts

**Good prompts (specific):**

- "Write a comprehensive beginner's guide to setting up a WordPress blog, including choosing hosting, installing WordPress, selecting a theme, and essential plugins to install"
- "Create a technical tutorial on implementing REST API authentication in Python using JWT tokens, with code examples and security best practices"
- "Write a friendly, casual blog post about 10 productivity tips for remote workers, with personal anecdotes and actionable advice"

**Bad prompts (too vague):**

- "Write about WordPress"
- "Blog post about technology"
- "Something interesting"

## Tips for Best Results

### Be Specific in Your Prompt

Include:

- Target audience (beginners, developers, business owners)
- Key points to cover
- Desired structure or format
- Examples or case studies you want included

### Tone Matters

- **Professional** - Business blogs, corporate content
- **Casual** - Personal blogs, lifestyle content
- **Technical** - Developer blogs, tutorials, documentation
- **Friendly** - Community content, advice, tips

### Post Length

- **Short (~500 words)** - Quick tips, announcements, simple how-tos
- **Medium (~1000 words)** - Standard blog posts, guides
- **Long (~2000 words)** - Comprehensive guides, in-depth tutorials

### SEO Metadata

Enabling SEO metadata includes:

- Optimized title (50-60 chars)
- Meta description (150-160 chars)
- Focus keyword
- Related keywords

## Cost Estimate

Using `gpt-4o-mini` (default):

- Short post (~500 words): $0.01 - $0.02
- Medium post (~1000 words): $0.02 - $0.04
- Long post (~2000 words): $0.04 - $0.08

Using `gpt-4o`:

- Costs ~10x more but higher quality
- Change model in `.env`: `OPENAI_MODEL=gpt-4o`

Check current pricing: [https://openai.com/pricing](https://openai.com/pricing)

## Workflow

### Option 1: AI → Upload

1. Generate content with AI (`/generate-ai`)
2. Download markdown file
3. Upload to WordPress (`/upload`)

### Option 2: AI → Edit → Upload

1. Generate content with AI
2. Edit the markdown file in your favorite editor
3. Add images if needed
4. Upload to WordPress

### Option 3: Manual → AI Enhance

1. Write your own draft in markdown
2. Use AI to enhance specific sections (future feature)
3. Upload to WordPress

## Troubleshooting

### "OpenAI API key not configured"

- Make sure `.env` file exists in project root
- Check that `OPENAI_API_KEY=sk-...` is in the file
- Restart Flask after creating/editing `.env`

### "Rate limit exceeded"

- You've hit OpenAI's rate limit
- Wait a minute and try again
- Upgrade your OpenAI plan for higher limits

### "Insufficient quota"

- Your OpenAI account needs credits
- Add payment method at [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)

### Generated content is too short/long

- Adjust the length setting
- Be more specific in your prompt about desired length
- Regenerate if needed

### Content doesn't match my topic

- Make your prompt more specific
- Include examples of what you want
- Mention specific points to cover

## Security Notes

- ✅ **Never commit `.env` to Git** (already in `.gitignore`)
- ✅ **Never share your API key publicly**
- ✅ Store `.env` securely
- ✅ Rotate API keys periodically
- ✅ Use environment-specific keys (dev vs production)

## Advanced Usage

### Custom Models

Edit `.env` to change the AI model:

```
# Faster and cheaper
OPENAI_MODEL=gpt-4o-mini

# Higher quality
OPENAI_MODEL=gpt-4o

# Legacy (not recommended)
OPENAI_MODEL=gpt-3.5-turbo
```

### Environment Variables

Available settings in `.env`:

```
# Required
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL=gpt-4o-mini
FLASK_SECRET_KEY=your-secret-key
FLASK_DEBUG=1
```

## Next Steps

After generating content:

1. Review and edit the markdown if needed
2. Add your own images to the `images/` folder
3. Reference images in markdown: `![Alt text](images/photo.jpg)`
4. Upload everything to WordPress via `/upload`
5. Publish or save as draft

---

**Happy AI-powered blogging!** 🚀🤖
