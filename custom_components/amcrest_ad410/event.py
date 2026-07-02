"""Event entities for the Amcrest AD410 integration."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from homeassistant.components.event import EventDeviceClass, EventEntity
try:
    from homeassistant.components.event import DoorbellEventType
except ImportError:  # pragma: no cover - older HA compatibility
    DoorbellEventType = None  # type: ignore[assignment]
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    EVENT_DOORBELL_PRESSED,
    EVENT_HUMAN_CLEARED,
    EVENT_HUMAN_DETECTED,
    EVENT_MOTION_CLEARED,
    EVENT_MOTION_DETECTED,
)
from .runtime import AmcrestAD410Runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AD410 event entities."""

    runtime: AmcrestAD410Runtime = entry.runtime_data
    ring_type = DoorbellEventType.RING if DoorbellEventType is not None else "ring"
    async_add_entities(
        [
            AmcrestAD410EventEntity(
                runtime,
                key="doorbell",
                name="Doorbell",
                device_class=EventDeviceClass.DOORBELL,
                event_types=[ring_type],
                event_map={EVENT_DOORBELL_PRESSED: ring_type},
            ),
            AmcrestAD410EventEntity(
                runtime,
                key="motion_event",
                name="Motion event",
                device_class=EventDeviceClass.MOTION,
                event_types=[EVENT_MOTION_DETECTED, EVENT_MOTION_CLEARED],
                event_map={
                    EVENT_MOTION_DETECTED: EVENT_MOTION_DETECTED,
                    EVENT_MOTION_CLEARED: EVENT_MOTION_CLEARED,
                },
            ),
            AmcrestAD410EventEntity(
                runtime,
                key="human_event",
                name="Human event",
                device_class=EventDeviceClass.MOTION,
                event_types=[EVENT_HUMAN_DETECTED, EVENT_HUMAN_CLEARED],
                event_map={
                    EVENT_HUMAN_DETECTED: EVENT_HUMAN_DETECTED,
                    EVENT_HUMAN_CLEARED: EVENT_HUMAN_CLEARED,
                },
            ),
        ]
    )


class AmcrestAD410EventEntity(EventEntity):
    """A stateless AD410 event entity."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        runtime: AmcrestAD410Runtime,
        *,
        key: str,
        name: str,
        device_class: EventDeviceClass,
        event_types: Iterable[str],
        event_map: dict[str, str],
    ) -> None:
        """Initialize the event entity."""

        self._runtime = runtime
        self._event_map = event_map
        self._attr_name = name
        self._attr_unique_id = f"{runtime.unique_id_base}_{key}"
        self._attr_device_class = device_class
        self._attr_event_types = list(event_types)
        self._attr_device_info = runtime.entity_device_info

    @property
    def available(self) -> bool:
        """Return whether the event stream is connected."""

        return self._runtime.available

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime event updates."""

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._runtime.signal_event, self._async_handle_event
            )
        )

    @callback
    def _async_handle_event(self, event_type: str, event_data: dict[str, Any]) -> None:
        """Trigger the entity event if this entity owns the type."""

        mapped_type = self._event_map.get(event_type)
        if mapped_type is None:
            return
        self._trigger_event(mapped_type, event_data)
        self.async_write_ha_state()
