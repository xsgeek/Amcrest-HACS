"""Async client and parsers for Amcrest AD410/Dahua-style CGI endpoints."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Iterable
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlencode, urlsplit, urlunsplit

import httpx

from .const import (
    DEFAULT_EVENT_CODES,
    DEFAULT_FFMPEG_BINARY,
    DEFAULT_MAX_AUDIO_SECONDS,
    DEFAULT_PORT,
    DEFAULT_RTSP_PORT,
    DEFAULT_SPEAKER_CONTENT_TYPE,
    DEFAULT_SPEAKER_ENDPOINT,
    DEFAULT_STREAM_SUBTYPE,
)
from .event_parser import (
    AmcrestEvent,
    parse_dahua_key_value,
    parse_event_chunk,
)

_LOGGER = logging.getLogger(__name__)


class AmcrestAD410Error(Exception):
    """Base error for the integration."""


class CannotConnect(AmcrestAD410Error):
    """Raised when the device cannot be reached."""


class InvalidAuth(AmcrestAD410Error):
    """Raised when credentials are rejected."""


@dataclass(slots=True)
class DeviceInfo:
    """Device metadata returned by the camera."""

    serial_number: str | None = None
    model: str | None = None
    hardware_version: str | None = None
    software_version: str | None = None


class AmcrestAD410Client:
    """Small async client for the Amcrest AD410 local API."""

    def __init__(
        self,
        *,
        host: str,
        username: str,
        password: str,
        port: int = DEFAULT_PORT,
        rtsp_port: int = DEFAULT_RTSP_PORT,
        use_ssl: bool = False,
        verify_ssl: bool = False,
    ) -> None:
        """Initialize the client."""

        self.host = host.strip()
        self.username = username
        self.password = password
        self.port = port
        self.rtsp_port = rtsp_port
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        scheme = "https" if use_ssl else "http"
        self.base_url = f"{scheme}://{self.host}:{self.port}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=httpx.DigestAuth(username, password),
            timeout=httpx.Timeout(15.0, connect=8.0, read=60.0),
            verify=verify_ssl,
            follow_redirects=True,
        )

    async def async_close(self) -> None:
        """Close the underlying HTTP session."""

        await self._client.aclose()

    def rtsp_url(self, subtype: int = DEFAULT_STREAM_SUBTYPE) -> str:
        """Return an authenticated RTSP URL for the camera stream."""

        user = quote(self.username, safe="")
        password = quote(self.password, safe="")
        query = urlencode({"channel": 1, "subtype": subtype})
        return (
            f"rtsp://{user}:{password}@{self.host}:{self.rtsp_port}"
            f"/cam/realmonitor?{query}"
        )

    async def async_get_device_info(self) -> DeviceInfo:
        """Fetch device identity information."""

        system = await self._async_get_text(
            "/cgi-bin/magicBox.cgi", params={"action": "getSystemInfo"}
        )
        system_values = parse_dahua_key_value(system)

        version_values: dict[str, str] = {}
        try:
            version = await self._async_get_text(
                "/cgi-bin/magicBox.cgi", params={"action": "getSoftwareVersion"}
            )
            version_values = parse_dahua_key_value(version)
        except AmcrestAD410Error:
            _LOGGER.debug("Software version endpoint was unavailable", exc_info=True)

        return DeviceInfo(
            serial_number=_first_present(
                system_values,
                "serialNumber",
                "SerialNo",
                "serialno",
                "deviceInfo.SerialNo",
            ),
            model=_first_present(
                system_values,
                "deviceType",
                "DeviceType",
                "model",
                "deviceInfo.DeviceType",
            ),
            hardware_version=_first_present(
                system_values, "hardwareVersion", "HardwareVersion"
            ),
            software_version=_first_present(
                version_values,
                "version",
                "Version",
                "softwareVersion",
                "SoftwareVersion",
            ),
        )

    async def async_snapshot(self) -> bytes:
        """Fetch a JPEG snapshot."""

        response = await self._async_request(
            "GET", "/cgi-bin/snapshot.cgi", params={"channel": 1}
        )
        content_type = response.headers.get("content-type", "")
        if response.content and (
            "image" in content_type.lower() or response.content.startswith(b"\xff\xd8")
        ):
            return response.content
        raise CannotConnect("Snapshot endpoint did not return an image")

    async def async_event_stream(
        self, codes: Iterable[str] | None = None
    ) -> AsyncIterator[AmcrestEvent]:
        """Yield events from eventManager.cgi."""

        code_list = list(codes or DEFAULT_EVENT_CODES)
        params = {
            "action": "attach",
            "codes": f"[{','.join(code_list)}]",
            "heartbeat": 5,
        }
        buffer = ""

        try:
            async with self._client.stream(
                "GET", "/cgi-bin/eventManager.cgi", params=params
            ) as response:
                if response.status_code in (401, 403):
                    raise InvalidAuth("Invalid Amcrest credentials")
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if not chunk:
                        continue
                    buffer += chunk.replace("\r\n", "\n").replace("\r", "\n")
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        for event in parse_event_chunk(line):
                            yield event
                    if len(buffer) > 65536:
                        buffer = buffer[-8192:]
        except httpx.HTTPStatusError as err:
            if err.response.status_code in (401, 403):
                raise InvalidAuth("Invalid Amcrest credentials") from err
            raise CannotConnect(str(err)) from err
        except httpx.HTTPError as err:
            raise CannotConnect(str(err)) from err

    async def async_post_speaker_audio(
        self,
        audio: bytes,
        *,
        endpoint: str = DEFAULT_SPEAKER_ENDPOINT,
        content_type: str = DEFAULT_SPEAKER_CONTENT_TYPE,
    ) -> None:
        """Post G.711 mu-law audio bytes to the doorbell speaker endpoint."""

        path, params = _split_endpoint(endpoint)
        response = await self._async_request(
            "POST",
            path,
            params=params,
            content=audio,
            headers={"Content-Type": content_type},
            request_timeout=httpx.Timeout(60.0, connect=8.0, read=60.0),
        )
        text = response.text.strip() if response.content else ""
        if text and "error" in text.lower():
            raise CannotConnect(f"Doorbell speaker endpoint returned: {text}")

    async def async_convert_media_to_mulaw(
        self,
        media: str,
        *,
        ffmpeg_binary: str = DEFAULT_FFMPEG_BINARY,
        max_seconds: int = DEFAULT_MAX_AUDIO_SECONDS,
    ) -> bytes:
        """Convert a media URL/path into raw 8 kHz mono G.711 mu-law bytes."""

        args = [
            ffmpeg_binary,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-t",
            str(max_seconds),
            "-i",
            media,
            "-vn",
            "-ac",
            "1",
            "-ar",
            "8000",
            "-f",
            "mulaw",
            "pipe:1",
        ]
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0 or not stdout:
            message = stderr.decode(errors="replace").strip() or "ffmpeg failed"
            raise CannotConnect(message)
        return stdout

    async def _async_get_text(
        self, path: str, *, params: dict[str, Any] | None = None
    ) -> str:
        """Run a GET request and return response text."""

        response = await self._async_request("GET", path, params=params)
        return response.text

    async def _async_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        content: bytes | None = None,
        headers: dict[str, str] | None = None,
        request_timeout: httpx.Timeout | None = None,
    ) -> httpx.Response:
        """Run an authenticated request and normalize common errors."""

        try:
            response = await self._client.request(
                method,
                path,
                params=params,
                content=content,
                headers=headers,
                timeout=request_timeout,
            )
        except httpx.ConnectError as err:
            raise CannotConnect(str(err)) from err
        except httpx.TimeoutException as err:
            raise CannotConnect(str(err)) from err
        except httpx.HTTPError as err:
            raise CannotConnect(str(err)) from err

        if response.status_code in (401, 403):
            raise InvalidAuth("Invalid Amcrest credentials")
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            raise CannotConnect(str(err)) from err
        return response


def _first_present(values: dict[str, str], *keys: str) -> str | None:
    """Return the first non-empty value from a dict."""

    for key in keys:
        value = values.get(key)
        if value:
            return value
    return None


def _split_endpoint(endpoint: str) -> tuple[str, dict[str, str]]:
    """Split a configurable CGI endpoint into path and query parameters."""

    parsed = urlsplit(endpoint)
    if parsed.scheme or parsed.netloc:
        endpoint = urlunsplit(("", "", parsed.path, parsed.query, ""))
        parsed = urlsplit(endpoint)
    params: dict[str, str] = {}
    if parsed.query:
        for pair in parsed.query.split("&"):
            if not pair:
                continue
            key, _, value = pair.partition("=")
            params[key] = value
    return parsed.path or endpoint, params
