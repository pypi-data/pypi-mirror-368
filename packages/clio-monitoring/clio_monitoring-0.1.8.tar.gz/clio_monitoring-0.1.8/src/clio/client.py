"""Main Clio client for Playwright integration"""

from __future__ import annotations

import atexit
import os
import tempfile
import threading
from pathlib import Path
from typing import Awaitable, Dict, Optional, TypedDict
from weakref import WeakKeyDictionary

import httpx
from playwright.async_api import BrowserContext, Page

from .config import Config
from .exceptions import (
    ClioError,
    ClioAuthError,
    ClioUploadError,
    ClioRateLimitError
)
from .logger import configure_logging, get_logger
from .uploader import Uploader
from .utils import mask_sensitive_data

logger = get_logger("client")


class PageInfo(TypedDict):
    """Information about a monitored page"""
    video_path: Optional[str]
    uploaded: bool


class RunInfoRequired(TypedDict):
    """Required fields for run info"""
    run_id: str
    video_upload_url: str
    trace_upload_url: str
    video_s3_key: str
    trace_s3_key: str
    trace_enabled: bool
    pages: Dict[Page, PageInfo]


class RunInfo(RunInfoRequired, total=False):
    """Complete run info with optional fields"""
    trace_path: str


class ClioMonitor:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.cliomonitoring.com",
        retry_attempts: int = 3,
        raise_on_error: bool = False,
        verify_ssl: bool = True,
        debug: bool = False
    ) -> None:
        # Configure logging level based on debug flag
        configure_logging(debug)

        self.config: Config = Config(
            api_key=api_key,
            base_url=base_url,
            retry_attempts=retry_attempts,
            raise_on_error=raise_on_error,
            verify_ssl=verify_ssl,
            debug=debug
        )
        self.uploader: Uploader = Uploader(self.config)
        # Use WeakKeyDictionary to auto-cleanup when context is garbage collected
        self._active_runs: WeakKeyDictionary[BrowserContext, RunInfo] = WeakKeyDictionary()
        self._lock: threading.Lock = threading.Lock()
        self._temp_files: set[str] = set()

        # Register cleanup on exit
        atexit.register(self._cleanup_temp_files)

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary trace files on exit"""
        for file_path in self._temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup {file_path}: {e}")

    async def start_run(
        self,
        context: BrowserContext,
        automation_name: Optional[str] = None,
        success_criteria: Optional[str] = None,
        playwright_instructions: Optional[str] = None
    ) -> Awaitable[Optional[str]]:
        """Start monitoring a Playwright automation run
        
        Returns:
            str: The unique run ID for this automation execution
        """
        try:
            # Create run via API
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                response = await client.post(
                    f"{self.config.base_url}/api/sdk/runs/create",
                    headers=self.config.headers,
                    json={
                        "automation_name": automation_name,
                        "success_criteria": success_criteria,
                        "playwright_instructions": playwright_instructions
                    }
                )

                if response.status_code == 429:
                    raise ClioRateLimitError("Monthly rate limit exceeded")
                elif response.status_code == 401:
                    raise ClioAuthError("Invalid API key")
                elif response.status_code != 200:
                    error_msg = mask_sensitive_data(response.text)
                    raise ClioError(f"Failed to create run: {error_msg}")

                run_data = response.json()
                run_id = run_data["id"]

            # Get upload URLs
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            ) as client:
                response = await client.get(
                    f"{self.config.base_url}/api/sdk/runs/{run_id}/upload-urls",
                    headers=self.config.headers
                )

                if response.status_code != 200:
                    error_msg = mask_sensitive_data(response.text)
                    raise ClioError(f"Failed to get upload URLs: {error_msg}")

                upload_data = response.json()

            # Enable tracing if not already enabled
            logger.info(f"🔍 Enabling trace capture for run {run_id}")
            await context.tracing.start(screenshots=True, snapshots=True, sources=True)

            # Store run info with thread safety
            with self._lock:
                # Check if context already has a monitor
                if hasattr(context, '_clio_monitor_patched'):
                    logger.warning(
                        "Context already has a Clio monitor attached, skipping")
                    return run_id

                self._active_runs[context] = {
                    "run_id": run_id,
                    "video_upload_url": upload_data["video_upload_url"],
                    "trace_upload_url": upload_data["trace_upload_url"],
                    "video_s3_key": upload_data["video_s3_key"],
                    "trace_s3_key": upload_data["trace_s3_key"],
                    "trace_enabled": True,  # Track that we enabled tracing
                    "pages": {}  # Track pages and their videos
                }

                # Mark context as patched
                context._clio_monitor_patched = True  # type: ignore[attr-defined]
                return run_id

            # Set up page tracking - listen for page creation
            async def on_page_created(page: Page) -> None:
                """Handle new page creation - track it and set up close listener"""
                logger.info(f"📄 New page created: {page.url}")
                
                with self._lock:
                    run_info = self._active_runs.get(context)
                    if not run_info:
                        return
                    
                    # Get video path if available
                    video_path = None
                    if page.video:
                        try:
                            video_path = await page.video.path()
                            logger.info(f"🎥 Page video path: {mask_sensitive_data(str(video_path))}")
                        except Exception as e:
                            logger.debug(f"Could not get video path yet: {e}")
                    
                    # Store page info
                    page_info: PageInfo = {
                        "video_path": str(video_path) if video_path else None,
                        "uploaded": False
                    }
                    run_info["pages"][page] = page_info
                
                # Set up page close event listener
                async def on_page_close(closing_page: Page) -> None:
                    """Handle page close event - update video path if needed"""
                    logger.info(f"🔒 Page closed: {closing_page.url}")
                    
                    # Update video path if we don't have it yet
                    with self._lock:
                        run_info = self._active_runs.get(context)
                        if run_info and closing_page in run_info["pages"]:
                            page_info = run_info["pages"][closing_page]
                            
                            # Get final video path if we don't have it yet
                            if not page_info["video_path"] and closing_page.video:
                                try:
                                    video_path = await closing_page.video.path()
                                    page_info["video_path"] = str(video_path)
                                    logger.info(f"🎥 Updated video path: {mask_sensitive_data(page_info['video_path'])}")
                                except Exception as e:
                                    logger.warning(f"Could not get video path: {e}")
                
                # Register close event listener on the page  
                page.on("close", on_page_close)
            
            # Register page event listener
            context.on("page", on_page_created)

            # Add a public method to manually stop and save trace
            async def stop_and_save_trace() -> None:
                """Stop tracing and save trace file"""
                with self._lock:
                    run_info = self._active_runs.get(context)
                    if not run_info or not run_info.get("trace_enabled"):
                        return
                
                try:
                    logger.info(f"📊 Stopping trace and saving trace file...")
                    # Use temp directory for trace files
                    trace_dir = tempfile.gettempdir()
                    trace_path = os.path.join(
                        trace_dir, f"clio_trace_{run_info['run_id']}.zip")
                    
                    # Check if context is still valid before stopping trace
                    if hasattr(context, '_impl_obj') and not getattr(context._impl_obj, '_is_closed', False):
                        await context.tracing.stop(path=trace_path)
                        logger.info(
                            f"📊 Trace saved to {mask_sensitive_data(trace_path)}")

                        # Store trace path for upload and cleanup
                        with self._lock:
                            if context in self._active_runs:
                                self._active_runs[context]["trace_path"] = trace_path
                                self._active_runs[context]["trace_enabled"] = False  # Mark as stopped
                                self._temp_files.add(trace_path)
                    else:
                        logger.warning("📊 Context already closed, cannot save trace")
                        with self._lock:
                            if context in self._active_runs:
                                self._active_runs[context]["trace_enabled"] = False
                except Exception as trace_error:
                    logger.warning(
                        f"⚠️ Failed to save trace: {mask_sensitive_data(str(trace_error))}")
                    # Mark trace as disabled even on error to prevent retry loops
                    with self._lock:
                        if context in self._active_runs:
                            self._active_runs[context]["trace_enabled"] = False

            # Store the stop function for external access
            context._clio_stop_trace = stop_and_save_trace  # type: ignore[attr-defined]

            # Monkey-patch context.close() to save trace before closing
            original_close = context.close
            
            async def patched_close(*, reason: Optional[str] = None) -> None:
                """Patched close method that closes context first, then uploads files"""
                logger.info(f"🔒 Context close initiated, stopping trace first...")
                
                # Stop and save trace before closing
                await stop_and_save_trace()
                
                logger.info(f"🔒 Closing context now...")
                # Close the context FIRST - this is when Playwright finishes writing video files
                await original_close(reason=reason)
                
                logger.info(f"📤 Context closed, video files are now complete, uploading...")
                # Now that context is closed, video files are fully written - upload them
                try:
                    await self._handle_context_upload(context)
                    logger.info(f"✅ Context upload completed")
                except Exception as e:
                    logger.error(
                        f"❌ Error uploading files: {mask_sensitive_data(str(e))}")
                    if self.config.raise_on_error:
                        raise
                finally:
                    # Clean up resources
                    logger.info(f"🧹 Cleaning up context")
                    with self._lock:
                        if context in self._active_runs:
                            run_info = self._active_runs.get(context, {})
                            # Clean up trace file
                            trace_path = run_info.get("trace_path")
                            if trace_path and os.path.exists(trace_path):
                                try:
                                    os.remove(trace_path)
                                    self._temp_files.discard(trace_path)
                                    logger.debug(
                                        f"Cleaned up trace file: {mask_sensitive_data(trace_path)}")
                                except Exception as e:
                                    logger.warning(f"Failed to cleanup trace: {e}")

                            del self._active_runs[context]

            # Replace the close method with our patched version
            context.close = patched_close

            logger.info(
                f"Started monitoring run {mask_sensitive_data(run_id)} for {automation_name or 'untitled automation'}")

            return run_id

        except Exception as e:
            logger.error(f"Failed to start run: {mask_sensitive_data(str(e))}")
            # Clean up on failure
            with self._lock:
                if context in self._active_runs:
                    del self._active_runs[context]
                if hasattr(context, '_clio_monitor_patched'):
                    delattr(context, '_clio_monitor_patched')
            if self.config.raise_on_error:
                raise

    async def _handle_context_upload(self, context: BrowserContext) -> None:
        """Handle uploading trace and any remaining videos after context closes"""
        logger.info(f"🚀 _handle_context_upload called for context")

        with self._lock:
            run_info = self._active_runs.get(context)

        if not run_info:
            logger.warning(f"⚠️ Context not found in active runs")
            return

        try:
            # Check if any videos were uploaded from pages
            any_video_uploaded = False
            pages_info = run_info.get("pages", {})
            for _page, page_info in pages_info.items():
                if page_info.get("uploaded"):
                    any_video_uploaded = True
                    break
            
            # Upload videos (context is closed, so video files are complete)
            for _page, page_info in pages_info.items():
                video_path_str = page_info.get("video_path")
                
                if video_path_str and not page_info.get("uploaded"):
                    logger.info(f"📤 Uploading video: {mask_sensitive_data(video_path_str)}")
                    
                    try:
                        video_path = Path(video_path_str)
                        
                        if video_path.exists() and video_path.stat().st_size > 0:
                            video_success, _ = await self.uploader.upload_files(
                                video_path=video_path,
                                trace_path=None,
                                video_url=run_info["video_upload_url"],
                                trace_url=None
                            )
                            if video_success:
                                page_info["uploaded"] = True
                                any_video_uploaded = True
                                logger.info(f"✅ Video uploaded successfully")
                        else:
                            logger.warning(f"⚠️ Skipping empty or missing video file")
                            
                    except Exception as e:
                        logger.error(f"Failed to upload video: {e}")

            # Find trace file (use stored trace path if available)
            trace_path = None
            stored_trace_path = run_info.get("trace_path")
            if stored_trace_path:
                trace_path = Path(stored_trace_path)
                logger.info(f"📊 Using stored trace file: {trace_path}")
            elif hasattr(context, '_impl_obj') and hasattr(context._impl_obj, '_trace_path'):  # type: ignore[misc]
                trace_path = Path(context._impl_obj._trace_path)  # type: ignore[misc]
                logger.info(f"📊 Using context trace file: {trace_path}")

            # Upload trace
            trace_success = False
            if trace_path:
                logger.info(f"📤 Uploading trace file...")
                _, trace_success = await self.uploader.upload_files(
                    video_path=None,
                    trace_path=trace_path,
                    video_url=None,
                    trace_url=run_info["trace_upload_url"]
                )
                if trace_success:
                    logger.info(f"✅ Trace uploaded successfully")

            # Mark upload as complete if anything was uploaded
            if any_video_uploaded or trace_success:
                async with httpx.AsyncClient(
                    timeout=self.config.timeout,
                    verify=self.config.verify_ssl
                ) as client:
                    response = await client.post(
                        f"{self.config.base_url}/api/sdk/runs/{run_info['run_id']}/complete",
                        headers=self.config.headers,
                        json={
                            "video_s3_key": run_info["video_s3_key"] if any_video_uploaded else None,
                            "trace_s3_key": run_info["trace_s3_key"] if trace_success else None
                        }
                    )

                    if response.status_code == 200:
                        logger.info(
                            f"Successfully completed run {mask_sensitive_data(run_info['run_id'])}")
                    else:
                        error_msg = mask_sensitive_data(response.text)
                        logger.error(
                            f"Failed to mark upload complete: {error_msg}")

        except Exception as e:
            error_msg = mask_sensitive_data(str(e))
            logger.error(f"Failed to handle context upload: {error_msg}")
            if self.config.raise_on_error:
                raise ClioUploadError(f"Upload failed: {error_msg}")
