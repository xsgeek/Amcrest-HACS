"""Home Assistant integration for the Amcrest AD410 video doorbell."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from .const import (
    DOMAIN,
    FIELD_DEVICE_ID,
    FIELD_DURATION,
    FIELD_ENTRY_ID,
    FIELD_MEDIA_CONTENT_ID,
    FIELD_MEDIA_CONTENT_TYPE,
    FIELD_MEDIA_PLAYER_ENTITY_ID,
    FIELD_SUBTYPE,
    PLATFORMS,
    SERVICE_PLAY_AUDIO_ON_DOORBELL,
    SERVICE_PLAY_MICROPHONE_STREAM,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall

    from .runtime import AmcrestAD410Runtime

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up integration-level services."""

    hass.data.setdefault(DOMAIN, {})
    _async_register_services(hass)
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Set up an Amcrest AD410 config entry."""

    from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError

    from .api import CannotConnect, InvalidAuth
    from .runtime import AmcrestAD410Runtime

    runtime = AmcrestAD410Runtime(hass, entry)
    try:
        await runtime.async_setup()
    except InvalidAuth as err:
        raise HomeAssistantError("Invalid Amcrest AD410 credentials") from err
    except CannotConnect as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = runtime
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await runtime.async_start()

    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> bool:
    """Unload an Amcrest AD410 config entry."""

    runtime = entry.runtime_data
    await runtime.async_stop()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def _async_reload_entry(
    hass: HomeAssistant, entry: ConfigEntry
) -> None:
    """Reload the integration after options change."""

    await hass.config_entries.async_reload(entry.entry_id)


def _async_register_services(hass: HomeAssistant) -> None:
    """Register integration services once."""

    import voluptuous as vol

    import homeassistant.helpers.config_validation as cv

    play_microphone_schema = vol.Schema(
        {
            vol.Optional(FIELD_DEVICE_ID): cv.string,
            vol.Optional(FIELD_ENTRY_ID): cv.string,
            vol.Required(FIELD_MEDIA_PLAYER_ENTITY_ID): cv.entity_id,
            vol.Optional(FIELD_MEDIA_CONTENT_TYPE, default="video"): cv.string,
            vol.Optional(FIELD_SUBTYPE): vol.Coerce(int),
        }
    )
    play_audio_schema = vol.Schema(
        {
            vol.Optional(FIELD_DEVICE_ID): cv.string,
            vol.Optional(FIELD_ENTRY_ID): cv.string,
            vol.Required(FIELD_MEDIA_CONTENT_ID): cv.string,
            vol.Optional(FIELD_MEDIA_CONTENT_TYPE): cv.string,
            vol.Optional(FIELD_DURATION): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=300)
            ),
        }
    )

    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_MICROPHONE_STREAM):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_MICROPHONE_STREAM,
            _handle_play_microphone_stream,
            schema=play_microphone_schema,
        )
    if not hass.services.has_service(DOMAIN, SERVICE_PLAY_AUDIO_ON_DOORBELL):
        hass.services.async_register(
            DOMAIN,
            SERVICE_PLAY_AUDIO_ON_DOORBELL,
            _handle_play_audio_on_doorbell,
            schema=play_audio_schema,
        )


async def _handle_play_microphone_stream(call: ServiceCall) -> None:
    """Handle the play microphone stream service."""

    runtime = _runtime_from_service_call(call.hass, call.data)
    await runtime.async_play_microphone_stream(
        media_player_entity_id=call.data[FIELD_MEDIA_PLAYER_ENTITY_ID],
        subtype=call.data.get(FIELD_SUBTYPE),
        media_content_type=call.data[FIELD_MEDIA_CONTENT_TYPE],
    )


async def _handle_play_audio_on_doorbell(call: ServiceCall) -> None:
    """Handle the doorbell speaker service."""

    runtime = _runtime_from_service_call(call.hass, call.data)
    await runtime.async_play_audio_on_doorbell(
        media_content_id=call.data[FIELD_MEDIA_CONTENT_ID],
        media_content_type=call.data.get(FIELD_MEDIA_CONTENT_TYPE),
        duration=call.data.get(FIELD_DURATION),
    )


def _runtime_from_service_call(
    hass: HomeAssistant, data: dict[str, Any]
) -> AmcrestAD410Runtime:
    """Resolve a runtime from service data."""

    from homeassistant.const import CONF_DEVICE_ID
    from homeassistant.exceptions import HomeAssistantError

    runtimes: dict[str, AmcrestAD410Runtime] = hass.data.get(DOMAIN, {})
    if not runtimes:
        raise HomeAssistantError("No Amcrest AD410 devices are configured")

    entry_id = data.get(FIELD_ENTRY_ID)
    if entry_id:
        if entry_id in runtimes:
            return runtimes[entry_id]
        raise HomeAssistantError(f"Unknown Amcrest AD410 entry_id: {entry_id}")

    device_id = data.get(FIELD_DEVICE_ID) or data.get(CONF_DEVICE_ID)
    if device_id:
        for runtime in runtimes.values():
            if runtime.device_id == device_id:
                return runtime
        raise HomeAssistantError(f"Unknown Amcrest AD410 device_id: {device_id}")

    if len(runtimes) == 1:
        return next(iter(runtimes.values()))
    raise HomeAssistantError("Specify device_id or entry_id for this service call")
