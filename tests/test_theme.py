from termforge.shell import export_shell_prompt
from termforge.theme import built_in_theme_names, load_theme


def test_builtin_themes_load():
    names = built_in_theme_names()
    assert {"aurora", "ember", "paper"}.issubset(names)
    for name in names:
        theme = load_theme(name)
        assert len(theme.palette) == 16


def test_shell_export_contains_theme_name():
    theme = load_theme("aurora")
    script = export_shell_prompt(theme, "zsh")
    assert "TERMFORGE_THEME='aurora'" in script
    assert "PROMPT=" in script
