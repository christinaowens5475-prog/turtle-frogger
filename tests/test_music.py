"""Tests for music module pure-logic functions (no audio hardware required)."""
import importlib
import pytest


@pytest.fixture(autouse=True)
def reset_music():
    """Reset music module global state between tests."""
    import src.music as m
    m._muted = False
    m._note_index = 0
    yield
    m._muted = False
    m._note_index = 0


def test_toggle_mute_enables():
    import src.music as m
    assert m.is_muted() is False
    m.toggle_mute()
    assert m.is_muted() is True


def test_toggle_mute_disables():
    import src.music as m
    m.toggle_mute()
    m.toggle_mute()
    assert m.is_muted() is False


def test_is_muted_reflects_state():
    import src.music as m
    m._muted = True
    assert m.is_muted() is True
    m._muted = False
    assert m.is_muted() is False
