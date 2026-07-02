"""Tests for AD410 device automation triggers."""

import pytest
from custom_components.amcrest_ad410.const import (
    DOMAIN,
    EVENT_DOORBELL_PRESSED,
    EVENT_HUMAN_CLEARED,
    EVENT_HUMAN_DETECTED,
    EVENT_MOTION_CLEARED,
    EVENT_MOTION_DETECTED,
)
from custom_components.amcrest_ad410.device_trigger import TRIGGER_SCHEMA
from homeassistant.const import CONF_DEVICE_ID, CONF_DOMAIN, CONF_PLATFORM, CONF_TYPE


@pytest.mark.parametrize(
    "trigger_type",
    [
        EVENT_DOORBELL_PRESSED,
        EVENT_MOTION_DETECTED,
        EVENT_MOTION_CLEARED,
        EVENT_HUMAN_DETECTED,
        EVENT_HUMAN_CLEARED,
    ],
)
def test_trigger_schema_accepts_planned_trigger_types(trigger_type: str) -> None:
    """Accept every AD410 trigger type tracked in the project checklist."""

    trigger = TRIGGER_SCHEMA(
        {
            CONF_PLATFORM: "device",
            CONF_DOMAIN: DOMAIN,
            CONF_DEVICE_ID: "device-id",
            CONF_TYPE: trigger_type,
        }
    )

    assert trigger[CONF_TYPE] == trigger_type
