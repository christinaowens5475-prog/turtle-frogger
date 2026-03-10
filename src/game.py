import pygame
import sys

from .turtle_player import TurtlePlayer
from .obstavle import make_vehicles, PowerUp

SCREEN_WIDTH  = 600
SCREEN_HEIGHT = 660
GRID_SIZE     = 60
FPS           = 60

WHITE      = (255, 255, 255)
YELLOW     = (255, 220, 0)
BLACK      = (0, 0, 0)
RED        = (200, 30, 30)
GRAY       = (50, 50, 50)
POND_BLUE  = (30, 144, 255)
POND_DARK  = (0, 90, 180)
LILY_GREEN = (0, 160, 60)


class Game:
    def __init__(self):
        pygame.init()
        self.screen     = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Turtle Frogger")
        self.clock      = pygame.time.Clock()
        self.font       = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20)

        self.level    = 1
        self.player   = TurtlePlayer()
        self.vehicles = make_vehicles(self.level)
        self.powerup  = PowerUp()

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

    def _draw_hud(self):
        p = self.player
        pygame.draw.rect(self.screen, GRAY, (0, 0, SCREEN_WIDTH, 60))
        self.screen.blit(self.font.render(f"Score: {p.score}", True, WHITE), (10, 15))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE), (220, 15))
        for i in range(p.lives):
            self.screen.blit(self.small_font.render("♥", True, RED), (422 + i * 35, 18))
        if p.invincible:
            txt = self.small_font.render(f"INVINCIBLE! {p.inv_timer // 60 + 1}s", True, YELLOW)
            self.screen.blit(txt, (SCREEN_WIDTH // 2 - 70, 35))

    def _draw(self):
        self.screen.fill(BLACK)
        self._draw_pond()
        self._draw_road_lanes()
        for v in self.vehicles:
            v.draw(self.screen)
        self.powerup.draw(self.screen, self.font)
        p = self.player
        if not p.flashing or p.flash_timer % 10 < 5:
            p.draw(self.screen)
        self._draw_hud()
        pygame.display.flip()

    # ── Game-over screen ──────────────────────────────────────

    def _game_over(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.font.render("GAME OVER",                   True, RED),   (SCREEN_WIDTH // 2 - 80,  250))
        self.screen.blit(self.font.render(f"Final Score: {self.player.score}", True, WHITE), (SCREEN_WIDTH // 2 - 90,  310))
        self.screen.blit(self.small_font.render("Close and rerun to play again!", True, GRAY), (SCREEN_WIDTH // 2 - 130, 370))
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()

    # ── Main loop ─────────────────────────────────────────────

    def run(self):
        while True:
            self.clock.tick(FPS)
            p = self.player

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and not p.flashing:
                    if   event.key == pygame.K_UP:    p.move("up")
                    elif event.key == pygame.K_DOWN:  p.move("down")
                    elif event.key == pygame.K_LEFT:  p.move("left")
                    elif event.key == pygame.K_RIGHT: p.move("right")

            # Update
            for v in self.vehicles:
                v.update()
            p.update()
            self.powerup.update()

            # Power-up collection
            if self.powerup.check_collect(p.x, p.y):
                p.activate_invincibility()
                self.powerup.reset()

            # Collision
            if not p.invincible and not p.flashing:
                t_rect = p.get_rect()
                if any(t_rect.colliderect(v.get_rect()) for v in self.vehicles):
                    p.take_hit()
                    if p.lives <= 0:
                        self._game_over()

            # Goal reached
            if p.y == 0:
                p.score += 100
                self.level += 1
                self.vehicles = make_vehicles(self.level)
                p.reset_position()

            self._draw()
