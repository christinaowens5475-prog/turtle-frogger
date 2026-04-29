import asyncio
import pygame

from .turtle_player import TurtlePlayer
from .obstavle import make_vehicles, PowerUp
from . import music

SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 660
GRID_SIZE     = 60
FPS           = 60

WHITE      = (255, 255, 255)
YELLOW     = (255, 220, 0)
BLACK      = (0,   0,   0)
RED        = (200, 30,  30)
GRAY       = (50,  50,  50)
DARK_GRAY  = (80,  80,  80)
LILY_GREEN = (0,   160, 60)

# (main_fill, ripple_outline) per level — cycles when level > palette length
_POND_PALETTE = [
    ((30,  144, 255), (0,   90,  180)),  # 1 — blue
    ((0,   200, 200), (0,   130, 140)),  # 2 — cyan
    ((20,  190,  90), (0,   130,  55)),  # 3 — emerald
    ((160,  60, 230), (100,  20, 170)),  # 4 — purple
    ((230, 120,  20), (170,  70,   0)),  # 5 — orange
    ((230,  50, 150), (170,  10, 100)),  # 6 — pink
    ((220,  40,  40), (160,  10,  10)),  # 7 — red
    ((220, 190,   0), (160, 130,   0)),  # 8 — gold
]


def _pond_colors_for_level(level):
    return _POND_PALETTE[(level - 1) % len(_POND_PALETTE)]

# HUD mute button
_MUTE_RECT = pygame.Rect(SCREEN_WIDTH - 90, 10, 80, 38)

# Title screen "Ready to Start" button
_READY_RECT = pygame.Rect(200, 400, 200, 54)

# Character select cards  — 160×240 each, 30 px margins/gaps
_CHAR_CARDS = {
    "turtle": pygame.Rect( 30, 130, 160, 240),
    "frog":   pygame.Rect(220, 130, 160, 240),
    "beaver": pygame.Rect(410, 130, 160, 240),
}


class Game:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen     = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turtle Frogger")
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.SysFont("Arial", 28, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self._running          = True
        self.state             = "title"
        self.selected_character = "turtle"

        # Game objects — populated in _start_game()
        self.level    = 1
        self.player   = None
        self.vehicles = []
        self.powerup  = None

        music.init()

    # ── State transitions ─────────────────────────────────────

    def _start_game(self):
        """Enter playing state after character selection."""
        self.level    = 1
        self.player   = TurtlePlayer(character=self.selected_character)
        self.vehicles = make_vehicles(self.level)
        self.powerup  = PowerUp()
        pygame.display.set_caption(
            f"{self.selected_character.capitalize()} Frogger"
        )
        self.state = "playing"

    def _restart_after_game_over(self):
        """Restart game keeping same character; skip title/select."""
        self.level    = 1
        self.player   = TurtlePlayer(character=self.selected_character)
        self.vehicles = make_vehicles(self.level)
        self.powerup  = PowerUp()
        music.init()
        self.state = "playing"

    # ── Title screen ──────────────────────────────────────────

    def _draw_title(self, mouse_pos):
        self.screen.fill((10, 30, 10))

        # Background road lanes (dimmed)
        for row in range(1, 9):
            ry = row * GRID_SIZE + 60
            pygame.draw.rect(self.screen, (22, 22, 22), (0, ry, SCREEN_WIDTH, GRID_SIZE))
            pygame.draw.rect(self.screen, (40, 40, 40), (0, ry + GRID_SIZE - 2, SCREEN_WIDTH, 2))

        # Ponds top and bottom
        self._draw_pond()
        self._draw_start_pond()

        # Dark vignette so text is readable over the background
        veil = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        veil.set_alpha(140)
        veil.fill(BLACK)
        self.screen.blit(veil, (0, 0))

        # Redraw ponds over veil so they still glow
        self._draw_pond()
        self._draw_start_pond()

        # Game title
        title = self.title_font.render("TURTLE FROGGER", True, YELLOW)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 195))

        sub = self.small_font.render(
            "Cross the road.  Reach the pond.", True, (180, 220, 180)
        )
        self.screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 275))

        # Ready to Start button
        hovered  = _READY_RECT.collidepoint(mouse_pos)
        btn_col  = (80, 170, 80) if hovered else (40, 110, 40)
        pygame.draw.rect(self.screen, btn_col,  _READY_RECT, border_radius=12)
        pygame.draw.rect(self.screen, WHITE,    _READY_RECT, 3, border_radius=12)
        btn_txt = self.font.render("Ready to Start", True, WHITE)
        self.screen.blit(btn_txt, (
            _READY_RECT.centerx - btn_txt.get_width()  // 2,
            _READY_RECT.centery - btn_txt.get_height() // 2,
        ))

        pygame.display.flip()

    # ── Character select screen ───────────────────────────────

    def _draw_character_select(self, mouse_pos):
        self.screen.fill((12, 35, 12))

        heading = self.title_font.render("Choose Your Character", True, WHITE)
        self.screen.blit(heading, (SCREEN_WIDTH // 2 - heading.get_width() // 2, 45))

        for char, rect in _CHAR_CARDS.items():
            hovered    = rect.collidepoint(mouse_pos)
            bg_col     = (60, 100, 60) if hovered else (35, 60, 35)
            border_col = YELLOW        if hovered else (100, 160, 100)

            pygame.draw.rect(self.screen, bg_col,     rect, border_radius=14)
            pygame.draw.rect(self.screen, border_col, rect, 3, border_radius=14)

            # Character preview: draw 60×60 sprite onto a surface, scale 2×
            prev = pygame.Surface((60, 60))
            prev.fill(bg_col)
            TurtlePlayer.draw_preview(prev, char, 0, 0)
            scaled = pygame.transform.scale(prev, (120, 120))
            self.screen.blit(scaled, (
                rect.x + (rect.width - 120) // 2,
                rect.y + 20,
            ))

            # Character name
            name_surf = self.font.render(char.capitalize(), True, WHITE)
            self.screen.blit(name_surf, (
                rect.centerx - name_surf.get_width() // 2,
                rect.y + 155,
            ))

            # Hover hint
            if hovered:
                hint = self.small_font.render("Click to select", True, YELLOW)
                self.screen.blit(hint, (
                    rect.centerx - hint.get_width() // 2,
                    rect.y + 195,
                ))

        pygame.display.flip()

    # ── Game drawing helpers ──────────────────────────────────

    def _draw_road_lanes(self):
        for row in range(1, 9):
            y = row * GRID_SIZE + 60
            pygame.draw.rect(self.screen, (30, 30, 30), (0, y, SCREEN_WIDTH, GRID_SIZE))
            for dx in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(self.screen, WHITE, (dx, y + 2, 20, 4))
            pygame.draw.rect(self.screen, WHITE, (0, y + GRID_SIZE - 3, SCREEN_WIDTH, 3))

    def _draw_pond(self):
        y = 60
        pond, ripple = _pond_colors_for_level(self.level)
        pygame.draw.rect(self.screen, pond, (0, y, SCREEN_WIDTH, GRID_SIZE))
        for i in range(4):
            rx = 80 + i * 130
            pygame.draw.ellipse(self.screen, ripple, (rx - 35, y + 10, 70, 40), 2)
            pygame.draw.ellipse(self.screen, ripple, (rx - 20, y + 18, 40, 22), 2)
        for lx in [50, 170, 300, 430, 550]:
            pygame.draw.ellipse(self.screen, LILY_GREEN, (lx - 15, y + 15, 30, 22))
            pygame.draw.polygon(self.screen, pond,       [(lx, y + 26), (lx - 6, y + 15), (lx + 6, y + 15)])
            pygame.draw.circle(self.screen,  WHITE,      (lx, y + 26), 4)
            pygame.draw.circle(self.screen,  YELLOW,     (lx, y + 26), 2)
        txt = self.small_font.render("🐸  SWIM TO SAFETY  🐸", True, WHITE)
        self.screen.blit(txt, (SCREEN_WIDTH // 2 - 100, y + 38))

    def _draw_start_pond(self):
        y = 9 * GRID_SIZE + 60
        pond, ripple = _pond_colors_for_level(self.level)
        pygame.draw.rect(self.screen, pond, (0, y, SCREEN_WIDTH, GRID_SIZE))
        for i in range(4):
            rx = 80 + i * 130
            pygame.draw.ellipse(self.screen, ripple, (rx - 35, y + 10, 70, 40), 2)
            pygame.draw.ellipse(self.screen, ripple, (rx - 20, y + 18, 40, 22), 2)
        for lx in [50, 170, 300, 430, 550]:
            pygame.draw.ellipse(self.screen, LILY_GREEN, (lx - 15, y + 15, 30, 22))
            pygame.draw.polygon(self.screen, pond,       [(lx, y + 26), (lx - 6, y + 15), (lx + 6, y + 15)])
            pygame.draw.circle(self.screen,  WHITE,      (lx, y + 26), 4)
            pygame.draw.circle(self.screen,  YELLOW,     (lx, y + 26), 2)
        txt = self.small_font.render("🐢  START HERE  🐢", True, WHITE)
        self.screen.blit(txt, (SCREEN_WIDTH // 2 - 90, y + 38))

    def _draw_hud(self):
        p = self.player
        pygame.draw.rect(self.screen, GRAY, (0, 0, SCREEN_WIDTH, 60))
        self.screen.blit(self.font.render(f"Score: {p.score}", True, WHITE), (10, 15))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE), (200, 15))
        for i in range(p.lives):
            self.screen.blit(self.small_font.render("♥", True, RED), (340 + i * 22, 18))
        if p.invincible:
            txt = self.small_font.render(
                f"INVINCIBLE! {(p.inv_timer + 59) // 60}s", True, YELLOW
            )
            self.screen.blit(txt, (200, 38))
        btn_color = DARK_GRAY if music.is_muted() else (60, 120, 60)
        pygame.draw.rect(self.screen, btn_color, _MUTE_RECT, border_radius=6)
        pygame.draw.rect(self.screen, WHITE,     _MUTE_RECT, 2, border_radius=6)
        label = "MUTED" if music.is_muted() else "MUSIC"
        self.screen.blit(self.small_font.render(label, True, WHITE),
                         (_MUTE_RECT.x + 10, _MUTE_RECT.y + 10))

    def _draw_level_up(self):
        txt = self.font.render("LEVEL UP!", True, YELLOW)
        self.screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, 130))

    def _draw(self):
        self.screen.fill(BLACK)
        self._draw_pond()
        self._draw_road_lanes()
        self._draw_start_pond()
        for v in self.vehicles:
            v.draw(self.screen)
        self.powerup.draw(self.screen, self.font)
        self.player.draw(self.screen)
        if self.player.celebrating:
            self._draw_level_up()
        self._draw_hud()
        pygame.display.flip()

    # ── Game-over screen ──────────────────────────────────────

    async def _game_over(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.font.render("GAME OVER", True, RED),
                         (SCREEN_WIDTH // 2 - 80, 250))
        self.screen.blit(self.font.render(f"Final Score: {self.player.score}", True, WHITE),
                         (SCREEN_WIDTH // 2 - 90, 310))
        self.screen.blit(self.small_font.render("Restarting...", True, GRAY),
                         (SCREEN_WIDTH // 2 - 55, 370))
        pygame.display.flip()
        music.stop()
        for _ in range(4 * FPS):
            await asyncio.sleep(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    return
        self._restart_after_game_over()

    # ── Main loop ─────────────────────────────────────────────

    async def run(self):
        while self._running:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()

            if self.state == "title":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False
                    music.handle_event(event)
                    if event.key == pygame.K_m if event.type == pygame.KEYDOWN else False:
                        music.toggle_mute()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if _READY_RECT.collidepoint(event.pos):
                            self.state = "select"
                self._draw_title(mouse_pos)

            elif self.state == "select":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False
                    music.handle_event(event)
                    if event.key == pygame.K_m if event.type == pygame.KEYDOWN else False:
                        music.toggle_mute()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        for char, rect in _CHAR_CARDS.items():
                            if rect.collidepoint(event.pos):
                                self.selected_character = char
                                self._start_game()
                                break
                self._draw_character_select(mouse_pos)

            elif self.state == "playing":
                p = self.player
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False
                    music.handle_event(event)
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            music.toggle_mute()
                        if not p.flashing and not p.celebrating:
                            if   event.key == pygame.K_UP:    p.move("up")
                            elif event.key == pygame.K_DOWN:  p.move("down")
                            elif event.key == pygame.K_LEFT:  p.move("left")
                            elif event.key == pygame.K_RIGHT: p.move("right")
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if _MUTE_RECT.collidepoint(event.pos):
                            music.toggle_mute()

                for v in self.vehicles:
                    v.update()
                p.update()
                self.powerup.update()

                if self.powerup.check_collect(p.x, p.y):
                    p.activate_invincibility()
                    self.powerup.reset()

                if not p.invincible and not p.flashing and not p.celebrating:
                    t_rect = p.get_rect()
                    if any(t_rect.colliderect(v.get_rect()) for v in self.vehicles):
                        p.take_hit()
                        if p.lives <= 0:
                            await self._game_over()

                if p.y == 0 and not p.celebrating:
                    p.score += 100
                    p.celebrate()

                if p.celebrating and p.celebrate_timer <= 0:
                    p.celebrating = False
                    self.level   += 1
                    self.vehicles = make_vehicles(self.level)
                    p.reset_position()

                self._draw()

            await asyncio.sleep(0)
