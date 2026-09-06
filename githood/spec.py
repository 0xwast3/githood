"""Parse a one-page spec file into the handful of facts the scaffolder needs.

The format is deliberately boring: a title, some `key: value` lines and a
`rules:` list. Anything githood cannot map to a field is kept in `extra` and
copied into the generated README, so nothing a human wrote is silently lost.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

BROKERS = ("robinhood", "alpaca", "paper")

SLUG_RE = re.compile(r"[^a-z0-9]+")


class SpecError(ValueError):
    """Raised when a spec cannot be turned into a repo."""


def slugify(text: str) -> str:
    slug = SLUG_RE.sub("-", text.strip().lower()).strip("-")
    if not slug:
        raise SpecError("the project name is empty after slugifying it")
    return slug


@dataclass
class Spec:
    name: str
    broker: str = "paper"
    symbols: tuple = ("AAPL",)
    timeframe: str = "5m"
    max_position: float = 0.10
    stop_loss: float = 0.02
    cash: float = 10000.0
    rules: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)

    @property
    def slug(self) -> str:
        return slugify(self.name)

    @property
    def module(self) -> str:
        return self.slug.replace("-", "_")

    def summary(self) -> str:
        return (
            f"{self.name} · {self.broker} · {len(self.symbols)} symbols · "
            f"{self.timeframe} · max {self.max_position:.0%} per position"
        )


def _parse_number(key: str, raw: str) -> float:
    text = raw.strip().rstrip("%")
    try:
        value = float(text)
    except ValueError as exc:  # pragma: no cover - message is the point
        raise SpecError(f"{key} must be a number, got {raw!r}") from exc
    if raw.strip().endswith("%"):
        value /= 100.0
    return value


def parse(text: str) -> Spec:
    """Turn spec text into a :class:`Spec`, or explain why it cannot."""
    name = ""
    fields: dict = {}
    rules: list = []
    in_rules = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue
        if stripped.startswith("#"):
            if not name:
                name = stripped.lstrip("#").strip()
            continue
        if in_rules and stripped.startswith(("-", "*")):
            rules.append(stripped[1:].strip())
            continue
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            if key == "rules" and not value:
                in_rules = True
                continue
            in_rules = False
            fields[key] = value

    if not name:
        raise SpecError("no title found — the first heading is the project name")
    if not rules:
        raise SpecError("no rules found — a bot with no rules is a random number generator")

    broker = fields.pop("broker", "paper").lower()
    if broker not in BROKERS:
        raise SpecError(f"unknown broker {broker!r}, expected one of {', '.join(BROKERS)}")

    raw_symbols = fields.pop("symbols", "AAPL")
    symbols = tuple(s.strip().upper() for s in raw_symbols.split(",") if s.strip())
    if not symbols:
        raise SpecError("symbols is empty")

    spec = Spec(
        name=name,
        broker=broker,
        symbols=symbols,
        timeframe=fields.pop("timeframe", "5m"),
        max_position=_parse_number("max_position", fields.pop("max_position", "0.10")),
        stop_loss=_parse_number("stop_loss", fields.pop("stop_loss", "0.02")),
        cash=_parse_number("cash", fields.pop("cash", "10000")),
        rules=rules,
        extra=fields,
    )

    if not 0 < spec.max_position <= 1:
        raise SpecError("max_position must sit between 0 and 1")
    if not 0 < spec.stop_loss <= 1:
        raise SpecError("stop_loss must sit between 0 and 1")
    return spec


def load(path) -> Spec:
    p = Path(path)
    if not p.is_file():
        raise SpecError(f"no spec file at {p}")
    return parse(p.read_text(encoding="utf-8"))
