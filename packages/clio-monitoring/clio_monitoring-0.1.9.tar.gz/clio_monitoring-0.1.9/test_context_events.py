"""
Test if Playwright has context close events
"""

import asyncio
from playwright.async_api import async_playwright

async def test_context_events():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        context = await browser.new_context()
        
        # Check what events are available on context
        print("Context event names:", dir(context))
        print("\nLooking for close-related events...")
        
        # Try to listen for close event
        close_fired = False
        
        async def on_context_close():
            nonlocal close_fired
            close_fired = True
            print("Context close event fired!")
        
        try:
            # Try registering a close event
            context.on("close", on_context_close)
            print("Successfully registered 'close' event listener")
        except Exception as e:
            print(f"Could not register 'close' event: {e}")
        
        # Also check browser context events
        print("\nBrowser events:", dir(browser))
        
        # Create a page
        page = await context.new_page()
        await page.goto("https://example.com")
        
        # Close context
        print("\nClosing context...")
        await context.close()
        await asyncio.sleep(0.5)
        
        print(f"Close event fired: {close_fired}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_context_events())