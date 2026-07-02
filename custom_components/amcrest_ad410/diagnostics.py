"""Diagnostics for the Amcrest AD410 integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .runtime import AmcrestAD410Runtime

TO_REDACT = {CONF_USERNAME, CONF_PASSWORD}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    runtime: AmcrestAD410Runtime | None = hass.data[DOMAIN].get(entry.entry_id)
    data = {
        "entry": {
            key: ("**REDACTED**" if key in TO_REDACT else value)
            for key, value in entry.data.items()
            if key != CONF_PASSWORD
        },
        "host": entry.data.get(CONF_HOST),
        "options": dict(entry.options),
    }
    if runtime is not None:
        data["device"] = {
            "device_id": runtime.device_id,
            "serial_number": runtime.device_info.serial_number,
            "model": runtime.device_info.model,
            "software_version": runtime.device_info.software_version,
            "available": runtime.available,
            "motion_detected": runtime.motion_detected,
            "human_detected": runtime.human_detected,
        }
        if runtime.last_event is not None:
            data["last_event"] = {
                "code": runtime.last_event.code,
                "action": runtime.last_event.action,
                "index": runtime.last_event.index,
                "raw": runtime.last_event.raw,
            }
    return data
