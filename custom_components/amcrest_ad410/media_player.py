"""Media player entity for the AD410 speaker."""

from __future__ import annotations

from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
try:
    from homeassistant.components.media_player.const import MediaType
except ImportError:  # pragma: no cover - older HA compatibility
    from homeassistant.const import MediaType  # type: ignore[assignment]
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .runtime import AmcrestAD410Runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AD410 speaker entity."""

    runtime: AmcrestAD410Runtime = entry.runtime_data
    async_add_entities([AmcrestAD410Speaker(runtime)])


class AmcrestAD410Speaker(MediaPlayerEntity):
    """Best-effort media player for the AD410 doorbell speaker."""

    _attr_has_entity_name = True
    _attr_name = "Speaker"
    _attr_should_poll = False
    _attr_supported_features = MediaPlayerEntityFeature.PLAY_MEDIA

    def __init__(self, runtime: AmcrestAD410Runtime) -> None:
        """Initialize the media player."""

        self._runtime = runtime
        self._attr_unique_id = f"{runtime.unique_id_base}_speaker"
        self._attr_device_info = runtime.entity_device_info
        self._attr_state = MediaPlayerState.IDLE

    @property
    def available(self) -> bool:
        """Return whether the device is available."""

        return self._runtime.available

    async def async_play_media(
        self,
        media_type: MediaType | str,
        media_id: str,
        enqueue: Any | None = None,
        announce: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Play media on the AD410 speaker."""

        self._attr_state = MediaPlayerState.PLAYING
        self.async_write_ha_state()
        try:
            await self._runtime.async_play_audio_on_doorbell(
                media_content_id=media_id,
                media_content_type=str(media_type),
            )
        finally:
            self._attr_state = MediaPlayerState.IDLE
            self.async_write_ha_state()
