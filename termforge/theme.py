from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any

from .color import normalize_hex


@dataclass(frozen=True)
class TerminalTheme:
    name: str
    background: str
    foreground: str
    cursor: str
    selection_background: str
    transparency: int
    palette: tuple[str, ...]
    prompt_gradient: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TerminalTheme":
        required = [
            "name",
            "background",
            "foreground",
            "cursor",
            "selection_background",
            "transparency",
            "palette",
            "prompt_gradient",
        ]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"theme missing fields: {', '.join(missing)}")

        palette = tuple(normalize_hex(color) for color in data["palette"])
        if len(palette) != 16:
            raise ValueError("theme palette must contain exactly 16 colors")

        prompt_gradient = tuple(normalize_hex(color) for color in data["prompt_gradient"])
        if not prompt_gradient:
            raise ValueError("theme prompt_gradient must contain at least one color")

        transparency = int(data["transparency"])
        if transparency < 0 or transparency > 100:
            raise ValueError("theme transparency must be between 0 and 100")

        return cls(
            name=str(data["name"]),
            background=normalize_hex(data["background"]),
            foreground=normalize_hex(data["foreground"]),
            cursor=normalize_hex(data["cursor"]),
            selection_background=normalize_hex(data["selection_background"]),
            transparency=transparency,
            palette=palette,
            prompt_gradient=prompt_gradient,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "background": self.background,
            "foreground": self.foreground,
            "cursor": self.cursor,
            "selection_background": self.selection_background,
            "transparency": self.transparency,
            "palette": list(self.palette),
            "prompt_gradient": list(self.prompt_gradient),
        }


def built_in_theme_names() -> list[str]:
    theme_dir = resources.files("termforge").joinpath("themes")
    return sorted(path.name.removesuffix(".json") for path in theme_dir.iterdir() if path.name.endswith(".json"))


def load_theme(name_or_path: str) -> TerminalTheme:
    path = Path(name_or_path).expanduser()
    if path.exists():
        return _load_theme_path(path)

    if path.suffix == ".json":
        raise FileNotFoundError(f"theme file not found: {path}")

    theme_file = resources.files("termforge").joinpath("themes", f"{name_or_path}.json")
    if not theme_file.is_file():
        choices = ", ".join(built_in_theme_names())
        raise FileNotFoundError(f"unknown theme {name_or_path!r}; built-ins: {choices}")

    with theme_file.open("r", encoding="utf-8") as handle:
        return TerminalTheme.from_dict(json.load(handle))


def _load_theme_path(path: Path) -> TerminalTheme:
    with path.open("r", encoding="utf-8") as handle:
        return TerminalTheme.from_dict(json.load(handle))
