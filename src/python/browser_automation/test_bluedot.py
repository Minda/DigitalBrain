#!/usr/bin/env python3
"""
Simple test script for Bluedot browser automation.
This script performs a basic navigation test to the Bluedot site.
"""

import asyncio
from playwright.async_api import async_playwright


async def test_bluedot_access():
    """Test basic access to Bluedot site."""

    print("Starting Playwright browser test for Bluedot...")

    async with async_playwright() as p:
        # Launch browser in non-headless mode so you can see what's happening
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )

        # Create a new browser context
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        # Create a new page
        page = await context.new_page()

        try:
            # Navigate to the Bluedot course page
            print("\nNavigating to: https://bluedot.org/courses/technical-ai-safety/1/1")
            response = await page.goto(
                "https://bluedot.org/courses/technical-ai-safety/1/1",
                wait_until='networkidle',
                timeout=30000
            )

            # Get the current URL after navigation
            current_url = page.url
            print(f"Current URL: {current_url}")

            # Get the page title
            title = await page.title()
            print(f"Page title: {title}")

            # Check if we were redirected to a login page
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                print("\n⚠️  Redirected to login page - authentication required")
                print("This is expected behavior for a protected course.")

                # Take a screenshot of the login page
                await page.screenshot(path="bluedot_login_page.png")
                print("Screenshot saved as: bluedot_login_page.png")

                # Look for login form elements
                login_forms = await page.query_selector_all('form, [type="email"], [type="password"], input')
                print(f"Found {len(login_forms)} potential login form elements")

            else:
                print("\n✅ Page loaded without login redirect")
                print("(This might mean the course is public or you have saved cookies)")

                # Take a screenshot of the page
                await page.screenshot(path="bluedot_course_page.png")
                print("Screenshot saved as: bluedot_course_page.png")

            # Try to find course-related elements
            print("\nLooking for course elements...")
            selectors = {
                'headings': 'h1, h2, h3',
                'buttons': 'button, [role="button"]',
                'links': 'a[href*="course"], a[href*="lesson"]',
                'content': '[class*="content"], [class*="lesson"], main'
            }

            for name, selector in selectors.items():
                elements = await page.query_selector_all(selector)
                if elements:
                    print(f"  - Found {len(elements)} {name}")

            # Get some text content from the page
            print("\nExtracting text preview...")
            text_content = await page.inner_text('body')
            preview = text_content[:300] if text_content else "No text content"
            print(f"Text preview: {preview}...")

            # Wait a bit to see the page
            print("\nKeeping browser open for 5 seconds...")
            await asyncio.sleep(5)

        except Exception as e:
            print(f"\n❌ Error during test: {e}")

        finally:
            # Close the browser
            await browser.close()
            print("\nTest completed. Browser closed.")


if __name__ == "__main__":
    print("="*60)
    print("BLUEDOT BROWSER AUTOMATION TEST")
    print("="*60)
    asyncio.run(test_bluedot_access())