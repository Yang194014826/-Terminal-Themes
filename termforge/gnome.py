from __future__ import annotations

import ast
import shutil
import subprocess
from dataclasses import dataclass

from .theme import TerminalTheme

PROFILE_SCHEMA = "org.gnome.Terminal.Legacy.Profile"
PROFILES_SCHEMA = "org.gnome.Terminal.ProfilesList"
PROFILES_ROOT = "/org/gnome/terminal/legacy/profiles:"


@dataclass(frozen=True)
class GSettingsCommand:
    args: tuple[str, ...]

    def shell_display(self) -> str:
        return " ".join(_quote(arg) for arg in self.args)


def gnome_terminal_available() -> bool:
    return shutil.which("gsettings") is not None


def apply_theme(
    theme: TerminalTheme,
    *,
    profile_id: str | None = None,
    profile_name: str | None = None,
    dry_run: bool = False,
) -> list[GSettingsCommand]:
    if not gnome_terminal_available():
        raise RuntimeError("gsettings not found; GNOME Terminal settings cannot be changed")

    profile_path = resolve_profile_path(profile_id=profile_id, profile_name=profile_name)
    keys = set(list_keys(profile_path))
    commands = build_apply_commands(theme, profile_path, keys)

    if not dry_run:
        for command in commands:
            subprocess.run(command.args, check=True)
    return commands


def build_apply_commands(
    theme: TerminalTheme,
    profile_path: str,
    keys: set[str],
) -> list[GSettingsCommand]:
    commands: list[GSettingsCommand] = []

    def add(key: str, value: str) -> None:
        if key in keys:
            commands.append(
                GSettingsCommand(("gsettings", "set", f"{PROFILE_SCHEMA}:{profile_path}", key, value))
            )

    add("use-theme-colors", "false")
    add("foreground-color", _gvariant_string(theme.foreground))
    add("background-color", _gvariant_string(theme.background))
    add("cursor-background-color", _gvariant_string(theme.cursor))
    add("cursor-foreground-color", _gvariant_string(theme.background))
    add("highlight-background-color", _gvariant_string(theme.selection_background))
    add("highlight-foreground-color", _gvariant_string(theme.foreground))
    add("palette", _gvariant_array(theme.palette))

    if "use-transparent-background" in keys and "background-transparency-percent" in keys:
        add("use-transparent-background", "true" if theme.transparency > 0 else "false")
        add("background-transparency-percent", str(theme.transparency))

    return commands


def resolve_profile_path(*, profile_id: str | None = None, profile_name: str | None = None) -> str:
    if profile_id and profile_name:
        raise ValueError("use either profile_id or profile_name, not both")
    if profile_id:
        return f"{PROFILES_ROOT}/:{profile_id}/"
    if profile_name:
        for found_id, found_name in list_profiles().items():
            if found_name == profile_name:
                return f"{PROFILES_ROOT}/:{found_id}/"
        raise RuntimeError(f"GNOME Terminal profile not found by visible-name: {profile_name!r}")

    default_id = _gsettings_get(PROFILES_SCHEMA, "default").strip("'")
    return f"{PROFILES_ROOT}/:{default_id}/"


def list_profiles() -> dict[str, str]:
    raw = _gsettings_get(PROFILES_SCHEMA, "list")
    profile_ids = ast.literal_eval(raw)
    profiles: dict[str, str] = {}
    for profile_id in profile_ids:
        path = f"{PROFILES_ROOT}/:{profile_id}/"
        try:
            visible_name = _gsettings_get(f"{PROFILE_SCHEMA}:{path}", "visible-name").strip("'")
        except subprocess.CalledProcessError:
            visible_name = profile_id
        profiles[profile_id] = visible_name
    return profiles


def list_keys(profile_path: str) -> list[str]:
    completed = subprocess.run(
        ["gsettings", "list-keys", f"{PROFILE_SCHEMA}:{profile_path}"],
        check=True,
        text=True,
        capture_output=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def _gsettings_get(schema: str, key: str) -> str:
    completed = subprocess.run(
        ["gsettings", "get", schema, key],
        check=True,
        text=True,
        capture_output=True,
    )
    return completed.stdout.strip()


def _gvariant_string(value: str) -> str:
    return repr(value)


def _gvariant_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(repr(value) for value in values) + "]"


def _quote(arg: str) -> str:
    if not arg or any(char.isspace() or char in "'\"[]():" for char in arg):
        return "'" + arg.replace("'", "'\"'\"'") + "'"
    return arg
