#  Copyright (c) 2025 AshokShau
#  Licensed under the GNU AGPL v3.0: https://www.gnu.org/licenses/agpl-3.0.html
#  Part of the TgMusicBot project. All rights reserved where applicable.

import asyncio
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union
from urllib.parse import unquote

import aiofiles
import httpx

import config
from AviaxMusic.logging import LOGGER

@dataclass
class DownloadResult:
    success: bool
    file_path: Optional[Path] = None
    error: Optional[str] = None


class HttpxClient:
    DEFAULT_TIMEOUT = 120
    DEFAULT_DOWNLOAD_TIMEOUT = 180
    CHUNK_SIZE = 8192
    MAX_RETRIES = 2
    BACKOFF_FACTOR = 1.0

    def __init__(
        self,
        timeout: int = DEFAULT_TIMEOUT,
        download_timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
        max_redirects: int = 0,
    ) -> None:
        self._timeout = timeout
        self._download_timeout = download_timeout
        self._max_redirects = max_redirects
        self._session = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=self._timeout,
                read=self._timeout,
                write=self._timeout,
                pool=self._timeout
            ),
            follow_redirects=max_redirects > 0,
            max_redirects=max_redirects,
        )

    async def close(self) -> None:
        try:
            await self._session.aclose()
        except Exception as e:
            LOGGER(__name__).error("Error closing HTTP session: %s", repr(e))

    @staticmethod
    def _get_headers(url: str, base_headers: dict[str, str]) -> dict[str, str]:
        headers = base_headers.copy()
        if config.API_URL and url.startswith(config.API_URL):
            headers["X-API-Key"] = config.API_KEY
        return headers

    async def download_file(
        self,
        url: str,
        file_path: Optional[Union[str, Path]] = None,
        overwrite: bool = False,
        **kwargs: Any,
    ) -> DownloadResult:
        if not url:
            return DownloadResult(success=False, error="Empty URL provided")

        headers = self._get_headers(url, kwargs.pop("headers", {}))

        try:
            # Dynamic timeout override for known slow hosts
            if "sslip.io" in url:
                timeout = httpx.Timeout(connect=30.0, read=180.0, write=30.0, pool=60.0)
            else:
                timeout = httpx.Timeout(connect=30.0, read=self._download_timeout)

            start = time.monotonic()

            async with self._session.stream(
                "GET", url, timeout=timeout, headers=headers
            ) as response:
                response.raise_for_status()

                # Determine filename
                if file_path is None:
                    cd = response.headers.get("Content-Disposition", "")
                    match = re.search(r'filename="?([^"]+)"?', cd)
                    filename = (
                        unquote(match[1]) if match else (Path(url).name or uuid.uuid4().hex)
                    )
                    path = Path(config.DOWNLOADS_DIR) / filename
                else:
                    path = Path(file_path) if isinstance(file_path, str) else file_path

                if path.exists() and not overwrite:
                    return DownloadResult(success=True, file_path=path)

                path.parent.mkdir(parents=True, exist_ok=True)
                async with aiofiles.open(path, "wb") as f:
                    async for chunk in response.aiter_bytes(self.CHUNK_SIZE):
                        await f.write(chunk)

            duration = time.monotonic() - start
            LOGGER(__name__).debug("Downloaded file to %s in %.2fs", path, duration)
            return DownloadResult(success=True, file_path=path)

        except Exception as e:
            error_msg = self._handle_http_error(e, url)
            LOGGER(__name__).error(error_msg)
            return DownloadResult(success=False, error=error_msg)

    async def make_request(
        self,
        url: str,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = BACKOFF_FACTOR,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        if not url:
            LOGGER(__name__).warning("Empty URL provided")
            return None

        headers = self._get_headers(url, kwargs.pop("headers", {}))

        for attempt in range(max_retries):
            try:
                start = time.monotonic()
                response = await self._session.get(url, headers=headers, **kwargs)
                response.raise_for_status()
                duration = time.monotonic() - start
                LOGGER(__name__).debug("Request to %s succeeded in %.2fs", url, duration)
                return response.json()

            except httpx.TooManyRedirects as e:
                error_msg = f"Redirect loop for {url}: {repr(e)}"
                LOGGER(__name__).warning(error_msg)
                if attempt == max_retries - 1:
                    LOGGER(__name__).error(error_msg)
                    return None

            except httpx.HTTPStatusError as e:
                body = e.response.text if e.response else "No response"
                error_msg = f"HTTP error {e.response.status_code} for {url}. Body: {body}"
                LOGGER(__name__).warning(error_msg)
                if attempt == max_retries - 1:
                    LOGGER(__name__).error(error_msg)
                    return None

            except httpx.RequestError as e:
                error_msg = f"Request failed for {url}: {repr(e)}"
                LOGGER(__name__).warning(error_msg)
                if attempt == max_retries - 1:
                    LOGGER(__name__).error(error_msg)
                    return None

            except ValueError as e:
                LOGGER(__name__).error("Invalid JSON response from %s: %s", url, repr(e))
                return None

            except Exception as e:
                LOGGER(__name__).error("Unexpected error for %s: %s", url, repr(e))
                return None

            await asyncio.sleep(backoff_factor * (2 ** attempt))

        LOGGER(__name__).error("All retries failed for URL: %s", url)
        return None

    @staticmethod
    def _handle_http_error(e: Exception, url: str) -> str:
        if isinstance(e, httpx.TooManyRedirects):
            return f"Too many redirects for {url}: {repr(e)}"
        elif isinstance(e, httpx.HTTPStatusError):
            return f"HTTP error {e.response.status_code} for {url}. Body: {e.response.text}"
        elif isinstance(e, httpx.ReadTimeout):
            return f"Read timeout for {url}: {repr(e)}"
        elif isinstance(e, httpx.RequestError):
            return f"Request failed for {url}: {repr(e)}"
        return f"Unexpected error for {url}: {repr(e)}"
