"""Config flow for the Amcrest AD410 integration."""

from __future__ import annotations

from typing import Any

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .api import AmcrestAD410Client, CannotConnect, InvalidAuth
from .const import (
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
    DEFAULT_CAMERA_STREAMS,
    DEFAULT_DOORBELL_CODES,
    DEFAULT_FFMPEG_BINARY,
    DEFAULT_HUMAN_CODES,
    DEFAULT_MAX_AUDIO_SECONDS,
    DEFAULT_MOTION_CODES,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_RTSP_PORT,
    DEFAULT_SPEAKER_CONTENT_TYPE,
    DEFAULT_SPEAKER_ENDPOINT,
    DEFAULT_STREAM_SUBTYPE,
    DOMAIN,
)
from .event_parser import codes_to_csv
from .stream_profiles import (
    STREAM_PROFILE_OPTIONS,
    normalize_stream_subtypes,
    stream_subtypes_to_options,
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input and return device metadata."""

    client = AmcrestAD410Client(
        host=data[CONF_HOST],
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        port=data[CONF_PORT],
        rtsp_port=data[CONF_RTSP_PORT],
        use_ssl=data[CONF_USE_SSL],
        verify_ssl=data[CONF_VERIFY_SSL],
    )
    try:
        info = await client.async_get_device_info()
    finally:
        await client.async_close()

    return {
        "serial_number": info.serial_number or data[CONF_HOST],
        "model": info.model or "AD410",
    }


class AmcrestAD410ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Amcrest AD410."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""

        return AmcrestAD410OptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["serial_number"])
                self._abort_if_unique_id_configured(
                    updates={CONF_HOST: user_input[CONF_HOST]}
                )
                title = user_input.get(CONF_NAME) or (
                    f"{DEFAULT_NAME} {user_input[CONF_HOST]}"
                )
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_RTSP_PORT, default=DEFAULT_RTSP_PORT): int,
                    vol.Optional(CONF_USE_SSL, default=False): bool,
                    vol.Optional(CONF_VERIFY_SSL, default=False): bool,
                    vol.Optional(
                        CONF_STREAM_SUBTYPE, default=DEFAULT_STREAM_SUBTYPE
                    ): int,
                }
            ),
            errors=errors,
        )


class AmcrestAD410OptionsFlow(config_entries.OptionsFlow):
    """Handle Amcrest AD410 options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""

        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage integration options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options
        default_stream_subtype = int(
            options.get(
                CONF_STREAM_SUBTYPE,
                self.config_entry.data.get(CONF_STREAM_SUBTYPE, DEFAULT_STREAM_SUBTYPE),
            )
        )
        camera_streams = stream_subtypes_to_options(
            normalize_stream_subtypes(
                options.get(CONF_CAMERA_STREAMS),
                [default_stream_subtype]
                if default_stream_subtype >= 0
                else DEFAULT_CAMERA_STREAMS,
            )
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DOORBELL_CODES,
                        default=options.get(
                            CONF_DOORBELL_CODES, codes_to_csv(DEFAULT_DOORBELL_CODES)
                        ),
                    ): str,
                    vol.Optional(
                        CONF_MOTION_CODES,
                        default=options.get(
                            CONF_MOTION_CODES, codes_to_csv(DEFAULT_MOTION_CODES)
                        ),
                    ): str,
                    vol.Optional(
                        CONF_HUMAN_CODES,
                        default=options.get(
                            CONF_HUMAN_CODES, codes_to_csv(DEFAULT_HUMAN_CODES)
                        ),
                    ): str,
                    vol.Optional(
                        CONF_SPEAKER_ENDPOINT,
                        default=options.get(
                            CONF_SPEAKER_ENDPOINT, DEFAULT_SPEAKER_ENDPOINT
                        ),
                    ): str,
                    vol.Optional(
                        CONF_SPEAKER_CONTENT_TYPE,
                        default=options.get(
                            CONF_SPEAKER_CONTENT_TYPE, DEFAULT_SPEAKER_CONTENT_TYPE
                        ),
                    ): str,
                    vol.Optional(
                        CONF_FFMPEG_BINARY,
                        default=options.get(CONF_FFMPEG_BINARY, DEFAULT_FFMPEG_BINARY),
                    ): str,
                    vol.Optional(
                        CONF_MAX_AUDIO_SECONDS,
                        default=options.get(
                            CONF_MAX_AUDIO_SECONDS, DEFAULT_MAX_AUDIO_SECONDS
                        ),
                    ): int,
                    vol.Optional(
                        CONF_STREAM_SUBTYPE,
                        default=options.get(
                            CONF_STREAM_SUBTYPE,
                            self.config_entry.data.get(
                                CONF_STREAM_SUBTYPE, DEFAULT_STREAM_SUBTYPE
                            ),
                        ),
                    ): int,
                    vol.Optional(
                        CONF_CAMERA_STREAMS,
                        default=camera_streams,
                    ): cv.multi_select(STREAM_PROFILE_OPTIONS),
                }
            ),
        )
