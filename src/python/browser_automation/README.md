# Browser Automation for Bluedot AI Safety Course

This directory contains browser automation tools for accessing and interacting with the Bluedot AI Safety course at https://bluedot.org/courses/technical-ai-safety/1/1.

## Setup

1. Install Playwright:
```bash
uv pip install playwright
uv run playwright install
```

2. The browser installation might take a few minutes as it downloads Chrome, Firefox, and WebKit binaries.

## Files

- **`bluedot_browser.py`** - Main automation class with full authentication and navigation features
- **`test_bluedot.py`** - Simple test script to verify setup and basic navigation
- **`.auth/`** - Directory for storing authentication state (gitignored)

## Usage

### First-time Setup (Manual Login)

Run the main script to set up authentication:

```bash
uv run python src/python/browser_automation/bluedot_browser.py
```

The script will:
1. Open a browser window
2. Navigate to the Bluedot course site
3. If not logged in, redirect to the login page
4. Wait for you to manually log in
5. Save your authentication state for future use

### Test Basic Access

To test if Playwright is working correctly:

```bash
uv run python src/python/browser_automation/test_bluedot.py
```

This will:
- Open the Bluedot site
- Check if login is required
- Take screenshots
- Display page information

### Using the BluedotBrowser Class

```python
from bluedot_browser import BluedotBrowser

async def main():
    async with BluedotBrowser(headless=False) as browser:
        # Check authentication
        if not await browser.is_authenticated():
            await browser.manual_login()

        # Navigate to course
        success = await browser.navigate_to_course()

        # Extract content
        if success:
            content = await browser.extract_course_content()
            print(content)
```

## Features

### Authentication Management
- **Session Persistence**: Saves authentication state to `.auth/bluedot_state.json`
- **Auto-restore**: Automatically loads saved session on subsequent runs
- **Manual Login Support**: Guided process for initial authentication

### Anti-Detection Features
- Custom user agent strings
- Disabled automation indicators
- Stealth JavaScript injections
- Realistic viewport settings

### Content Extraction
- Course title and content detection
- Video/iframe identification
- Navigation menu extraction
- Full page screenshots

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit `.auth/` directory** - Contains sensitive session data
2. **Use dedicated test accounts** when possible
3. **Respect rate limits** - Add delays between requests
4. **Follow Terms of Service** - Only automate permitted actions

## Troubleshooting

### "Playwright browsers not found"
Run: `uv run playwright install`

### "Browser detected as automated"
- Use headful mode (headless=False)
- Ensure stealth settings are applied
- Add human-like delays between actions

### Session expired
- Delete `.auth/bluedot_state.json`
- Run manual login again

### Page elements not found
- Check if selectors have changed
- Increase wait timeouts
- Verify you're on the correct page

## Advanced Usage

### Custom Navigation

```python
# Navigate to specific lesson
await browser.page.goto("https://bluedot.org/courses/technical-ai-safety/2/1")

# Click next lesson button
next_button = await browser.page.query_selector('[aria-label="Next lesson"]')
if next_button:
    await next_button.click()
```

### Content Downloading

```python
# Save lesson content
content = await browser.page.inner_html('.lesson-content')
with open('lesson.html', 'w') as f:
    f.write(content)
```

### Handling Dynamic Content

```python
# Wait for specific elements
await browser.page.wait_for_selector('.video-player', timeout=10000)

# Wait for network idle
await browser.page.wait_for_load_state('networkidle')
```

## Limitations

1. **OAuth/SSO Login**: If Bluedot uses Google/Microsoft SSO, manual login is required
2. **Captchas**: Cannot automatically solve captchas
3. **Rate Limiting**: May be blocked if too many requests are made
4. **Dynamic Content**: Some content may load after initial page load

## Next Steps

- Add content parsing and extraction
- Implement lesson progress tracking
- Create automated quiz/exercise completion
- Add support for downloading course materials
- Implement retry logic for network errors