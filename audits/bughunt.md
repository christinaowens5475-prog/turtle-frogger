# Bug Hunt — 2026-04-27

Static analysis of all source files. No runtime available in audit environment.

---

## BUG-001 — numpy in music.py but not in requirements.txt
**Severity:** Medium  
**File:** `src/music.py:4`, `requirements.txt`  
**Description:** `music.py` imports `numpy` and uses it for waveform generation. `requirements.txt` only lists `pygame-ce`. On a fresh install (`pip install -r requirements.txt`), music silently fails — `_NUMPY_OK = False` and `init()` returns early. No error is surfaced to the user.  
**Impact:** All music disabled silently on fresh installs and web builds.  
**Fix:** Add `numpy` to `requirements.txt`, OR document in CLAUDE.md that music requires `numpy` separately (already added to CLAUDE.md).  
**Status:** Partially mitigated by `_NUMPY_OK` guard; root cause not fixed.

---

## BUG-002 — inv_timer display is off by one second
**Severity:** Low  
**File:** `src/game.py:85`  
**Description:** `p.inv_timer // 60 + 1` — at `inv_timer=300` (just activated) this shows `6s` but actual remaining time is `5s`. The `+ 1` inflates the displayed countdown by 1 second throughout.  
**Reproduction:** Collect a power-up; HUD shows "INVINCIBLE! 6s" at activation.  
**Fix:**
```python
# Before
txt = self.small_font.render(f"INVINCIBLE! {p.inv_timer // 60 + 1}s", True, YELLOW)
# After
txt = self.small_font.render(f"INVINCIBLE! {p.inv_timer // 60}s", True, YELLOW)
```

---

## BUG-003 — Game restart via self.__init__() re-initializes pygame
**Severity:** Low  
**File:** `src/game.py:131`  
**Description:** `_game_over` calls `self.__init__()` to restart. This calls `pygame.init()` again (benign but wasteful), creates a new display surface (replacing the existing one), and silently leaks the old fonts. On some platforms `pygame.display.set_mode()` called twice can cause a flash or warning.  
**Impact:** Low risk on desktop; potential instability in browser (pygbag) across restarts.  
**Fix:** Extract restart logic into a `_reset_state()` method that only resets game-state attributes without re-initializing pygame.

---

## BUG-004 — PowerUp can spawn inside the pond row (y=0) if spawned during level transition
**Severity:** Low  
**File:** `src/obstavle.py:69`  
**Description:** `PowerUp._spawn()` uses `random.randint(1, 9)` for `y` — this limits it to road rows. However, `y=1` through `y=9` overlap with vehicle lanes. The PowerUp is drawn on top of vehicles but collected by grid position match (`check_collect`). This is a visual overlap issue, not a logic bug. The more serious case is that if a PowerUp spawns at the same cell as a vehicle, the heart icon is obscured and the player cannot see the pickup.  
**Impact:** Minor UX — power-up occasionally invisible under a vehicle.  
**Fix:** After `_spawn()`, check for vehicle overlap or restrict spawn to cells with no active vehicle.

---

## BUG-005 — Vehicle wrapping uses instantaneous x, not clamped
**Severity:** Very Low  
**File:** `src/obstavle.py:27-30`  
**Description:** `Vehicle.update` adds `speed` then checks wrap condition. At very high levels, speed could theoretically be large enough to jump past the wrap check in a single frame, but since `speed = 1 + (level-1)*0.3`, at level 20 speed ≈ 6.7 — well within one frame's travel. Not a realistic issue.  
**Status:** Not a true bug; document as non-issue.

---

## BUG-006 — music.stop() doesn't reset _note_index
**Severity:** Very Low  
**File:** `src/music.py:86-88`  
**Description:** `music.stop()` cancels the timer but doesn't reset `_note_index`. On game restart via `self.__init__()`, `music.init()` is called again which re-sets the timer, but `_note_index` continues from where it left off. This is harmless (the melody loops), but is unexpected state.  
**Fix:** Add `_note_index = 0` to `stop()`.

---

## Summary Table

| ID | Severity | File | Description | Fix Complexity |
|----|----------|------|-------------|----------------|
| BUG-001 | Medium | `requirements.txt`, `music.py` | numpy not in requirements | Trivial |
| BUG-002 | Low | `game.py:85` | Invincibility timer off by 1s | Trivial |
| BUG-003 | Low | `game.py:131` | Restart via `__init__()` re-inits pygame | Medium |
| BUG-004 | Low | `obstavle.py:69` | PowerUp can appear under vehicles | Low |
| BUG-005 | Very Low | `obstavle.py:27` | Vehicle wrap at high speeds | Non-issue |
| BUG-006 | Very Low | `music.py:86` | Note index not reset on stop | Trivial |
