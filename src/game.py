import asyncio
import pygame

from .turtle_player import TurtlePlayer
from .obstavle import make_vehicles, PowerUp
from . import music

SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 660
GRID_SIZE     = 60
FPS           = 60

WHITE        = (255, 255, 255)
YELLOW       = (255, 220, 0)
BLACK        = (0, 0, 0)
RED          = (200, 30, 30)
GRAY         = (50, 50, 50)
DARK_GRAY    = (80, 80, 80)
POND_BLUE    = (30, 144, 255)
POND_DARK    = (0, 90, 180)
LILY_GREEN   = (0, 160, 60)
START_GREEN  = (0, 180, 80)

# Mute button rect (top-right of HUD)
_MUTE_RECT = pygame.Rect(SCREEN_WIDTH - 90, 10, 80, 38)


class Game:
    def __init__(self):
        pygame.init()
        self.screen     = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turtle Frogger")
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self._running = True
        self.level    = 1
        self.player   = TurtlePlayer()
        self.vehicles = make_vehicles(self.level)
        self.powerup  = PowerUp()
        music.init()

    # ── Drawing helpers ───────────────────────────────────────

    def _draw_road_lanes(self):
        for row in range(1, 11):
            y = row * GRID_SIZE + 60
            pygame.draw.rect(self.screen, (30, 30, 30), (0, y, SCREEN_WIDTH, GRID_SIZE))
            for dx in range(0, SCREEN_WIDTH, 40):
                pygame.draw.rect(self.screen, WHITE, (dx, y + 2, 20, 4))
            pygame.draw.rect(self.screen, WHITE, (0, y + GRID_SIZE - 3, SCREEN_WIDTH, 3))

    def _draw_pond(self):
        y = 60
        pygame.draw.rect(self.screen, POND_BLUE, (0, y, SCREEN_WIDTH, GRID_SIZE))
        for i in range(4):
            rx = 80 + i * 130
            pygame.draw.ellipse(self.screen, POND_DARK, (rx - 35, y + 10, 70, 40), 2)
            pygame.draw.ellipse(self.screen, POND_DARK, (rx - 20, y + 18, 40, 22), 2)
        for lx in [50, 170, 300, 430, 550]:
            pygame.draw.ellipse(self.screen, LILY_GREEN, (lx - 15, y + 15, 30, 22))
            pygame.draw.polygon(self.screen, POND_BLUE,  [(lx, y + 26), (lx - 6, y + 15), (lx + 6, y + 15)])
            pygame.draw.circle(self.screen,  WHITE,      (lx, y + 26), 4)
            pygame.draw.circle(self.screen,  YELLOW,     (lx, y + 26), 2)
        txt = self.small_font.render("🐸  SWIM TO SAFETY  🐸", True, WHITE)
        self.screen.blit(txt, (SCREEN_WIDTH // 2 - 100, y + 38))

    def _draw_start_zone(self):
        sx = 5 * GRID_SIZE
        sy = 10 * GRID_SIZE + 60
        pygame.draw.rect(self.screen, START_GREEN, (sx, sy, GRID_SIZE, GRID_SIZE), border_radius=6)
        pygame.draw.rect(self.screen, YELLOW,      (sx, sy, GRID_SIZE, GRID_SIZE), 3, border_radius=6)
        lbl = self.small_font.render("START", True, WHITE)
        self.screen.blit(lbl, (sx + GRID_SIZE // 2 - lbl.get_width() // 2, sy + GRID_SIZE // 2 - lbl.get_height() // 2))

    def _draw_hud(self):
        p = self.player
        pygame.draw.rect(self.screen, GRAY, (0, 0, SCREEN_WIDTH, 60))
        self.screen.blit(self.font.render(f"Score: {p.score}", True, WHITE), (10, 15))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE), (200, 15))
        for i in range(p.lives):
            self.screen.blit(self.small_font.render("♥", True, RED), (340 + i * 22, 18))
        if p.invincible:
            txt = self.small_font.render(f"INVINCIBLE! {p.inv_timer // 60 + 1}s", True, YELLOW)
            self.screen.blit(txt, (200, 38))
        # Mute button
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
        self._draw_start_zone()
        for v in self.vehicles:
            v.draw(self.screen)
        self.powerup.draw(self.screen, self.font)
        self.player.draw(self.screen)
        if self.player.celebrating:
            self._draw_level_up()
        self._draw_hud()
        pygame.display.flip()

    # ── Game-over screen (async — no blocking calls) ──────────

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
        for _ in range(4 * FPS):   # show for 4 seconds without blocking
            await asyncio.sleep(0)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    return
        self.__init__()   # restart — avoids blank canvas in browser

    # ── Main loop (async — yields to browser every frame) ─────

    async def run(self):
        while self._running:
            self.clock.tick(FPS)
            p = self.player

            # Events
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

            # Update
            for v in self.vehicles:
                v.update()
            p.update()
            self.powerup.update()

            # Power-up collection
            if self.powerup.check_collect(p.x, p.y):
                p.activate_invincibility()
                self.powerup.reset()

            # Collision (skip while celebrating)
            if not p.invincible and not p.flashing and not p.celebrating:
                t_rect = p.get_rect()
                if any(t_rect.colliderect(v.get_rect()) for v in self.vehicles):
                    p.take_hit()
                    if p.lives <= 0:
                        await self._game_over()

            # Goal reached — start celebration
            if p.y == 0 and not p.celebrating:
                p.score += 100
                p.celebrate()

            # Celebration finished — advance level
            if p.celebrating and p.celebrate_timer <= 0:
                p.celebrating = False
                self.level   += 1
                self.vehicles = make_vehicles(self.level)
                p.reset_position()

            self._draw()
            await asyncio.sleep(0)   # yield to browser every frame
