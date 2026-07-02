"""Tests for the AD410 event parser."""

from custom_components.amcrest_ad410.event_parser import (
    csv_to_codes,
    parse_event_chunk,
    parse_event_line,
)


def test_parse_event_line_basic() -> None:
    """Parse a simple VideoMotion event."""

    event = parse_event_line("Code=VideoMotion;action=Start;index=0")

    assert event is not None
    assert event.code == "VideoMotion"
    assert event.action == "Start"
    assert event.index == "0"


def test_parse_event_line_with_extra_data() -> None:
    """Parse extra key/value fields when firmware includes them."""

    event = parse_event_line(
        "Code=SmartMotionHuman;action=Stop;index=0;Region=1;Confidence=89"
    )

    assert event is not None
    assert event.code == "SmartMotionHuman"
    assert event.data == {"Region": "1", "Confidence": "89"}


def test_parse_event_chunk_ignores_multipart_headers() -> None:
    """Ignore multipart headers and keep device event lines."""

    events = parse_event_chunk(
        "--boundary\r\n"
        "Content-Type: text/plain\r\n\r\n"
        "Code=CallNoAnswered;action=Pulse;index=0\r\n"
        "--boundary\r\n"
    )

    assert len(events) == 1
    assert events[0].code == "CallNoAnswered"
    assert events[0].action == "Pulse"


def test_csv_to_codes_falls_back_to_default() -> None:
    """Empty option strings fall back to defaults."""

    assert csv_to_codes(" , ", ["VideoMotion"]) == ["VideoMotion"]
    assert csv_to_codes("VideoMotion, HumanDetect", []) == [
        "VideoMotion",
        "HumanDetect",
    ]
