# Playwright Course Downloader - Quick Start

Automate downloading entire courses from login-protected educational platforms.

## Quick Start

### 1. Install Dependencies

```bash
uv pip install playwright
uv run playwright install
```

### 2. First-Time Setup (Authentication)

```bash
# Open browser for manual login
uv run python .claude/skills/playwright-downloading-courses/scripts/bluedot_interactive.py
```

This will:
1. Open a browser window
2. Navigate to the course login page
3. Wait for you to log in
4. Automatically save your session when login is detected

### 3. Download Course

```bash
# Download all lessons
uv run python .claude/skills/playwright-downloading-courses/scripts/bluedot_full_scraper.py
```

### 4. Process Resources

```bash
# Extract and filter links
uv run python .claude/skills/playwright-downloading-courses/scripts/extract_links_from_json.py
uv run python .claude/skills/playwright-downloading-courses/scripts/filter_relevant_links.py

# Download high-value resources (arXiv papers, etc.)
uv run python .claude/skills/playwright-downloading-courses/scripts/download_high_value_resources.py
```

## What Gets Downloaded

- ✅ All course lesson pages as PDFs
- ✅ YouTube video transcripts (JSON + Markdown)
- ✅ arXiv research papers
- ✅ External links catalog
- ✅ Filtered high-value resources
- ✅ Comprehensive documentation

## Output Location

```
downloads/[course_name]/
├── pdfs/                 # All lesson PDFs
├── transcripts/          # YouTube transcripts
├── downloaded_resources/ # arXiv papers, articles
├── extracted_links/      # Link analysis
└── COMPLETE_DOWNLOAD_SUMMARY.md
```

## Adapting for Other Platforms

To use with a different educational platform:

1. **Edit course URL** in `bluedot_full_scraper.py`:
   ```python
   course_slug = "your-course-name"
   base_url = "https://your-platform.com"
   ```

2. **Update lesson URL pattern**:
   ```python
   url = f"{base_url}/courses/{course_slug}/{unit_num}/{lesson_num}"
   ```

3. **Adjust authentication flow** in `bluedot_interactive.py` if needed

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `bluedot_browser.py` | Core browser automation class |
| `bluedot_interactive.py` | Interactive login helper |
| `bluedot_full_scraper.py` | Main course downloader |
| `extract_links_from_json.py` | Extract & categorize links |
| `filter_relevant_links.py` | Filter high-value resources |
| `download_high_value_resources.py` | Download arXiv papers, articles |
| `extract_pdf_text.py` | Verify PDF content quality |

## Example Output

```
📂 Analyzing course...
✅ Found 22 lessons across 6 units
📥 Downloading lesson PDFs... [22/22]
📹 Found 5 YouTube videos
📥 Downloading transcripts... [5/5]
🔗 Extracted 206 external links
✨ Filtered to 66 high-value resources
📥 Downloading arXiv papers... [7/7]

✅ Complete! See: downloads/bluedot_technical_ai_safety_complete/
```

## Troubleshooting

**"Browser not found"**
```bash
uv run playwright install
```

**"Authentication failed"**
- Re-run `bluedot_interactive.py`
- Check if login URL changed
- Verify credentials

**"No text in PDFs"**
- This is normal for some web-to-PDF conversions
- Use the extracted JSON data instead
- Text extraction script can verify content

## See Also

- Full documentation: `SKILL.md`
- Browser automation guide: `plans/browser-automation-login-sites.md`
- Related skills: `youtube-fetching-transcripts`, `download-url`
