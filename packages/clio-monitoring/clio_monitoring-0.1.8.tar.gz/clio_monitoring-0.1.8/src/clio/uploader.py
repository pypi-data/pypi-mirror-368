"""File upload functionality for Clio SDK"""

import asyncio
import httpx
from pathlib import Path
from typing import Optional, Tuple, BinaryIO
import os

from .config import Config
from .exceptions import ClioUploadError
from .utils import mask_sensitive_data
from .logger import get_logger

logger = get_logger("uploader")


class Uploader:
    def __init__(self, config: Config):
        self.config = config

    async def upload_file(
        self,
        file_path: Path,
        presigned_url: str,
        content_type: str = "video/mp4"
    ) -> bool:
        """Upload a file to S3 using presigned URL with streaming for large files"""
        file_size = file_path.stat().st_size
        logger.info(
            f"📤 Starting upload of {file_path.name} ({file_size:,} bytes)")

        if not file_path.exists():
            raise ClioUploadError(f"File not found: {file_path}")

        # Use streaming for files larger than 10MB
        use_streaming = file_size > 10 * 1024 * 1024

        # Calculate timeout based on file size (minimum 30s, 1s per MB)
        timeout_seconds = max(30, min(600, file_size // (1024 * 1024)))
        timeout = httpx.Timeout(timeout_seconds, connect=10.0)

        async with httpx.AsyncClient(
            timeout=timeout,
            verify=self.config.verify_ssl
        ) as client:
            for attempt in range(self.config.retry_attempts):
                try:
                    logger.info(
                        f"📤 Upload attempt {attempt + 1} for {file_path.name} (timeout: {timeout_seconds}s)")

                    if use_streaming:
                        # Stream large files
                        logger.debug(
                            f"Using streaming upload for large file ({file_size:,} bytes)")
                        with open(file_path, 'rb') as f:
                            response = await client.put(
                                presigned_url,
                                content=self._file_reader(f, file_size),
                                headers={
                                    "Content-Type": content_type,
                                    "Content-Length": str(file_size)
                                }
                            )
                    else:
                        # Load small files into memory
                        with open(file_path, 'rb') as f:
                            file_content = f.read()

                        response = await client.put(
                            presigned_url,
                            content=file_content,
                            headers={"Content-Type": content_type}
                        )

                    logger.info(
                        f"📤 Upload response: Status {response.status_code}")
                    if response.status_code == 200:
                        logger.info(
                            f"✅ Successfully uploaded {file_path.name}")
                        return True
                    else:
                        error_msg = mask_sensitive_data(
                            response.text[:200])  # Limit error message size
                        logger.warning(
                            f"❌ Upload attempt {attempt + 1} failed with status {response.status_code}: {error_msg}"
                        )

                except asyncio.TimeoutError:
                    logger.error(
                        f"Upload attempt {attempt + 1} timed out after {timeout_seconds}s")
                    if attempt == self.config.retry_attempts - 1:
                        if self.config.raise_on_error:
                            raise ClioUploadError(
                                f"Upload timed out for {file_path.name}")
                        return False
                except Exception as e:
                    error_msg = mask_sensitive_data(str(e))
                    logger.error(
                        f"Upload attempt {attempt + 1} failed: {error_msg}")
                    if attempt == self.config.retry_attempts - 1:
                        if self.config.raise_on_error:
                            raise ClioUploadError(
                                f"Failed to upload {file_path.name}: {error_msg}")
                        return False

                # Wait before retry with exponential backoff
                if attempt < self.config.retry_attempts - 1:
                    wait_time = min(30, 2 ** attempt)  # Cap at 30 seconds
                    logger.debug(f"Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)

        return False

    async def _file_reader(self, file: BinaryIO, total_size: int):
        """Async generator for streaming file uploads with progress tracking"""
        chunk_size = 1024 * 1024  # 1MB chunks
        bytes_read = 0

        while True:
            # Read file chunk asynchronously to avoid blocking
            chunk = await asyncio.get_event_loop().run_in_executor(None, file.read, chunk_size)
            if not chunk:
                break

            bytes_read += len(chunk)
            if bytes_read % (10 * 1024 * 1024) == 0:  # Log every 10MB
                progress = (bytes_read / total_size) * 100
                logger.debug(
                    f"Upload progress: {progress:.1f}% ({bytes_read:,}/{total_size:,} bytes)")

            yield chunk

    async def upload_files(
        self,
        video_path: Optional[Path],
        trace_path: Optional[Path],
        video_url: Optional[str],
        trace_url: Optional[str]
    ) -> Tuple[bool, bool]:
        """Upload video and trace files concurrently"""
        logger.info(f"🚀 Starting file uploads...")
        logger.info(f"🎥 Video path: {mask_sensitive_data(str(video_path))}")
        logger.info(f"📊 Trace path: {mask_sensitive_data(str(trace_path))}")

        tasks = []

        if video_path and video_url:
            logger.info(f"🎥 Adding video upload task")
            tasks.append(self.upload_file(video_path, video_url, "video/webm"))

        if trace_path and trace_url:
            logger.info(f"📊 Adding trace upload task")
            tasks.append(self.upload_file(
                trace_path, trace_url, "application/zip"))

        if not tasks:
            logger.warning(
                "⚠️ No upload tasks created - no files or URLs provided")
            return False, False

        # Run uploads with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=600  # 10 minute total timeout
            )
        except asyncio.TimeoutError:
            logger.error("❌ Upload operation timed out after 10 minutes")
            return False, False

        video_success = False
        trace_success = False

        if video_path and video_url:
            video_success = results[0] is True

        if trace_path and trace_url:
            idx = 1 if (video_path and video_url) else 0
            trace_success = results[idx] is True

        return video_success, trace_success
