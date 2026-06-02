from __future__ import annotations

import re
from typing import Iterable, Sequence

HEX_RE = re.compile(r"^#?[0-9a-fA-F]{6}$")


def normalize_hex(value: str) -> str:
    raw = value.strip()
    if not HEX_RE.match(raw):
        raise ValueError(f"invalid RGB hex color: {value!r}")
    if not raw.startswith("#"):
        raw = f"#{raw}"
    return raw.lower()


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    color = normalize_hex(value).lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(rgb: Sequence[int]) -> str:
    if len(rgb) != 3:
        raise ValueError("RGB value must contain exactly 3 channels")
    channels = []
    for channel in rgb:
        if channel < 0 or channel > 255:
            raise ValueError(f"RGB channel out of range: {channel}")
        channels.append(channel)
    return "#{:02x}{:02x}{:02x}".format(*channels)


def lerp_color(left: str, right: str, ratio: float) -> str:
    ratio = max(0.0, min(1.0, ratio))
    l_rgb = hex_to_rgb(left)
    r_rgb = hex_to_rgb(right)
    return rgb_to_hex(tuple(round(l + (r - l) * ratio) for l, r in zip(l_rgb, r_rgb)))


def gradient(colors: Sequence[str], steps: int) -> list[str]:
    if steps <= 0:
        return []
    normalized = [normalize_hex(color) for color in colors]
    if not normalized:
        raise ValueError("at least one gradient color is required")
    if len(normalized) == 1 or steps == 1:
        return [normalized[0]] * steps

    result = []
    spans = len(normalized) - 1
    for idx in range(steps):
        pos = idx / max(steps - 1, 1)
        span_idx = min(int(pos * spans), spans - 1)
        span_start = span_idx / spans
        span_size = 1 / spans
        local_ratio = (pos - span_start) / span_size
        result.append(lerp_color(normalized[span_idx], normalized[span_idx + 1], local_ratio))
    return result


def ansi_fg(color: str) -> str:
    r, g, b = hex_to_rgb(color)
    return f"\033[38;2;{r};{g};{b}m"


def ansi_bg(color: str) -> str:
    r, g, b = hex_to_rgb(color)
    return f"\033[48;2;{r};{g};{b}m"


def ansi_reset() -> str:
    return "\033[0m"


def gradient_text(text: str, colors: Sequence[str]) -> str:
    rendered = []
    for char, color in zip(text, gradient(colors, len(text))):
        rendered.append(f"{ansi_fg(color)}{char}")
    rendered.append(ansi_reset())
    return "".join(rendered)


def swatch(colors: Iterable[str]) -> str:
    blocks = []
    for color in colors:
        blocks.append(f"{ansi_bg(color)}  {ansi_reset()} {normalize_hex(color)}")
    return "  ".join(blocks)
