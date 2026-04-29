# Technical Debt Log

| Date | ID | Area | Description | Severity | Source |
|------|----|------|-------------|----------|--------|
| 2026-04-27 | DEBT-001 | Naming | `src/obstavle.py` filename typo — should be `obstacle.py` | Medium | drift-audit DRIFT-001 |
| 2026-04-27 | DEBT-002 | Architecture | Constants (`GRID_SIZE`, `SCREEN_WIDTH`, colors) duplicated across 3 modules | Medium | drift-audit DRIFT-002 |
| 2026-04-27 | DEBT-003 | Dependencies | `numpy` absent from `requirements.txt` — intentional (web load speed); `music.py` degrades silently via try/except | Closed | bughunt BUG-001 / drift-audit DRIFT-003 |
| 2026-04-27 | DEBT-004 | Bug | Invincibility HUD timer displays 1 second too high (`// 60 + 1`) | Closed | bughunt BUG-002 — fixed in commit a31928d (`(p.inv_timer + 59) // 60`) |
| 2026-04-27 | DEBT-005 | Architecture | `_game_over` restarts game via `self.__init__()` — re-inits pygame | Low | bughunt BUG-003 |
| 2026-04-27 | DEBT-006 | UX | PowerUp can spawn visually under a vehicle | Low | bughunt BUG-004 |
| 2026-04-27 | DEBT-007 | Performance | Static background redrawn from scratch every frame (200+ draw calls) | Medium | optimize OPT-001 |
| 2026-04-27 | DEBT-008 | Style | No type hints on any public methods or functions | Low | drift-audit DRIFT-004 |
| 2026-04-27 | DEBT-009 | Testing | Zero tests exist — no test framework installed | Closed | test-audit — 37 tests added 2026-04-27 (pytest, all passing) |
| 2026-04-27 | DEBT-010 | Architecture | Music module uses mutable module-level state — hard to test | Low | drift-audit DRIFT-005 |
| 2026-04-27 | DEBT-011 | Bug | `music.stop()` doesn't reset `_note_index` | Very Low | bughunt BUG-006 |
