# Clio SDK

Python SDK for Clio - Playwright automation monitoring service.

## Installation

```bash
pip install clio_monitoring
```

## Quick Start

```python
from playwright.async_api import async_playwright
from clio import ClioMonitor

# Initialize Clio
monitor = ClioMonitor(api_key="your-api-key")

async def test_example():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        # Create context with video recording enabled
        context = await browser.new_context(
            record_video_dir="./videos",
            record_video_size={"width": 1280, "height": 720}
        )

        # Start monitoring this test
        await monitor.start_run(
            context=context,
            automation_name="User Login Test",
            success_criteria="User successfully logs in and sees dashboard",
            playwright_instructions="Navigate to login page, enter credentials, verify dashboard loads"
        )

        # Your test code here
        page = await context.new_page()
        await page.goto("https://example.com/login")
        # ... rest of your test

        # Videos and traces are automatically uploaded when context closes
        await context.close()
        await browser.close()
```

## Configuration

```python
monitor = ClioMonitor(
    api_key="your-api-key",
    base_url="https://api.cliomonitoring.com",  # Optional: for self-hosted instances
    retry_attempts=3,                  # Optional: number of upload retry attempts
    raise_on_error=False              # Optional: raise exceptions on errors
)
```

## Features

- **Automatic Upload**: Videos and traces are automatically uploaded when the browser context closes
- **Retry Logic**: Failed uploads are automatically retried
- **Rate Limiting**: Respects your organization's monthly rate limits
- **Error Handling**: Configurable error handling (log or raise exceptions)

## Requirements

- Python 3.8+
- Playwright 1.40+

## License

MIT
