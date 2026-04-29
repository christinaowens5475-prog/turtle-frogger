# Optimization Audit — 2026-04-27

Static analysis only. All profiling claims are theoretical; validate with cProfile if needed.

---

## OPT-001 — Cache static background surfaces (High Impact)
**File:** `src/game.py` — `_draw_road_lanes`, `_draw_pond`, `_draw_start_zone`  
**Issue:** All three methods are called every frame (60 FPS) and draw content that never changes between frames. `_draw_road_lanes` draws 10 rectangles + 150 dashed lines. `_draw_pond` draws 12 ellipses, 5 lily pads, and text.  
**Cost:** ~200+ draw calls/frame for static geometry.  
**Fix:** Pre-render to a `pygame.Surface` in `__init__`, blit the cached surface each frame.
```python
# In __init__:
self._bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
self._draw_road_lanes_to(self._bg)
self._draw_pond_to(self._bg)
self._draw_start_zone_to(self._bg)

# In _draw:
self.screen.blit(self._bg, (0, 0))   # replaces fill + 3 draw methods
```
**Estimated gain:** Eliminates ~200 draw calls/frame → significant on low-power hardware / web.

---

## OPT-002 — Cache vehicle Rects (Low Impact)
**File:** `src/game.py:171`, `src/obstavle.py:58-60`  
**Issue:** `any(t_rect.colliderect(v.get_rect()) for v in self.vehicles)` creates a new `pygame.Rect` for every vehicle on every frame. With ~20-27 vehicles, that's ~25 Rect allocations/frame just for collision.  
**Fix:** Store the rect as `self._rect` in `Vehicle.update()` and return it from `get_rect()` without reconstructing.
```python
def update(self):
    self.x += self.speed
    # wrap logic...
    y = self.row * GRID_SIZE + 60 + (GRID_SIZE - self.h) // 2
    self._rect = pygame.Rect(self.x, y, self.w, self.h)

def get_rect(self):
    return self._rect
```
**Estimated gain:** Saves ~25 small object allocations/frame. Minor in CPython, more meaningful in Pyodide (web).

---

## OPT-003 — Pre-render font surfaces for static HUD text (Very Low Impact)
**File:** `src/game.py:77-93`  
**Issue:** `self.font.render(f"Score: {p.score}", True, WHITE)` is called every frame, but the score only changes when the player moves. Same for `Level:` text.  
**Fix:** Cache rendered text surfaces and invalidate only on change.
```python
# Only re-render when score changes:
if p.score != self._last_score:
    self._score_surf = self.font.render(f"Score: {p.score}", True, WHITE)
    self._last_score = p.score
self.screen.blit(self._score_surf, (10, 15))
```
**Estimated gain:** Trivial for desktop; reduces GC pressure in browser builds.

---

## OPT-004 — music._make_tone is called once at init — already optimal
**File:** `src/music.py:53-64`  
**Status:** Notes are pre-generated at init and stored as pygame.Sound objects. Playback is just `sound.play()`. No optimization needed.

---

## OPT-005 — make_vehicles called on every level-up (acceptable)
**File:** `src/game.py:185`  
**Status:** `make_vehicles` runs once per level transition, not per frame. The cost is negligible. No optimization needed.

---

## OPT-006 — Celebration math uses sin/cos every frame (Very Low Impact)
**File:** `src/turtle_player.py:85-119`  
**Issue:** `_draw_celebrating` calls `math.sin`/`math.cos` ~15 times per frame for 3 seconds (180 frames). Total ≈ 2700 trig calls for a celebration.  
**Fix:** Not worth optimizing. Celebration is short-lived and trig on modern hardware is negligible.

---

## Priority Order
1. **OPT-001** — Background surface cache (do this first, biggest win on web)
2. **OPT-002** — Vehicle rect caching (quick win, marginal improvement)
3. **OPT-003** — Font surface caching (only if profiling shows render calls as hot)

## Web-Specific Notes
On pygbag/Pyodide, Python runs at ~50-80% native speed and GC is more expensive. OPT-001 will have the largest impact there. The game currently calls `await asyncio.sleep(0)` every frame correctly — this is the right pattern for pygbag and should not be changed.
