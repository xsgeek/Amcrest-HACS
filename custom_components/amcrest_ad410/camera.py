"""Camera entity for the Amcrest AD410 integration."""

from __future__ import annotations

from homeassistant.components.camera import Camera

try:
    from homeassistant.components.camera import CameraEntityFeature
except ImportError:  # pragma: no cover - older HA compatibility
    CameraEntityFeature = None  # type: ignore[assignment]
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .runtime import AmcrestAD410Runtime
from .stream_profiles import stream_profile_name


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the AD410 camera."""

    runtime: AmcrestAD410Runtime = entry.runtime_data
    async_add_entities(
        [
            AmcrestAD410Camera(runtime, subtype=subtype, primary=index == 0)
            for index, subtype in enumerate(runtime.camera_stream_subtypes())
        ]
    )


class AmcrestAD410Camera(Camera):
    """Camera entity exposing AD410 RTSP and snapshots."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    if CameraEntityFeature is not None:
        _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self, runtime: AmcrestAD410Runtime, *, subtype: int, primary: bool
    ) -> None:
        """Initialize the camera."""

        super().__init__()
        self._runtime = runtime
        self._subtype = subtype
        profile_name = stream_profile_name(subtype)
        self._attr_name = None if primary else profile_name
        self._attr_unique_id = (
            f"{runtime.unique_id_base}_camera"
            if primary
            else f"{runtime.unique_id_base}_camera_subtype_{subtype}"
        )
        self._attr_extra_state_attributes = {
            "rtsp_subtype": subtype,
            "stream_profile": profile_name,
        }
        self._attr_device_info = runtime.entity_device_info

    @property
    def available(self) -> bool:
        """Return whether the device is available."""

        return self._runtime.available

    async def stream_source(self) -> str:
        """Return the RTSP stream source."""

        return self._runtime.rtsp_url(self._subtype)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""

        return await self._runtime.async_snapshot()
