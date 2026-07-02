"""Tests for AD410 stream profile helpers."""

from custom_components.amcrest_ad410.stream_profiles import (
    normalize_stream_subtypes,
    stream_profile_name,
    stream_subtypes_to_options,
)


def test_normalize_stream_subtypes_preserves_order_and_dedupes() -> None:
    """Normalize HA option values to unique RTSP subtypes."""

    assert normalize_stream_subtypes(["1", "0", "1", "2"], [0]) == [1, 0, 2]


def test_normalize_stream_subtypes_handles_csv_and_invalid_values() -> None:
    """Ignore invalid subtype values and fall back when needed."""

    assert normalize_stream_subtypes("2, bad, -1, 0", [1]) == [2, 0]
    assert normalize_stream_subtypes(["bad"], [1]) == [1]


def test_stream_subtypes_to_options() -> None:
    """Convert subtypes back to HA multi-select option strings."""

    assert stream_subtypes_to_options([0, 2]) == ["0", "2"]


def test_stream_profile_name() -> None:
    """Name main and sub streams for camera entities."""

    assert stream_profile_name(0) == "Main stream"
    assert stream_profile_name(1) == "Sub stream"
    assert stream_profile_name(2) == "Sub stream 2"
