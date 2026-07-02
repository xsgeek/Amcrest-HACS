"""Pure parsers for Dahua/Amcrest event stream messages."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
import re

EVENT_LINE_RE = re.compile(
    r"Code=(?P<code>[^;\r\n]+);action=(?P<action>[^;\r\n]+);index=(?P<index>[^;\r\n]+)(?P<rest>[^\r\n]*)"
)


@dataclass(slots=True)
class AmcrestEvent:
    """A parsed Dahua/Amcrest event stream item."""

    code: str
    action: str
    index: str
    raw: str
    data: dict[str, str] = field(default_factory=dict)


def parse_dahua_key_value(text: str) -> dict[str, str]:
    """Parse simple Dahua CGI key/value responses."""

    values: dict[str, str] = {}
    for raw_line in text.replace("\r", "\n").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def parse_event_line(line: str) -> AmcrestEvent | None:
    """Parse one text line from eventManager.cgi."""

    match = EVENT_LINE_RE.search(line)
    if match is None:
        return None

    data: dict[str, str] = {}
    rest = match.group("rest").strip()
    if rest.startswith(";"):
        for part in rest[1:].split(";"):
            if not part or "=" not in part:
                continue
            key, value = part.split("=", 1)
            data[key.strip()] = value.strip()

    return AmcrestEvent(
        code=match.group("code").strip(),
        action=match.group("action").strip(),
        index=match.group("index").strip(),
        raw=match.group(0).strip(),
        data=data,
    )


def parse_event_chunk(chunk: str) -> list[AmcrestEvent]:
    """Parse all complete event lines from a text chunk."""

    events: list[AmcrestEvent] = []
    for line in chunk.replace("\r", "\n").splitlines():
        event = parse_event_line(line)
        if event is not None:
            events.append(event)
    return events


def csv_to_codes(value: str | Iterable[str] | None, default: Iterable[str]) -> list[str]:
    """Normalize a comma-separated option into event code strings."""

    if value is None:
        return list(default)
    if isinstance(value, str):
        parts = value.split(",")
    else:
        parts = list(value)
    codes = [part.strip() for part in parts if part and part.strip()]
    return codes or list(default)


def codes_to_csv(codes: Iterable[str]) -> str:
    """Convert event code strings to a stable comma-separated option value."""

    return ",".join(dict.fromkeys(code.strip() for code in codes if code.strip()))
