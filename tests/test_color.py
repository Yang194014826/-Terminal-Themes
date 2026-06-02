from termforge.color import gradient, gradient_text, hex_to_rgb, lerp_color, normalize_hex


def test_normalize_hex_accepts_hashless_values():
    assert normalize_hex("ABCDEF") == "#abcdef"


def test_hex_to_rgb():
    assert hex_to_rgb("#102030") == (16, 32, 48)


def test_lerp_color_midpoint():
    assert lerp_color("#000000", "#ffffff", 0.5) == "#808080"


def test_gradient_uses_requested_step_count():
    assert gradient(["#000000", "#ffffff"], 3) == ["#000000", "#808080", "#ffffff"]


def test_gradient_text_contains_reset_sequence():
    assert gradient_text("ok", ["#ff0000"]).endswith("\033[0m")
