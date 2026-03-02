#!/usr/bin/env python3
"""
Browser automation for Bluedot AI Safety course
https://bluedot.org/courses/technical-ai-safety/1/1

This script handles authentication and navigation for the Bluedot course site.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional
import sys

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BluedotBrowser:
    """Handles browser automation for Bluedot AI Safety courses."""

    def __init__(self, headless: bool = False):
        """
        Initialize the Bluedot browser automation.

        Args:
            headless: Whether to run in headless mode (False recommended for initial auth)
        """
        self.headless = headless
        self.auth_file = Path(__file__).parent / ".auth" / "bluedot_state.json"
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the browser and create context."""
        playwright = await async_playwright().start()

        # Launch browser with anti-detection settings
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )

        # Check if we have saved authentication state
        if self.auth_file.exists():
            print(f"Loading authentication state from {self.auth_file}")
            self.context = await self.browser.new_context(
                storage_state=str(self.auth_file),
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
        else:
            print("No saved authentication state found. Creating new context.")
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

        self.page = await self.context.new_page()

        # Add stealth settings
        await self.page.add_init_script("""
            // Override the navigator.webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // Override plugins to look more realistic
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            // Override languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)

    async def close(self):
        """Close browser and cleanup."""
        if self.browser:
            await self.browser.close()

    async def save_auth_state(self):
        """Save current authentication state to file."""
        if self.context:
            # Ensure auth directory exists
            self.auth_file.parent.mkdir(parents=True, exist_ok=True)

            # Save the storage state
            await self.context.storage_state(path=str(self.auth_file))
            print(f"Authentication state saved to {self.auth_file}")

    async def navigate_to_course(self, course_url: str = "https://bluedot.org/courses/technical-ai-safety/1/1"):
        """
        Navigate to the course page.

        Args:
            course_url: The URL of the course to navigate to

        Returns:
            True if navigation successful, False otherwise
        """
        try:
            print(f"Navigating to {course_url}")
            response = await self.page.goto(course_url, wait_until='networkidle', timeout=30000)

            # Check if we're redirected to login
            current_url = self.page.url
            print(f"Current URL: {current_url}")

            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                print("Redirected to login page. Authentication required.")
                return False

            # Wait for course content to load
            try:
                await self.page.wait_for_selector('[class*="course"], [class*="lesson"], [class*="content"], main',
                                                   timeout=10000)
                print("Course content detected.")
                return True
            except:
                print("Course content not found, but page loaded.")
                return True

        except Exception as e:
            print(f"Error navigating to course: {e}")
            return False

    async def manual_login(self):
        """
        Navigate to login page and wait for manual authentication.

        This method opens the login page and waits for the user to manually
        log in. Once logged in, it saves the authentication state.
        """
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("\nThe browser will open the Bluedot login page.")
        print("Please log in manually using your credentials.")
        print("After successful login, press Enter in the terminal...")
        print("="*60 + "\n")

        # Navigate to the main page which should redirect to login
        # Use 'load' instead of 'networkidle' to handle redirects better
        try:
            await self.page.goto("https://bluedot.org/courses/technical-ai-safety/1/1",
                                wait_until='load', timeout=30000)
        except Exception as e:
            # If navigation fails due to redirect, that's ok - we're expecting it
            print(f"Navigation redirected (expected): {type(e).__name__}")
            pass

        # Wait a bit for any redirects to complete
        await asyncio.sleep(2)

        # Wait for user to complete manual login
        input("\nPress Enter after you've successfully logged in...")

        # Save the authentication state
        await self.save_auth_state()
        print("Authentication state has been saved for future use.")

    async def is_authenticated(self) -> bool:
        """
        Check if we're currently authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        try:
            # Navigate to a protected page
            await self.page.goto("https://bluedot.org/courses",
                                wait_until='networkidle', timeout=10000)

            # Check if we're on a login page
            current_url = self.page.url
            if 'login' in current_url.lower() or 'signin' in current_url.lower():
                return False

            # Look for user-specific elements (adjust selectors as needed)
            user_elements = await self.page.query_selector_all(
                '[class*="user"], [class*="profile"], [class*="avatar"], [class*="account"]'
            )

            return len(user_elements) > 0

        except Exception as e:
            print(f"Error checking authentication: {e}")
            return False

    async def extract_course_content(self):
        """
        Extract content from the current course page.

        Returns:
            Dictionary containing course content
        """
        content = {}

        try:
            # Extract page title
            title = await self.page.title()
            content['title'] = title

            # Try various selectors for course content
            selectors = {
                'course_title': 'h1, [class*="title"]',
                'lesson_content': '[class*="lesson"], [class*="content"], main',
                'video': 'video, iframe[src*="youtube"], iframe[src*="vimeo"]',
                'navigation': '[class*="nav"], [class*="menu"]'
            }

            for key, selector in selectors.items():
                elements = await self.page.query_selector_all(selector)
                if elements:
                    content[key] = f"Found {len(elements)} {key} element(s)"

            # Get page text content
            text_content = await self.page.inner_text('body')
            content['text_preview'] = text_content[:500] if text_content else "No text content"

            # Screenshot the page for reference
            screenshot_path = Path(__file__).parent / ".auth" / "current_page.png"
            await self.page.screenshot(path=str(screenshot_path))
            content['screenshot'] = str(screenshot_path)

        except Exception as e:
            content['error'] = str(e)

        return content


async def main():
    """Main function to demonstrate Bluedot browser automation."""

    # Run in non-headless mode for initial setup
    async with BluedotBrowser(headless=False) as browser:

        # Check if we're already authenticated
        if await browser.is_authenticated():
            print("✅ Already authenticated!")
        else:
            print("❌ Not authenticated. Starting manual login process...")
            await browser.manual_login()

        # Navigate to the course
        success = await browser.navigate_to_course()

        if success:
            print("\n✅ Successfully navigated to course!")

            # Extract and display course content
            print("\nExtracting course content...")
            content = await browser.extract_course_content()

            print("\nCourse Content Summary:")
            print("-" * 40)
            for key, value in content.items():
                if key != 'text_preview':
                    print(f"{key}: {value}")

            if 'text_preview' in content:
                print(f"\nText preview:\n{content['text_preview']}")

            # Keep browser open for manual interaction if needed
            input("\nPress Enter to close the browser...")
        else:
            print("\n❌ Failed to navigate to course. You may need to log in.")

            # Attempt manual login if navigation failed
            if not await browser.is_authenticated():
                await browser.manual_login()

                # Try navigating again after login
                if await browser.navigate_to_course():
                    print("✅ Successfully navigated to course after login!")

                    # Extract content
                    content = await browser.extract_course_content()
                    print(f"\nCourse page title: {content.get('title', 'Unknown')}")


if __name__ == "__main__":
    # Check if playwright browsers are installed
    browsers_path = Path.home() / "Library" / "Caches" / "ms-playwright"
    if not browsers_path.exists():
        print("⚠️  Playwright browsers not found.")
        print("Run: uv run playwright install")
        sys.exit(1)

    asyncio.run(main())