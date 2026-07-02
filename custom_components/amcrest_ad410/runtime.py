"""Runtime coordinator for one Amcrest AD410 config entry."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable
from contextlib import suppress
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.network import get_url

from .api import (
    AmcrestAD410Client,
    CannotConnect,
    DeviceInfo,
)
from .const import (
    ATTR_ACTION,
    ATTR_CODE,
    ATTR_DEVICE_ID,
    ATTR_INDEX,
    ATTR_RAW,
    ATTR_SOURCE,
    ATTR_TYPE,
    CONF_CAMERA_STREAMS,
    CONF_DOORBELL_CODES,
    CONF_FFMPEG_BINARY,
    CONF_HUMAN_CODES,
    CONF_MAX_AUDIO_SECONDS,
    CONF_MOTION_CODES,
    CONF_RTSP_PORT,
    CONF_SPEAKER_CONTENT_TYPE,
    CONF_SPEAKER_ENDPOINT,
    CONF_STREAM_SUBTYPE,
    CONF_USE_SSL,
    CONF_VERIFY_SSL,
    DEFAULT_DOORBELL_CODES,
    DEFAULT_FFMPEG_BINARY,
    DEFAULT_HUMAN_CODES,
    DEFAULT_MAX_AUDIO_SECONDS,
    DEFAULT_MOTION_CODES,
    DEFAULT_PORT,
    DEFAULT_RTSP_PORT,
    DEFAULT_SPEAKER_CONTENT_TYPE,
    DEFAULT_SPEAKER_ENDPOINT,
    DEFAULT_STREAM_SUBTYPE,
    DOMAIN,
    EVENT_AD410,
    EVENT_DOORBELL_PRESSED,
    EVENT_HUMAN_CLEARED,
    EVENT_HUMAN_DETECTED,
    EVENT_MOTION_CLEARED,
    EVENT_MOTION_DETECTED,
    MANUFACTURER,
    SIGNAL_EVENT,
    SIGNAL_STATE,
    START_ACTIONS,
    STOP_ACTIONS,
)
from .event_parser import AmcrestEvent, csv_to_codes
from .stream_profiles import normalize_stream_subtypes

_LOGGER = logging.getLogger(__name__)


class AmcrestAD410Runtime:
    """Manage the API client, push event stream, and current device state."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the runtime."""

        self.hass = hass
        self.entry = entry
        self.client = AmcrestAD410Client(
            host=entry.data[CONF_HOST],
            username=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            port=entry.data.get(CONF_PORT, DEFAULT_PORT),
            rtsp_port=entry.data.get(CONF_RTSP_PORT, DEFAULT_RTSP_PORT),
            use_ssl=entry.data.get(CONF_USE_SSL, False),
            verify_ssl=entry.data.get(CONF_VERIFY_SSL, False),
        )
        self.device_info = DeviceInfo()
        self.device_id: str | None = None
        self.motion_detected: bool | None = None
        self.human_detected: bool | None = None
        self.available = True
        self.last_event: AmcrestEvent | None = None
        self._event_task: asyncio.Task[None] | None = None
        self._stopped = asyncio.Event()

    @property
    def signal_event(self) -> str:
        """Dispatcher signal for event entities."""

        return f"{SIGNAL_EVENT}_{self.entry.entry_id}"

    @property
    def signal_state(self) -> str:
        """Dispatcher signal for stateful entities."""

        return f"{SIGNAL_STATE}_{self.entry.entry_id}"

    @property
    def name(self) -> str:
        """Return the configured device name."""

        return self.entry.title

    @property
    def unique_id_base(self) -> str:
        """Return a stable unique-id base."""

        return (
            self.device_info.serial_number
            or self.entry.unique_id
            or self.entry.entry_id
        )

    @property
    def entity_device_info(self) -> dict[str, Any]:
        """Return Home Assistant device info for entities."""

        return {
            "identifiers": {(DOMAIN, self.unique_id_base)},
            "manufacturer": MANUFACTURER,
            "model": self.device_info.model or "AD410",
            "name": self.name,
            "sw_version": self.device_info.software_version,
            "hw_version": self.device_info.hardware_version,
            "configuration_url": self.client.base_url,
        }

    async def async_setup(self) -> None:
        """Fetch metadata and register the device."""

        self.device_info = await self.client.async_get_device_info()
        device_registry = dr.async_get(self.hass)
        device = device_registry.async_get_or_create(
            config_entry_id=self.entry.entry_id,
            identifiers={(DOMAIN, self.unique_id_base)},
            manufacturer=MANUFACTURER,
            model=self.device_info.model or "AD410",
            name=self.name,
            sw_version=self.device_info.software_version,
            hw_version=self.device_info.hardware_version,
            configuration_url=self.client.base_url,
        )
        self.device_id = device.id

    async def async_start(self) -> None:
        """Start the persistent event stream."""

        self._stopped.clear()
        if self._event_task is None or self._event_task.done():
            self._event_task = self.hass.async_create_task(
                self._async_event_loop(), name=f"{DOMAIN}_{self.entry.entry_id}_events"
            )

    async def async_stop(self) -> None:
        """Stop background work and close the API client."""

        self._stopped.set()
        if self._event_task is not None:
            self._event_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._event_task
            self._event_task = None
        await self.client.async_close()

    async def async_snapshot(self) -> bytes:
        """Fetch a camera snapshot."""

        return await self.client.async_snapshot()

    def default_stream_subtype(self) -> int:
        """Return the RTSP subtype used by the primary camera entity."""

        return int(
            self.entry.options.get(
                CONF_STREAM_SUBTYPE,
                self.entry.data.get(CONF_STREAM_SUBTYPE, DEFAULT_STREAM_SUBTYPE),
            )
        )

    def camera_stream_subtypes(self) -> list[int]:
        """Return enabled camera stream subtypes with the default stream first."""

        default_subtype = self.default_stream_subtype()
        subtypes = normalize_stream_subtypes(
            self.entry.options.get(CONF_CAMERA_STREAMS), [default_subtype]
        )
        if default_subtype in subtypes:
            subtypes.remove(default_subtype)
        return [default_subtype, *subtypes]

    def rtsp_url(self, subtype: int | None = None) -> str:
        """Return the configured RTSP stream URL."""

        if subtype is None:
            subtype = self.default_stream_subtype()
        return self.client.rtsp_url(subtype)

    async def async_play_microphone_stream(
        self,
        *,
        media_player_entity_id: str,
        subtype: int | None = None,
        media_content_type: str = "video",
    ) -> None:
        """Ask a Home Assistant media player to play the doorbell RTSP stream."""

        await self.hass.services.async_call(
            "media_player",
            "play_media",
            {
                "entity_id": media_player_entity_id,
                "media_content_id": self.rtsp_url(subtype),
                "media_content_type": media_content_type,
            },
            blocking=True,
        )

    async def async_play_audio_on_doorbell(
        self,
        *,
        media_content_id: str,
        media_content_type: str | None = None,
        duration: int | None = None,
    ) -> None:
        """Convert a HA media source/URL and post it to the doorbell speaker."""

        media = await self._async_resolve_media(media_content_id, media_content_type)
        ffmpeg_binary = self.entry.options.get(
            CONF_FFMPEG_BINARY, DEFAULT_FFMPEG_BINARY
        )
        max_seconds = int(
            duration
            or self.entry.options.get(CONF_MAX_AUDIO_SECONDS, DEFAULT_MAX_AUDIO_SECONDS)
        )
        audio = await self.client.async_convert_media_to_mulaw(
            media,
            ffmpeg_binary=ffmpeg_binary,
            max_seconds=max_seconds,
        )
        await self.client.async_post_speaker_audio(
            audio,
            endpoint=self.entry.options.get(
                CONF_SPEAKER_ENDPOINT, DEFAULT_SPEAKER_ENDPOINT
            ),
            content_type=self.entry.options.get(
                CONF_SPEAKER_CONTENT_TYPE, DEFAULT_SPEAKER_CONTENT_TYPE
            ),
        )

    async def _async_resolve_media(
        self, media_content_id: str, media_content_type: str | None
    ) -> str:
        """Resolve Home Assistant media-source IDs to URLs usable by ffmpeg."""

        if media_content_id.startswith(("http://", "https://", "rtsp://", "file:")):
            return media_content_id

        if media_content_id.startswith("/"):
            base_url = get_url(self.hass, prefer_external=False, allow_internal=True)
            return f"{base_url.rstrip('/')}{media_content_id}"

        if media_content_id.startswith("media-source://"):
            from homeassistant.components import media_source

            resolved = await media_source.async_resolve_media(
                self.hass, media_content_id, self.entry.entry_id
            )
            url = resolved.url
            if url.startswith("/"):
                base_url = get_url(
                    self.hass, prefer_external=False, allow_internal=True
                )
                return f"{base_url.rstrip('/')}{url}"
            return url

        return media_content_id

    async def _async_event_loop(self) -> None:
        """Maintain the event stream with backoff reconnects."""

        delay = 1
        while not self._stopped.is_set():
            try:
                codes = self._event_codes()
                async for event in self.client.async_event_stream(codes):
                    delay = 1
                    self.available = True
                    self._handle_event(event)
                    if self._stopped.is_set():
                        break
            except asyncio.CancelledError:
                raise
            except CannotConnect as err:
                self.available = False
                async_dispatcher_send(self.hass, self.signal_state)
                _LOGGER.warning(
                    "AD410 event stream disconnected; reconnecting in %s seconds: %s",
                    delay,
                    err,
                )
            except Exception:
                self.available = False
                async_dispatcher_send(self.hass, self.signal_state)
                _LOGGER.exception(
                    "Unexpected AD410 event stream error; reconnecting in %s seconds",
                    delay,
                )

            with suppress(TimeoutError):
                await asyncio.wait_for(self._stopped.wait(), timeout=delay)
            delay = min(delay * 2, 60)

    @callback
    def _handle_event(self, event: AmcrestEvent) -> None:
        """Map a raw device event into HA events and state."""

        event_type = self._event_type(event)
        if event_type is None:
            _LOGGER.debug("Ignoring unmapped AD410 event: %s", event.raw)
            return

        self.last_event = event
        if event_type == EVENT_MOTION_DETECTED:
            self.motion_detected = True
        elif event_type == EVENT_MOTION_CLEARED:
            self.motion_detected = False
        elif event_type == EVENT_HUMAN_DETECTED:
            self.human_detected = True
        elif event_type == EVENT_HUMAN_CLEARED:
            self.human_detected = False

        event_data = {
            ATTR_DEVICE_ID: self.device_id,
            ATTR_TYPE: event_type,
            ATTR_CODE: event.code,
            ATTR_ACTION: event.action,
            ATTR_INDEX: event.index,
            ATTR_RAW: event.raw,
            ATTR_SOURCE: self.name,
            **event.data,
        }
        self.hass.bus.async_fire(EVENT_AD410, event_data)
        async_dispatcher_send(self.hass, self.signal_event, event_type, event_data)
        async_dispatcher_send(self.hass, self.signal_state)

    def _event_type(self, event: AmcrestEvent) -> str | None:
        """Return the HA event type represented by a raw device event."""

        code = event.code.lower()
        action = event.action.lower()
        if code in _lower_codes(self._doorbell_codes()) and action not in STOP_ACTIONS:
            return EVENT_DOORBELL_PRESSED
        if code in _lower_codes(self._motion_codes()):
            if action in START_ACTIONS:
                return EVENT_MOTION_DETECTED
            if action in STOP_ACTIONS:
                return EVENT_MOTION_CLEARED
        if code in _lower_codes(self._human_codes()):
            if action in START_ACTIONS:
                return EVENT_HUMAN_DETECTED
            if action in STOP_ACTIONS:
                return EVENT_HUMAN_CLEARED
        return None

    def _event_codes(self) -> list[str]:
        """Return all event codes to subscribe to."""

        return sorted(
            set(self._doorbell_codes() + self._motion_codes() + self._human_codes())
        )

    def _doorbell_codes(self) -> list[str]:
        return csv_to_codes(
            self.entry.options.get(CONF_DOORBELL_CODES), DEFAULT_DOORBELL_CODES
        )

    def _motion_codes(self) -> list[str]:
        return csv_to_codes(
            self.entry.options.get(CONF_MOTION_CODES), DEFAULT_MOTION_CODES
        )

    def _human_codes(self) -> list[str]:
        return csv_to_codes(
            self.entry.options.get(CONF_HUMAN_CODES), DEFAULT_HUMAN_CODES
        )


def _lower_codes(codes: Iterable[str]) -> set[str]:
    """Return normalized code names."""

    return {code.lower() for code in codes}
