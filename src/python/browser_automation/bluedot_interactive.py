#!/usr/bin/env python3
"""
Interactive browser automation for Bluedot AI Safety course.
This version keeps the browser open and waits for you to log in.
"""

import asyncio
from bluedot_browser import BluedotBrowser


async def interactive_login():
    """
    Interactive login flow - opens browser and waits for successful login.
    """
    print("="*60)
    print("BLUEDOT INTERACTIVE LOGIN")
    print("="*60)
    print("\nStarting browser automation...")
    print("A browser window will open shortly.")
    print("\nInstructions:")
    print("1. The browser will navigate to the Bluedot course page")
    print("2. You'll be redirected to the login page")
    print("3. Log in using your credentials (email/password or Google)")
    print("4. After successful login, navigate to a course page")
    print("5. Wait 10 seconds for the script to detect successful login")
    print("6. Your session will be automatically saved")
    print("="*60 + "\n")

    async with BluedotBrowser(headless=False) as browser:
        # Check if we're already authenticated
        print("Checking authentication status...")

        try:
            # Try to navigate to the course
            await browser.page.goto("https://bluedot.org/courses/technical-ai-safety/1/1",
                                   wait_until='load', timeout=30000)

            # Wait a bit for redirects
            await asyncio.sleep(3)

            current_url = browser.page.url
            print(f"\nCurrent URL: {current_url}")

            # Check if we're on a login page
            if 'login' in current_url.lower():
                print("\n⚠️  Not authenticated - please log in now...")
                print("\nWaiting for you to complete login...")
                print("(The script will automatically detect when you're logged in)")

                # Wait for successful login (check every 5 seconds for up to 5 minutes)
                max_attempts = 60
                for attempt in range(max_attempts):
                    await asyncio.sleep(5)

                    current_url = browser.page.url
                    print(f"  Checking... ({attempt + 1}/{max_attempts}) - URL: {current_url[:60]}...")

                    # Check if we're no longer on the login page
                    if 'login' not in current_url.lower():
                        print("\n✅ Login detected!")
                        break
                else:
                    print("\n⚠️  Timeout waiting for login. Please try again.")
                    return

                # Wait a bit more to ensure session is stable
                await asyncio.sleep(3)

                # Save authentication state
                await browser.save_auth_state()
                print("\n✅ Authentication state saved!")

            else:
                print("✅ Already authenticated!")

            # Try to extract some course content
            print("\nExtracting course information...")
            content = await browser.extract_course_content()

            print("\n" + "="*60)
            print("COURSE CONTENT SUMMARY")
            print("="*60)
            print(f"Page title: {content.get('title', 'Unknown')}")

            for key, value in content.items():
                if key not in ['title', 'text_preview', 'screenshot']:
                    print(f"{key}: {value}")

            if 'text_preview' in content:
                print(f"\nText preview:\n{content['text_preview'][:300]}...")

            if 'screenshot' in content:
                print(f"\nScreenshot saved: {content['screenshot']}")

            print("\n" + "="*60)
            print("Session is ready! You can now close the browser.")
            print("Future runs will use the saved authentication.")
            print("="*60)

            # Keep browser open for a bit so you can see the result
            print("\nKeeping browser open for 30 seconds...")
            await asyncio.sleep(30)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please check the browser window and try again.")


if __name__ == "__main__":
    asyncio.run(interactive_login())