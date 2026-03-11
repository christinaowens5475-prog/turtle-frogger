import pygame

try:
    import numpy as np
    _NUMPY_OK = True
except ImportError:
    _NUMPY_OK = False

SAMPLE_RATE = 44100
MUSIC_EVENT = pygame.USEREVENT + 1

# Note frequencies (Hz)
_NOTES = {
    "E4": 329.63, "F4": 349.23, "G4": 392.00,
    "A4": 440.00, "B4": 493.88, "C5": 523.25,
    "D5": 587.33, "E5": 659.25, "REST": 0,
}

# Upbeat looping melody
_MELODY = [
    "G4", "G4", "C5", "C5", "B4", "A4", "G4", "REST",
    "E4", "E4", "A4", "A4", "G4", "F4", "E4", "REST",
    "G4", "B4", "D5", "B4", "G4", "B4", "A4", "REST",
    "F4", "A4", "C5", "A4", "G4", "E4", "G4", "REST",
]

BPM      = 160
_BEAT_MS = int(60_000 / BPM / 2)   # eighth-note duration

_sounds          = {}
_note_index      = 0
_muted           = False
_music_available = False


def _make_tone(freq, duration_ms, volume=0.30):
    frames = int(duration_ms / 1000 * SAMPLE_RATE)
    if freq == 0 or frames == 0:
        wave = np.zeros((frames, 2), dtype=np.int16)
        return pygame.sndarray.make_sound(wave)

    t    = np.linspace(0, duration_ms / 1000, frames, False)
    wave = np.sign(np.sin(2 * np.pi * freq * t))
    wave += 0.4 * np.sign(np.sin(4 * np.pi * freq * t))

    release = min(int(0.12 * frames), frames)
    wave[-release:] *= np.linspace(1, 0, release)

    wave = np.clip(wave / 1.4 * volume * 32767, -32767, 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack([wave, wave]))


def init():
    """Pre-generate note sounds and start the music timer. Silently skipped if numpy/sndarray unavailable."""
    global _music_available
    if not _NUMPY_OK:
        return
    try:
        pygame.mixer.set_num_channels(8)
        for name, freq in _NOTES.items():
            _sounds[name] = _make_tone(freq, _BEAT_MS)
        pygame.time.set_timer(MUSIC_EVENT, _BEAT_MS)
        _music_available = True
    except Exception:
        _music_available = False


def handle_event(event):
    global _note_index
    if not _music_available or _muted:
        return
    if event.type == MUSIC_EVENT:
        _sounds[_MELODY[_note_index % len(_MELODY)]].play()
        _note_index += 1


def toggle_mute():
    global _muted
    _muted = not _muted


def is_muted():
    return _muted


def stop():
    if _music_available:
        pygame.time.set_timer(MUSIC_EVENT, 0)
