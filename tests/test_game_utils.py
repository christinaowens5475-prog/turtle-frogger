"""Tests for game-level utility functions (no display required)."""
from src.game import _pond_colors_for_level, _POND_PALETTE


def test_pond_color_level_1_is_blue():
    main, _ = _pond_colors_for_level(1)
    assert main == (30, 144, 255)


def test_pond_colors_unique_per_level():
    mains = [_pond_colors_for_level(lvl)[0] for lvl in range(1, len(_POND_PALETTE) + 1)]
    assert len(set(mains)) == len(_POND_PALETTE), "every level in the palette needs a unique color"


def test_pond_colors_cycle_after_palette():
    n = len(_POND_PALETTE)
    assert _pond_colors_for_level(1) == _pond_colors_for_level(n + 1)


def test_pond_colors_returns_two_tuples():
    main, dark = _pond_colors_for_level(3)
    assert len(main) == 3 and len(dark) == 3
