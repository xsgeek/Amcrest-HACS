"""Helpers for AD410 RTSP stream profile options."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

STREAM_PROFILE_OPTIONS = {
    "0": "Main stream (subtype 0)",
    "1": "Sub stream (subtype 1)",
    "2": "Sub stream 2 (subtype 2)",
}


def normalize_stream_subtypes(
    value: Iterable[Any] | str | int | None,
    default: Iterable[Any],
) -> list[int]:
    """Normalize a stored stream-profile option into RTSP subtype integers."""

    raw_values: Iterable[Any]
    if value is None:
        raw_values = default
    elif isinstance(value, str):
        raw_values = value.split(",")
    elif isinstance(value, int):
        raw_values = [value]
    else:
        raw_values = value

    subtypes: list[int] = []
    for raw_value in raw_values:
        try:
            subtype = int(str(raw_value).strip())
        except (TypeError, ValueError):
            continue
        if subtype < 0 or subtype in subtypes:
            continue
        subtypes.append(subtype)

    if subtypes:
        return subtypes
    return normalize_stream_subtypes(default, [0])


def stream_subtypes_to_options(subtypes: Iterable[int]) -> list[str]:
    """Convert RTSP subtype integers to option values for HA multi-select."""

    return [str(subtype) for subtype in normalize_stream_subtypes(subtypes, [0])]


def stream_profile_name(subtype: int) -> str:
    """Return a user-facing stream profile name."""

    if subtype == 0:
        return "Main stream"
    if subtype == 1:
        return "Sub stream"
    return f"Sub stream {subtype}"
