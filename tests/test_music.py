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
    m.stop()


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


def test_init_sets_music_available():
    """init() must set _music_available = True in a normal environment."""
    import src.music as m
    m._music_available = False
    m._sounds.clear()
    m.init()
    assert m._music_available is True
    assert set(m._sounds.keys()) == set(m._NOTES.keys())


def test_init_works_without_numpy(monkeypatch):
    """init() must succeed and set _music_available = True even when numpy is absent."""
    import src.music as m
    monkeypatch.setattr(m, '_NUMPY_OK', False)
    m._music_available = False
    m._sounds.clear()
    m.init()
    assert m._music_available is True
    assert set(m._sounds.keys()) == set(m._NOTES.keys())
