import asyncio
import json
import random
import os
from pathlib import Path
from playwright.async_api import async_playwright

COOKIES_FILE = "reddit_session.json"

async def save_session(page):
    """Save cookies after manual login so we don't log in every time."""
    cookies = await page.context.cookies()
    Path(COOKIES_FILE).write_text(json.dumps(cookies))
    print("✅ Session saved to reddit_session.json")

async def load_session(context):
    """Load saved cookies into the browser context."""
    if Path(COOKIES_FILE).exists():
        cookies = json.loads(Path(COOKIES_FILE).read_text())
        await context.add_cookies(cookies)
        return True
    return False

async def login_and_save(username: str, password: str):
    """
    Run this once manually to log in and save your session.
    After this, post_comment() will reuse the saved cookies.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # visible so you can solve CAPTCHAs
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.reddit.com/login/")
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_url("https://www.reddit.com/", timeout=15000)

        print("✅ Logged in successfully")
        await save_session(page)
        await browser.close()

async def post_comment(post_url: str, comment_text: str) -> dict:
    """
    Post a comment on a Reddit thread.
    
    Args:
        post_url: Full Reddit post URL
        comment_text: The comment to post (markdown supported)
    
    Returns:
        dict with success status and comment URL if successful
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            # Realistic browser fingerprint
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        session_loaded = await load_session(context)
        if not session_loaded:
            await browser.close()
            return {"success": False, "error": "No session found. Run login_and_save() first."}

        page = await context.new_page()

        try:
            # Use old.reddit.com — simpler DOM, more reliable for automation
            old_url = post_url.replace("www.reddit.com", "old.reddit.com").replace("new.reddit.com", "old.reddit.com")
            await page.goto(old_url, wait_until="domcontentloaded", timeout=20000)

            # Check we're still logged in
            is_logged_in = await page.query_selector('.user a')
            if not is_logged_in:
                await browser.close()
                return {"success": False, "error": "Session expired. Run login_and_save() again."}

            # Find the top-level comment box
            comment_box = await page.wait_for_selector('textarea[name="text"]', timeout=10000)

            # Human-like typing with random delays
            await comment_box.click()
            await asyncio.sleep(random.uniform(0.5, 1.2))
            for char in comment_text:
                await comment_box.type(char, delay=random.randint(30, 90))

            await asyncio.sleep(random.uniform(1.0, 2.5))

            # Submit
            submit_btn = await page.query_selector('.usertext-buttons button[type="submit"]')
            await submit_btn.click()

            # Wait for comment to appear
            await asyncio.sleep(random.uniform(2, 4))

            # Try to grab the URL of the new comment
            new_comment = await page.query_selector('.comment .usertext-body')
            comment_url = None
            if new_comment:
                permalink = await page.query_selector('.comment .bylink')
                if permalink:
                    comment_url = await permalink.get_attribute('href')

            print(f"✅ Comment posted on {post_url}")
            await browser.close()
            return {"success": True, "post_url": post_url, "comment_url": comment_url}

        except Exception as e:
            await browser.close()
            return {"success": False, "error": str(e), "post_url": post_url}


async def main():
    """
    Example usage. Two modes:

    MODE 1 – First time setup (run once):
        Set LOGIN_MODE=true, add your credentials below.
        A visible browser opens so you can handle any CAPTCHA.

    MODE 2 – Post a comment (normal usage):
        Set LOGIN_MODE=false, set POST_URL and COMMENT_TEXT.
        Runs headless.
    """

    LOGIN_MODE = os.getenv("LOGIN_MODE", "false").lower() == "true"

    if LOGIN_MODE:
        # Run once to save your session
        await login_and_save(
            username=os.getenv("REDDIT_USERNAME", "ShopifyAppGuy"),
            password=os.getenv("REDDIT_PASSWORD", "wqv_pcn@ayt7RYA9kne"),
        )
    else:
        # Normal operation — called by n8n with env vars or hardcoded for testing
        post_url = os.getenv("POST_URL", "https://www.reddit.com/r/shopify/comments/EXAMPLE/")
        comment_text = os.getenv("COMMENT_TEXT", "Your comment here.")

        result = await post_comment(post_url, comment_text)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())