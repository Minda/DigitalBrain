# Playwright Downloading Courses

Download entire online courses from login-protected educational platforms using Playwright browser automation.

## What This Skill Does

This skill automates downloading complete courses from educational platforms that require authentication:

1. **Browser Automation** - Uses Playwright to interact with websites like a real user
2. **Session Persistence** - Login once, reuse session for future downloads
3. **Complete Course Scraping** - Downloads all lessons, extracting PDFs, links, and videos
4. **Resource Organization** - Organizes content with lesson prefixes (e.g., U2L3_article.pdf)
5. **Link Extraction & Filtering** - Identifies and categorizes external resources
6. **Selective Downloading** - Downloads high-value resources (arXiv papers, articles, etc.)

## When to Use This Skill

Use this skill when the user wants to:
- Download an entire online course from a login-protected platform
- Archive educational content for offline study
- Extract and organize external resources from course materials
- Create a comprehensive offline version of a course

**Trigger phrases:**
- "download this entire course"
- "scrape [website] course"
- "get all lessons from [course URL]"
- "archive this educational content"
- "download course with external resources"

## How It Works

### Phase 1: Authentication Setup
1. User provides course URL
2. Open browser in non-headless mode for manual login
3. User logs in via OAuth/SSO/email
4. Save authentication state to `.auth/[site]_state.json`
5. Future runs reuse saved session (no re-login needed)

### Phase 2: Course Structure Discovery
1. Navigate through course to discover all units and lessons
2. Build complete lesson list (unit/lesson structure)
3. Save course structure to JSON

### Phase 3: Content Download
1. Visit each lesson page
2. Save page as PDF
3. Extract all links and YouTube video IDs
4. Download YouTube transcripts
5. Save structured data (JSON + Markdown)

### Phase 4: Resource Processing
1. Extract and categorize all external links
2. Filter out navigation/platform links
3. Identify high-value resources (papers, articles, code)
4. Download arXiv papers with lesson prefixes
5. Generate comprehensive documentation

## Usage

### Interactive Mode (Initial Setup)

When Claude needs to download a course for the first time:

```bash
# 1. Create browser automation instance
uv run python .claude/skills/playwright-downloading-courses/scripts/bluedot_interactive.py

# This opens a browser window where the user can:
# - Navigate to the login page
# - Log in with their credentials
# - The script detects successful login and saves the session
```

### Automated Mode (After Login)

Once authenticated, Claude can run the full scraper:

```bash
# 2. Download entire course
uv run python .claude/skills/playwright-downloading-courses/scripts/bluedot_full_scraper.py
```

This will:
- Use saved authentication
- Download all accessible lessons as PDFs
- Extract all links and YouTube videos
- Download video transcripts
- Generate comprehensive indices

### Resource Extraction & Download

```bash
# 3. Extract external links
uv run python .claude/skills/playwright-downloading-courses/scripts/extract_links_from_json.py

# 4. Filter to high-value resources
uv run python .claude/skills/playwright-downloading-courses/scripts/filter_relevant_links.py

# 5. Download high-value resources (arXiv papers, articles)
uv run python .claude/skills/playwright-downloading-courses/scripts/download_high_value_resources.py
```

### PDF Analysis

```bash
# 6. Verify PDF content quality
uv run python .claude/skills/playwright-downloading-courses/scripts/extract_pdf_text.py
```

## Output Structure

```
downloads/[course_name]/
├── pdfs/                          # Course lesson PDFs
│   ├── unit1_lesson1.pdf
│   ├── unit2_lesson3.pdf
│   └── ...
├── transcripts/                   # YouTube video transcripts
│   ├── [video_id].json           # Full transcript with timestamps
│   ├── [video_id].md             # Text-only version
│   └── README.md
├── extracted_links/               # Link analysis
│   ├── all_external_links.json
│   ├── all_external_links_detailed.md
│   ├── filtered_course_resources.json
│   └── filtered_course_resources.md
├── downloaded_resources/          # High-value resources
│   ├── arxiv_papers/
│   │   ├── U2L3_arxiv_2212.08073.pdf
│   │   └── U3L1_arxiv_2410.21939.pdf
│   ├── articles/
│   ├── github_repos/
│   └── UNITS_1-5_MANIFEST.md
├── pdf_analysis/                  # PDF content verification
│   └── pdf_text_analysis.json
├── COURSE_INDEX.md               # Master course index
├── COMPLETE_DOWNLOAD_SUMMARY.md  # Full documentation
├── complete_course_data.json     # Structured data
└── unit_*.md                     # Per-unit indices
```

## Key Scripts

### `bluedot_browser.py`
Core browser automation class with:
- Session persistence
- Anti-detection settings
- Page navigation and PDF export
- Content extraction methods

### `bluedot_interactive.py`
Interactive login helper:
- Opens browser for manual login
- Polls URL to detect successful authentication
- Saves session state

### `bluedot_full_scraper.py`
Complete course scraper:
- Downloads all lesson pages as PDFs
- Extracts links and YouTube videos
- Downloads transcripts
- Generates comprehensive documentation

### `extract_links_from_json.py`
Link extraction and categorization:
- Parses course JSON data
- Categorizes links by type (arXiv, GitHub, articles, etc.)
- Groups by lesson and unit

### `filter_relevant_links.py`
Filters out irrelevant content:
- Removes navigation/platform links
- Identifies high-value resources
- Creates filtered resource lists

### `download_high_value_resources.py`
Downloads filtered resources:
- arXiv papers (direct PDF download)
- Articles (using download-url skill)
- GitHub repositories (clone)
- Adds lesson prefixes to all files

### `extract_pdf_text.py`
PDF content verification:
- Extracts text from PDFs
- Analyzes keyword presence
- Identifies low-quality PDFs

## Requirements

- **Playwright**: `uv pip install playwright`
- **Browser binaries**: `uv run playwright install`
- **Python packages**: AsyncIO, pathlib, json, subprocess

## Technical Details

### Anti-Detection
- Disables automation flags: `--disable-blink-features=AutomationControlled`
- Uses persistent browser context
- Respects rate limiting with delays

### Session Persistence
Authentication state is saved to `.auth/[site]_state.json`:
```json
{
  "cookies": [...],
  "localStorage": [...],
  "sessionStorage": [...]
}
```

### Error Handling
- Timeouts: Configurable per operation (30-180s)
- Retries: Not implemented (manual retry recommended)
- Failed lessons: Logged but don't block full scrape

## Adaptation for Other Platforms

This skill was built for Bluedot Impact but can be adapted for other platforms:

1. **Change base URL** in scraper scripts
2. **Update lesson URL pattern** (currently `/courses/{course}/{unit}/{lesson}`)
3. **Adjust selectors** for content extraction
4. **Modify authentication flow** if needed
5. **Update file naming convention**

## Limitations

- Requires manual login for initial authentication
- Cannot bypass strong anti-bot protections (Cloudflare, etc.)
- Download speed limited by rate limiting
- Some PDFs may not have extractable text
- Article downloads depend on download-url skill

## Example Session

```
User: "Can you download the entire Bluedot Technical AI Safety course?"

Claude:
1. First, I'll set up authentication. Running the interactive login script...
2. [Opens browser] Please log in to Bluedot Impact.
3. [User logs in via Google OAuth]
4. ✅ Login detected! Session saved.
5. Now downloading all course content...
6. [Downloads 22 lessons, 5 YouTube transcripts, extracts 206 links]
7. Filtering to high-value resources (66 identified)...
8. Downloading arXiv papers and articles...
9. ✅ Complete! Downloaded:
   - 22 lesson PDFs
   - 5 video transcripts
   - 7 arXiv papers
   - Complete link index

All content saved to: downloads/bluedot_technical_ai_safety_complete/
```

## Future Enhancements

- [ ] Parallel lesson downloads
- [ ] Automatic retry on failure
- [ ] Progress bar for long downloads
- [ ] OCR for non-text PDFs
- [ ] Better article download reliability
- [ ] Support for more video platforms
- [ ] Cookie-based authentication
- [ ] Headless authentication flow (for some sites)

## Related Skills

- **youtube-fetching-transcripts** - Downloads YouTube transcripts
- **download-url** - Downloads web articles as PDFs
- **downloading-articles** - Alternative article download method

## Notes

- Always respect platform terms of service
- Use downloaded content for personal educational purposes only
- Rate limit requests to avoid overwhelming servers
- Some content may require additional authentication or subscription
