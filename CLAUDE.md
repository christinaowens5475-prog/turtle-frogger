# Turtle Frogger — CLAUDE.md

## Project Overview
A Python/pygame Frogger-style game where a turtle navigates traffic to reach a pond.
Supports both desktop (pygame-ce) and web (pygbag/asyncio) targets.
Deployed to GitHub Pages via pygbag.

## Stack
- Python 3.14 / pygame-ce
- pygbag for WebAssembly/browser builds
- No JavaScript, no npm, no database

## File Map
| File | Purpose |
|------|---------|
| `main.py` | Entry point — runs `Game().run()` via asyncio |
| `src/game.py` | Main game loop, drawing, HUD, level progression |
| `src/turtle_player.py` | Player state, movement, drawing, celebration animation |
| `src/obstavle.py` | Vehicle and PowerUp classes, lane factory (`make_vehicles`) |
| `src/music.py` | Procedural 8-bit music via numpy + pygame.sndarray |

## Constants (duplicated across modules — known debt)
- `GRID_SIZE = 60` — in `game.py` and `turtle_player.py`
- `SCREEN_WIDTH = 600` — in `game.py` and `obstavle.py`
- Colors (`WHITE`, `BLACK`, etc.) — in `game.py`, `turtle_player.py`, `obstavle.py`

## Running Locally
```bash
pip install pygame-ce numpy
python main.py
```

## Running Tests
```bash
pip install pytest
pytest tests/
```

## Building for Web
```bash
pip install pygbag
pygbag --build .
```

## Key Game Rules
- Grid: 10×10 cells, each 60×60 px. HUD is 60 px tall at top.
- Player starts at (5, 10). Goal is y=0 (pond row).
- Moving up scores +10. Reaching goal scores +100.
- 5 lives. Hit by vehicle → flash 90 frames → reset position.
- Power-up gives 300-frame (5s) invincibility.
- Each level: speed increases by `0.3 * (level-1)`.

## Known Issues / Debt
- `obstavle.py` filename is a typo (should be `obstacle.py`) — fixing requires updating imports everywhere
- `numpy` used in `music.py` but not in `requirements.txt` — music silently disabled if missing
- Constants duplicated across modules (GRID_SIZE, SCREEN_WIDTH, colors)
- `self.__init__()` used to restart after game over — works but is unconventional
- No test suite yet — see `audits/test-audit.md`

## Phase
phase-1-foundation (per `.claude/nerve-center-advisory.md`)
