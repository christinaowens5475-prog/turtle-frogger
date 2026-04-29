# Drift Audit — 2026-04-27

Code rot, inconsistencies, and structural divergence from good Python practices.

---

## DRIFT-001 — Typo in filename: `obstavle.py` (should be `obstacle.py`)
**Severity:** Medium  
**File:** `src/obstavle.py`  
**Description:** The filename is a misspelling. All imports reference the typo (`from .obstavle import ...`). Fixing requires renaming the file and updating imports in `game.py` and any future files.  
**Why it drifted:** Likely a quick initial commit that never got corrected.  
**Fix:**
```bash
git mv src/obstavle.py src/obstacle.py
# Update import in src/game.py:
# from .obstavle import make_vehicles, PowerUp
# → from .obstacle import make_vehicles, PowerUp
```
**Risk:** Low — mechanical rename, git history preserved with `git mv`.

---

## DRIFT-002 — Constants duplicated across modules
**Severity:** Medium  
**Files:** `game.py`, `turtle_player.py`, `obstavle.py`  
**Constants duplicated:**
- `GRID_SIZE = 60` — `game.py:6`, `turtle_player.py:4`
- `SCREEN_WIDTH = 600` — `game.py:8`, `obstavle.py:4`
- `WHITE = (255,255,255)` — all three files
- `BLACK = (0,0,0)` — `game.py` + `turtle_player.py`
- `YELLOW = (255,220,0)` — `game.py` + `turtle_player.py`

**Risk of drift:** If `GRID_SIZE` changes in one file but not another, layout breaks silently.  
**Fix:** Create `src/constants.py` and import from there. Medium refactor — not urgent but should be done before any layout changes.

---

## DRIFT-003 — numpy not in requirements.txt
**Severity:** Medium  
**Files:** `src/music.py:4`, `requirements.txt`  
**Description:** See BUG-001. From a drift perspective: the commit "Remove numpy from web requirements" (7b994fa) removed numpy from web requirements, but `music.py` still imports it. The desktop requirements were never updated to be explicit. This creates two classes of installs: desktop (numpy needed for music) and web (numpy absent, music silent). The requirements.txt doesn't distinguish these.  
**Fix:** Add `numpy` as an optional/desktop dependency or create `requirements-dev.txt`.

---

## DRIFT-004 — No type hints anywhere
**Severity:** Low  
**Files:** All source files  
**Description:** Python 3.14 supports full type hints. None of the game classes, methods, or functions use them. This makes IDE autocompletion and static analysis (mypy, pyright) less useful.  
**Fix:** At minimum annotate public method signatures:
```python
def move(self, direction: str) -> None: ...
def get_rect(self) -> pygame.Rect: ...
def make_vehicles(level: int) -> list[Vehicle]: ...
```
**Priority:** Low — game code, not a library. But add before codebase grows.

---

## DRIFT-005 — Music module uses mutable module-level globals
**Severity:** Low  
**File:** `src/music.py:31-34`  
**Description:** `_sounds`, `_note_index`, `_muted`, `_music_available` are module-level globals mutated by functions. This is a common Python anti-pattern that makes testing difficult (state leaks between tests) and makes the module non-reentrant.  
**Fix:** Wrap in a `MusicPlayer` class. Low priority since there's only one instance of the game.

---

## DRIFT-006 — `_game_over` is async but `run` is the only caller — inconsistency
**Severity:** Very Low  
**File:** `src/game.py:115`  
**Description:** `_game_over` is `async def` and uses `await asyncio.sleep(0)` in a loop (correct for pygbag). This is intentional and correct. Not drift — just documenting that the async boundary is correctly placed.  
**Status:** No action needed.

---

## DRIFT-007 — No `.claude/handoff.md`
**Severity:** High (process drift)  
**Description:** Per OVERSEER RULES, `handoff.md` must be maintained at the end of every session. File did not exist at audit start.  
**Fix:** Created in this session (see below).

---

## DRIFT-008 — No CLAUDE.md
**Severity:** High (process drift)  
**Description:** No project context file existed at audit start. Created in this session.  
**Fix:** Created `CLAUDE.md` in this session.

---

## DRIFT-009 — No test suite
**Severity:** High (process drift)  
**Description:** Per OVERSEER RULES, no request is complete without tests, and if no framework exists it must be set up first. Zero tests exist.  
**Fix:** See `audits/test-audit.md`. Test scaffold created in this session under `tests/`.

---

## Summary Table

| ID | Severity | Type | Description |
|----|----------|------|-------------|
| DRIFT-001 | Medium | Naming | `obstavle.py` filename typo |
| DRIFT-002 | Medium | Architecture | Constants duplicated across 3 modules |
| DRIFT-003 | Medium | Dependencies | numpy used but not in requirements.txt |
| DRIFT-004 | Low | Style | No type hints anywhere |
| DRIFT-005 | Low | Architecture | Music module uses mutable globals |
| DRIFT-006 | Very Low | — | Async `_game_over` — intentional, correct |
| DRIFT-007 | High | Process | No handoff.md |
| DRIFT-008 | High | Process | No CLAUDE.md |
| DRIFT-009 | High | Process | No test suite |
