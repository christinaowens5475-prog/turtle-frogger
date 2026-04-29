# Test Audit — 2026-04-27

## Status: NO TESTS EXIST

This project has zero tests. No test framework is installed.

## Environment Gap
- `pytest` not installed
- `pygame-ce` not installed in the audit environment (Python 3.14 bare)
- `numpy` not in `requirements.txt`

## Test Framework Recommendation
**pytest** — minimal setup, no config needed for pure Python logic tests.
pygame drawing code cannot be easily unit-tested without a display; isolate it behind the logic boundary.

### Setup Required
```bash
pip install pytest pygame-ce numpy
```

Add `pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

## Coverage Gaps (by module)

### `src/turtle_player.py` — HIGH PRIORITY
| Behaviour | Test needed |
|-----------|------------|
| `move("up")` decrements `y` and adds 10 to score | `test_move_up_decrements_y_and_scores` |
| `move("up")` at `y=0` is a no-op | `test_move_up_clamps_at_zero` |
| `move("down")` at `y=10` is a no-op | `test_move_down_clamps_at_ten` |
| `move("left")` at `x=0` is a no-op | `test_move_left_clamps_at_zero` |
| `move("right")` at `x=9` is a no-op | `test_move_right_clamps_at_nine` |
| `take_hit` decrements `lives` and starts flash | `test_take_hit_decrements_lives` |
| `activate_invincibility` sets timer to 300 | `test_invincibility_sets_timer` |
| `update` counts down `inv_timer` and clears `invincible` when expired | `test_invincibility_expires` |
| `update` counts down `flash_timer` and calls `reset_position` when expired | `test_flash_expires_resets_position` |
| `celebrate` sets `celebrating=True` and `celebrate_timer=180` | `test_celebrate_sets_state` |
| `update` freezes other timers while celebrating | `test_celebrate_freezes_timers` |
| `get_rect` returns correct pixel bounds for given (x, y) | `test_get_rect_pixel_bounds` |
| `reset_position` returns player to (5, 10) | `test_reset_position` |

### `src/obstavle.py` — MEDIUM PRIORITY
| Behaviour | Test needed |
|-----------|------------|
| `Vehicle.update` moves `x` by `speed` each tick | `test_vehicle_moves_by_speed` |
| `Vehicle` wraps right when `x > SCREEN_WIDTH` | `test_vehicle_wraps_right` |
| `Vehicle` wraps left when `x + w < 0` | `test_vehicle_wraps_left` |
| `Vehicle.get_rect` returns correct pixel rect | `test_vehicle_get_rect` |
| `PowerUp.check_collect` returns `True` when player on same cell | `test_powerup_collect_match` |
| `PowerUp.check_collect` returns `False` when player elsewhere | `test_powerup_collect_miss` |
| `PowerUp.update` deactivates after 300 ticks | `test_powerup_deactivates` |
| `PowerUp.update` respawns after 600 extra ticks | `test_powerup_respawns` |
| `make_vehicles` returns vehicles for rows 1-9 | `test_make_vehicles_row_coverage` |
| `make_vehicles` speed scales with level | `test_make_vehicles_speed_scaling` |

### `src/game.py` — LOW PRIORITY (requires pygame display)
| Behaviour | Notes |
|-----------|-------|
| Goal detection (`p.y == 0`) awards 100 points | Extract to testable method |
| Collision detection delegates to `v.colliderect` | Mock vehicles |
| Level advances when celebration ends | Integration test |
| Lives reach 0 → `_game_over` called | Mock `_game_over` |

### `src/music.py` — LOW PRIORITY
| Behaviour | Notes |
|-----------|-------|
| `toggle_mute` flips `_muted` state | Pure logic, testable |
| `is_muted` reflects current state | Pure logic |
| `init` gracefully skips when numpy missing | Already handled by `_NUMPY_OK` |

## Acceptance Criteria for "Test Audit Complete"
- [ ] `pytest` in `requirements.txt` (dev dependency)
- [ ] All `TurtlePlayer` logic tests pass
- [ ] All `Vehicle` / `PowerUp` logic tests pass
- [ ] `music.toggle_mute` / `is_muted` tested
- [ ] CI runs `pytest` on push
- [ ] Coverage ≥ 70% on non-drawing code

## Blocker
`pygame.Rect` is needed for `get_rect` tests. The tests can import just `pygame` (no display needed) if `pygame.display.init()` is not called. Use `os.environ["SDL_VIDEODRIVER"] = "dummy"` in `conftest.py`.
