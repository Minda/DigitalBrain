# Browser Automation for Login-Protected Sites

## Overview
This document outlines approaches for automating interactions with login-protected sites like https://bluedot.org/courses/technical-ai-safety/1/1.

## Available Tools Comparison

### 1. Playwright (Recommended) - Modern Browser Automation
**Pros:**
- Fast, reliable, actively maintained by Microsoft
- Better anti-detection capabilities than older tools
- Cross-browser support (Chrome, Firefox, WebKit)

**Features:**
- Native support for authentication state persistence
- Handles cookies, localStorage, and IndexedDB
- Can save/restore full browser session state
- Supports both headless and headful modes
- Built-in wait strategies for dynamic content

### 2. Selenium - Traditional Browser Automation
**Pros:**
- Mature ecosystem, extensive documentation
- Wide language support

**Cons:**
- Often detected by anti-bot systems
- Slower performance compared to newer tools
- More complex setup

**Status:** Becoming outdated for modern web automation (as of 2024)

### 3. Puppeteer - Chrome-focused Automation
**Pros:**
- Direct Chrome DevTools Protocol access
- Lightweight and fast

**Cons:**
- Chrome/Chromium only
- JavaScript-first (Python support via pyppeteer is less maintained)

### 4. Specialized Anti-Detection Browsers
- **Kameleo:** Advanced masking technology, canvas spoofing
- **Undetected ChromeDriver:** Dynamically alters browser functionality
- **Use case:** When standard automation is consistently blocked

## Implementation Strategy for Bluedot Course Site

### Phase 1: Initial Setup
1. Install Playwright for Python
   ```bash
   pip install playwright
   playwright install  # Downloads browser binaries
   ```

2. Set up browser with proper configuration
   ```python
   browser = playwright.chromium.launch(
       headless=False,  # Start with headful for better success
       args=['--disable-blink-features=AutomationControlled']
   )
   ```

3. Configure viewport and user agent for realistic browsing

### Phase 2: Authentication

#### Manual First Login
1. Navigate to login page
2. Enter credentials programmatically or manually
3. Handle any 2FA/captcha manually
4. Save authentication state after successful login

#### Persist Session
```python
# After successful login
storage = await context.storage_state(path="auth.json")

# Reuse in future sessions
context = await browser.new_context(storage_state="auth.json")
```

#### Storage Structure
```
.auth/
├── bluedot_session.json    # Main session state
├── cookies.json            # Backup of cookies only
└── .gitignore             # Never commit auth data
```

### Phase 3: Course Navigation
1. Load saved authentication state
2. Navigate directly to course pages
3. Extract content, complete exercises, or track progress
4. Handle dynamic content loading with proper waits

```python
# Example navigation pattern
await page.goto("https://bluedot.org/courses/technical-ai-safety/1/1")
await page.wait_for_selector(".course-content", timeout=30000)
content = await page.query_selector(".course-content")
```

### Phase 4: Storage & Security
1. Store auth state in `.auth/` directory (gitignored)
2. Implement session refresh logic
3. Add error handling for expired sessions
4. Rotate sessions if multiple accounts needed

## Key Considerations

### OAuth/SSO Login Challenges

**Problem:** Google/Microsoft OAuth often blocks automation with "This browser or app may not be secure" messages.

**Solutions:**
1. Use official OAuth libraries for initial auth, then persist cookies
2. Manual login once, automate subsequent interactions
3. Implement OAuth flow with local redirect server (recommended for production)

### Bot Detection Evasion

**Detection Methods Sites Use:**
- User agent analysis
- WebDriver property detection
- Canvas fingerprinting
- Behavioral analysis (mouse movements, typing patterns)
- IP reputation checks

**Evasion Techniques:**
1. Use headful mode when possible
2. Add random delays between actions (2-5 seconds)
3. Implement human-like mouse movements
4. Rotate user agents appropriately
5. Consider stealth plugins:
   ```python
   from playwright_stealth import stealth_sync
   stealth_sync(page)
   ```

### Session Management

**Best Practices:**
- Sessions expire - implement refresh logic
- Store multiple session states for different accounts
- Monitor for logout/session termination
- Implement retry logic with fresh login

**Session Refresh Pattern:**
```python
async def ensure_logged_in(page):
    # Check if still logged in
    if not await page.query_selector(".user-avatar"):
        # Reload session or re-login
        await login_with_saved_credentials(page)
```

## Performance Metrics

Based on 2024 research:
- **Headless mode:** 2-15× faster than headful
- **Session reuse:** 60-80% reduction in test time
- **Detection avoidance:** ~85.5% success rate with proper hardening

## Recommended Implementation Path

1. **Start with Playwright in headful mode**
   - Better success rate for initial development
   - Easier to debug authentication issues

2. **Manual login for initial authentication**
   - Handle captchas and 2FA manually
   - Save complete browser state after success

3. **Save and reuse session state**
   - Implement robust session persistence
   - Add expiry checking and refresh logic

4. **Build navigation/interaction logic**
   - Map out course structure
   - Implement content extraction or interaction

5. **Add stealth features if detected**
   - Only add complexity if needed
   - Monitor detection patterns

6. **Consider OAuth libraries for Google/Microsoft login**
   - Use google-auth-oauthlib for Google
   - Use msal for Microsoft

## Security Notes

⚠️ **Never commit authentication data to version control**
- Add `.auth/` to `.gitignore`
- Use environment variables for credentials
- Consider encrypting stored session data
- Implement proper access controls

## Alternative Approaches

### For High-Security Sites
If browser automation is consistently blocked:
1. **Official APIs:** Check if the site offers an API
2. **OAuth Integration:** Use proper OAuth flow instead of browser automation
3. **Browser Extensions:** Build an extension for legitimate use cases
4. **Manual + Semi-Automation:** Hybrid approach with human in the loop

### For Research/Testing
1. Use dedicated testing accounts
2. Respect rate limits and ToS
3. Implement exponential backoff
4. Log all automation activities

## Resources

- [Playwright Python Documentation](https://playwright.dev/python/docs/intro)
- [Playwright Authentication Guide](https://playwright.dev/python/docs/auth)
- [Browser Automation Best Practices 2024](https://scrapingant.com/blog/headless-vs-headful-browsers-in-2025-detection-tradeoffs)
- [OAuth2 in Python](https://testdriven.io/blog/oauth-python/)