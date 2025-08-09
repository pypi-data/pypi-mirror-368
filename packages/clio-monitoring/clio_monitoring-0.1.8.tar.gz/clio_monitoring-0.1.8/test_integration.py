#!/usr/bin/env python
"""
Integration tests for Clio SDK with mock server
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
import os
import json
import tempfile
import shutil
from aiohttp import web
from playwright.async_api import async_playwright
from clio import ClioMonitor
import logging

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MockClioServer:
    """Mock Clio API server for testing"""
    
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.runs = {}
        self.uploaded_videos = []
        self.uploaded_traces = []
        
    def setup_routes(self):
        self.app.router.add_post('/api/sdk/runs/create', self.create_run)
        self.app.router.add_get('/api/sdk/runs/{run_id}/upload-urls', self.get_upload_urls)
        self.app.router.add_post('/api/sdk/runs/{run_id}/complete', self.complete_run)
        self.app.router.add_put('/upload/video/{run_id}', self.upload_video)
        self.app.router.add_put('/upload/trace/{run_id}', self.upload_trace)
    
    async def create_run(self, request):
        data = await request.json()
        run_id = f"test_run_{len(self.runs) + 1}"
        self.runs[run_id] = {
            "automation_name": data.get("automation_name"),
            "success_criteria": data.get("success_criteria"),
            "status": "created"
        }
        return web.json_response({"id": run_id})
    
    async def get_upload_urls(self, request):
        run_id = request.match_info['run_id']
        base_url = f"http://localhost:8888"
        return web.json_response({
            "video_upload_url": f"{base_url}/upload/video/{run_id}",
            "trace_upload_url": f"{base_url}/upload/trace/{run_id}",
            "video_s3_key": f"videos/{run_id}.webm",
            "trace_s3_key": f"traces/{run_id}.zip"
        })
    
    async def upload_video(self, request):
        run_id = request.match_info['run_id']
        content = await request.read()
        self.uploaded_videos.append({
            "run_id": run_id,
            "size": len(content)
        })
        print(f"📹 Received video upload for {run_id}: {len(content)} bytes")
        return web.Response(status=200)
    
    async def upload_trace(self, request):
        run_id = request.match_info['run_id']
        content = await request.read()
        self.uploaded_traces.append({
            "run_id": run_id,
            "size": len(content)
        })
        print(f"📊 Received trace upload for {run_id}: {len(content)} bytes")
        return web.Response(status=200)
    
    async def complete_run(self, request):
        run_id = request.match_info['run_id']
        data = await request.json()
        if run_id in self.runs:
            self.runs[run_id]["status"] = "completed"
            self.runs[run_id]["uploaded_files"] = data
        print(f"✅ Run {run_id} marked as complete")
        return web.Response(status=200)
    
    async def start(self, port=8888):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', port)
        await site.start()
        return runner


async def test_single_page():
    """Test with a single page"""
    print("\n" + "="*50)
    print("TEST: Single Page Video Upload")
    print("="*50)
    
    # Start mock server
    server = MockClioServer()
    runner = await server.start()
    
    try:
        # Create temp directory for videos
        video_dir = tempfile.mkdtemp(prefix="clio_test_")
        
        # Initialize SDK
        monitor = ClioMonitor(
            api_key="clio_test_key_123",
            base_url="http://localhost:8888",
            debug=True
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Create context with video recording
            context = await browser.new_context(
                record_video_dir=video_dir,
                record_video_size={"width": 640, "height": 480}
            )
            
            # Start monitoring
            await monitor.start_run(
                context=context,
                automation_name="Single Page Test",
                success_criteria="Navigate to example.com"
            )
            
            # Create and use a single page
            page = await context.new_page()
            await page.goto("https://example.com")
            await page.wait_for_timeout(1000)
            
            # Close page (should trigger video upload)
            await page.close()
            await asyncio.sleep(1)  # Give time for upload
            
            # Close context (should upload trace)
            await context.close()
            await browser.close()
        
        # Check results
        print(f"\n📊 Test Results:")
        print(f"   Runs created: {len(server.runs)}")
        print(f"   Videos uploaded: {len(server.uploaded_videos)}")
        print(f"   Traces uploaded: {len(server.uploaded_traces)}")
        
        assert len(server.runs) == 1, "Should have created 1 run"
        assert len(server.uploaded_videos) >= 1, "Should have uploaded at least 1 video"
        assert len(server.uploaded_traces) == 1, "Should have uploaded 1 trace"
        
        print("✅ Single page test PASSED")
        
    finally:
        await runner.cleanup()
        shutil.rmtree(video_dir, ignore_errors=True)


async def test_multiple_pages():
    """Test with multiple pages"""
    print("\n" + "="*50)
    print("TEST: Multiple Pages Video Upload")
    print("="*50)
    
    # Start mock server
    server = MockClioServer()
    runner = await server.start()
    
    try:
        # Create temp directory for videos
        video_dir = tempfile.mkdtemp(prefix="clio_test_")
        
        # Initialize SDK
        monitor = ClioMonitor(
            api_key="clio_test_key_123",
            base_url="http://localhost:8888",
            debug=True
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Create context with video recording
            context = await browser.new_context(
                record_video_dir=video_dir,
                record_video_size={"width": 640, "height": 480}
            )
            
            # Start monitoring
            await monitor.start_run(
                context=context,
                automation_name="Multiple Pages Test",
                success_criteria="Navigate to multiple sites"
            )
            
            # Create multiple pages
            pages = []
            urls = [
                "https://example.com",
                "https://example.org",
                "https://example.net"
            ]
            
            for url in urls:
                page = await context.new_page()
                await page.goto(url)
                await page.wait_for_timeout(500)
                pages.append(page)
                print(f"   Created page: {url}")
            
            # Close pages one by one
            for i, page in enumerate(pages):
                print(f"   Closing page {i+1}...")
                await page.close()
                await asyncio.sleep(0.5)  # Give time for upload
            
            # Close context
            await context.close()
            await browser.close()
        
        # Check results
        print(f"\n📊 Test Results:")
        print(f"   Runs created: {len(server.runs)}")
        print(f"   Videos uploaded: {len(server.uploaded_videos)}")
        print(f"   Traces uploaded: {len(server.uploaded_traces)}")
        
        assert len(server.runs) == 1, "Should have created 1 run"
        assert len(server.uploaded_videos) >= len(urls), f"Should have uploaded at least {len(urls)} videos"
        assert len(server.uploaded_traces) == 1, "Should have uploaded 1 trace"
        
        print("✅ Multiple pages test PASSED")
        
    finally:
        await runner.cleanup()
        shutil.rmtree(video_dir, ignore_errors=True)


async def test_pages_closed_with_context():
    """Test pages that are not explicitly closed (closed with context)"""
    print("\n" + "="*50)
    print("TEST: Pages Closed with Context")
    print("="*50)
    
    # Start mock server
    server = MockClioServer()
    runner = await server.start()
    
    try:
        # Create temp directory for videos
        video_dir = tempfile.mkdtemp(prefix="clio_test_")
        
        # Initialize SDK
        monitor = ClioMonitor(
            api_key="clio_test_key_123",
            base_url="http://localhost:8888",
            debug=True
        )
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Create context with video recording
            context = await browser.new_context(
                record_video_dir=video_dir,
                record_video_size={"width": 640, "height": 480}
            )
            
            # Start monitoring
            await monitor.start_run(
                context=context,
                automation_name="Context Close Test",
                success_criteria="Test videos uploaded when context closes"
            )
            
            # Create pages but don't close them explicitly
            page1 = await context.new_page()
            await page1.goto("https://example.com")
            await page1.wait_for_timeout(500)
            
            page2 = await context.new_page()
            await page2.goto("https://example.org")
            await page2.wait_for_timeout(500)
            
            # Close only one page explicitly
            await page1.close()
            await asyncio.sleep(0.5)
            
            # Close context (should upload remaining videos)
            await context.close()
            await browser.close()
        
        # Check results
        print(f"\n📊 Test Results:")
        print(f"   Runs created: {len(server.runs)}")
        print(f"   Videos uploaded: {len(server.uploaded_videos)}")
        print(f"   Traces uploaded: {len(server.uploaded_traces)}")
        
        assert len(server.runs) == 1, "Should have created 1 run"
        assert len(server.uploaded_videos) >= 2, "Should have uploaded videos for both pages"
        assert len(server.uploaded_traces) == 1, "Should have uploaded 1 trace"
        
        print("✅ Context close test PASSED")
        
    finally:
        await runner.cleanup()
        shutil.rmtree(video_dir, ignore_errors=True)


async def main():
    """Run all integration tests"""
    print("\n🚀 Starting Clio SDK Integration Tests")
    
    try:
        await test_single_page()
        await test_multiple_pages()
        await test_pages_closed_with_context()
        
        print("\n" + "="*50)
        print("🎉 All integration tests PASSED!")
        print("="*50)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())