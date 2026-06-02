# Termforge

Termforge is an open source Ubuntu terminal theme customizer. It can preview
themes, apply color palettes and transparency to GNOME Terminal, and generate
Bash/Zsh prompt snippets with ANSI true-color gradients.

It does not require `sudo`. It changes only the current user's terminal profile.

## Install

From source:

```bash
python3 -m pip install .
```

For local development:

```bash
python3 -m pip install -e .
```

## Quick Start

Preview a theme:

```bash
termforge preview aurora
```

Apply it to the default GNOME Terminal profile:

```bash
termforge apply aurora --terminal gnome
```

Check what would be changed without applying:

```bash
termforge apply aurora --terminal gnome --dry-run
```

Generate a shell prompt snippet:

```bash
termforge export-shell aurora --shell zsh > ~/.termforge-prompt.zsh
echo 'source ~/.termforge-prompt.zsh' >> ~/.zshrc
```

## Built-in Themes

```bash
termforge list
```

Current built-ins:

- `aurora`: dark background, cyan/green/pink accents, 18% transparency.
- `ember`: dark charcoal background, warm orange/red accents.
- `paper`: light background, high-contrast text.

## Custom Theme

Create a JSON file:

```json
{
  "name": "my-theme",
  "background": "#101218",
  "foreground": "#f3f5f7",
  "cursor": "#7dd3fc",
  "selection_background": "#263244",
  "transparency": 12,
  "prompt_gradient": ["#7dd3fc", "#a7f3d0", "#f0abfc"],
  "palette": [
    "#1f2430", "#ff5c57", "#5af78e", "#f3f99d",
    "#57c7ff", "#ff6ac1", "#9aedfe", "#f1f1f0",
    "#686f7a", "#ff5c57", "#5af78e", "#f3f99d",
    "#57c7ff", "#ff6ac1", "#9aedfe", "#ffffff"
  ]
}
```

Then:

```bash
termforge preview ./my-theme.json
termforge apply ./my-theme.json --terminal gnome
```

## Background Images

Modern GNOME Terminal does not support terminal background images. Termforge
reports this in `doctor` instead of pretending to change it:

```bash
termforge doctor
```

For real background images, use a terminal emulator that supports them, such as
Kitty or WezTerm. Termforge's first release focuses on Ubuntu's default GNOME
Terminal.

## Commands

```bash
termforge list
termforge show aurora
termforge preview aurora
termforge apply aurora --terminal gnome --dry-run
termforge export-shell aurora --shell bash
termforge prompt-gradient aurora "hello ubuntu"
termforge doctor
```

## Safety

- No `sudo` is needed.
- `apply --dry-run` prints the `gsettings` commands before changing anything.
- Only the current user's GNOME Terminal profile is modified.
- If transparency keys are missing on your GNOME Terminal version, Termforge
  skips transparency and still applies colors.
