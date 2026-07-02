"""Binary sensors for the Amcrest AD410 integration."""

from __future__ import annotations

from collections.abc import Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .runtime import AmcrestAD410Runtime


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AD410 binary sensors."""

    runtime: AmcrestAD410Runtime = entry.runtime_data
    async_add_entities(
        [
            AmcrestAD410StateBinarySensor(
                runtime,
                key="motion",
                name="Motion",
                device_class=BinarySensorDeviceClass.MOTION,
                value_fn=lambda coordinator: coordinator.motion_detected,
            ),
            AmcrestAD410StateBinarySensor(
                runtime,
                key="human",
                name="Human",
                device_class=BinarySensorDeviceClass.OCCUPANCY,
                value_fn=lambda coordinator: coordinator.human_detected,
            ),
        ]
    )


class AmcrestAD410StateBinarySensor(BinarySensorEntity):
    """Binary sensor backed by the AD410 event stream."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        runtime: AmcrestAD410Runtime,
        *,
        key: str,
        name: str,
        device_class: BinarySensorDeviceClass,
        value_fn: Callable[[AmcrestAD410Runtime], bool | None],
    ) -> None:
        """Initialize the binary sensor."""

        self._runtime = runtime
        self._value_fn = value_fn
        self._attr_name = name
        self._attr_unique_id = f"{runtime.unique_id_base}_{key}"
        self._attr_device_class = device_class
        self._attr_device_info = runtime.entity_device_info

    @property
    def available(self) -> bool:
        """Return whether the event stream is connected."""

        return self._runtime.available

    @property
    def is_on(self) -> bool | None:
        """Return the latest known state."""

        return self._value_fn(self._runtime)

    async def async_added_to_hass(self) -> None:
        """Subscribe to runtime state updates."""

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._runtime.signal_state, self._async_handle_update
            )
        )

    @callback
    def _async_handle_update(self) -> None:
        """Write the updated state."""

        self.async_write_ha_state()
