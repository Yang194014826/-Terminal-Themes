from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

from .color import gradient_text, swatch
from .gnome import apply_theme, gnome_terminal_available, list_profiles
from .shell import export_shell_prompt
from .theme import built_in_theme_names, load_theme


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"termforge: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="termforge",
        description="Ubuntu terminal theme customizer for colors, transparency, and prompt gradients.",
    )
    sub = parser.add_subparsers(required=True)

    cmd = sub.add_parser("list", help="List built-in themes")
    cmd.set_defaults(func=cmd_list)

    cmd = sub.add_parser("show", help="Print a theme as JSON")
    cmd.add_argument("theme", help="Built-in theme name or JSON theme path")
    cmd.set_defaults(func=cmd_show)

    cmd = sub.add_parser("preview", help="Preview a theme in the current terminal")
    cmd.add_argument("theme", help="Built-in theme name or JSON theme path")
    cmd.add_argument("--sample", default="termforge ubuntu terminal theme", help="Sample text")
    cmd.set_defaults(func=cmd_preview)

    cmd = sub.add_parser("apply", help="Apply a theme to a terminal emulator")
    cmd.add_argument("theme", help="Built-in theme name or JSON theme path")
    cmd.add_argument("--terminal", choices=["gnome"], default="gnome")
    cmd.add_argument("--profile-id", help="GNOME Terminal profile UUID")
    cmd.add_argument("--profile-name", help="GNOME Terminal visible profile name")
    cmd.add_argument("--dry-run", action="store_true", help="Print gsettings commands without applying")
    cmd.set_defaults(func=cmd_apply)

    cmd = sub.add_parser("export-shell", help="Generate a Bash/Zsh prompt snippet")
    cmd.add_argument("theme", help="Built-in theme name or JSON theme path")
    cmd.add_argument("--shell", choices=["bash", "zsh"], default="zsh")
    cmd.add_argument("--output", type=Path, help="Write snippet to this path")
    cmd.set_defaults(func=cmd_export_shell)

    cmd = sub.add_parser("prompt-gradient", help="Render sample text with the theme prompt gradient")
    cmd.add_argument("theme", help="Built-in theme name or JSON theme path")
    cmd.add_argument("text")
    cmd.set_defaults(func=cmd_prompt_gradient)

    cmd = sub.add_parser("doctor", help="Report terminal customization support")
    cmd.set_defaults(func=cmd_doctor)

    return parser


def cmd_list(args: argparse.Namespace) -> int:
    for name in built_in_theme_names():
        print(name)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    theme = load_theme(args.theme)
    print(json.dumps(theme.to_dict(), indent=2))
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    theme = load_theme(args.theme)
    print(f"name:         {theme.name}")
    print(f"background:   {theme.background}")
    print(f"foreground:   {theme.foreground}")
    print(f"transparency: {theme.transparency}%")
    print()
    print("palette:")
    for idx in range(0, len(theme.palette), 4):
        print("  " + swatch(theme.palette[idx : idx + 4]))
    print()
    print("prompt gradient:")
    print("  " + gradient_text(args.sample, theme.prompt_gradient))
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    theme = load_theme(args.theme)
    commands = apply_theme(
        theme,
        profile_id=args.profile_id,
        profile_name=args.profile_name,
        dry_run=args.dry_run,
    )
    if args.dry_run:
        for command in commands:
            print(command.shell_display())
    else:
        print(f"Applied theme {theme.name!r} to GNOME Terminal.")
    return 0


def cmd_export_shell(args: argparse.Namespace) -> int:
    theme = load_theme(args.theme)
    script = export_shell_prompt(theme, args.shell)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(script, encoding="utf-8")
        print(args.output)
    else:
        print(script, end="")
    return 0


def cmd_prompt_gradient(args: argparse.Namespace) -> int:
    theme = load_theme(args.theme)
    print(gradient_text(args.text, theme.prompt_gradient))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    print(f"system: {platform.system()} {platform.release()}")
    print(f"python: {platform.python_version()}")
    print(f"gsettings: {'yes' if gnome_terminal_available() else 'no'}")
    print("gnome_terminal_colors: yes" if gnome_terminal_available() else "gnome_terminal_colors: no")
    print("gnome_terminal_transparency: version-dependent; termforge applies it only when keys exist")
    print("gnome_terminal_background_image: no")
    if gnome_terminal_available():
        try:
            profiles = list_profiles()
        except Exception as exc:
            print(f"gnome_profiles: unavailable ({exc})")
        else:
            print("gnome_profiles:")
            for profile_id, name in profiles.items():
                print(f"  {profile_id}  {name}")
    return 0
