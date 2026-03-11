import math
import pygame

GRID_SIZE = 60

GREEN  = (34, 139, 34)
YELLOW = (255, 220, 0)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
PINK   = (255, 182, 193)
ORANGE = (255, 140, 0)

CELEBRATE_DURATION = 180   # 3 seconds at 60 fps


class TurtlePlayer:
    def __init__(self):
        self.x = 5
        self.y = 10
        self.lives = 5
        self.score = 0
        self.invincible    = False
        self.inv_timer     = 0
        self.flashing      = False
        self.flash_timer   = 0
        self.celebrating   = False
        self.celebrate_timer = 0

    def move(self, direction):
        if direction == "up" and self.y > 0:
            self.y -= 1
            self.score += 10
        elif direction == "down" and self.y < 10:
            self.y += 1
        elif direction == "left" and self.x > 0:
            self.x -= 1
        elif direction == "right" and self.x < 9:
            self.x += 1

    def celebrate(self):
        self.celebrating     = True
        self.celebrate_timer = CELEBRATE_DURATION

    def update(self):
        if self.celebrating:
            self.celebrate_timer -= 1
            return   # freeze all other state while dancing

        if self.invincible:
            self.inv_timer -= 1
            if self.inv_timer <= 0:
                self.invincible = False
        if self.flashing:
            self.flash_timer -= 1
            if self.flash_timer <= 0:
                self.flashing = False
                self.reset_position()

    def draw(self, surface):
        if self.celebrating:
            self._draw_celebrating(surface)
        elif not self.flashing or self.flash_timer % 10 < 5:
            self._draw_normal(surface)

    # ── Normal drawing ────────────────────────────────────────

    def _draw_normal(self, surface):
        x = self.x * GRID_SIZE
        y = self.y * GRID_SIZE + 60
        color = PINK if self.invincible else GREEN
        pygame.draw.ellipse(surface, color,  (x + 10, y + 10, 40, 40))
        pygame.draw.ellipse(surface, YELLOW, (x + 15, y + 15, 30, 30))
        pygame.draw.circle(surface,  color,  (x + 30, y + 5), 8)
        pygame.draw.circle(surface,  BLACK,  (x + 27, y + 3), 2)
        pygame.draw.circle(surface,  BLACK,  (x + 33, y + 3), 2)

    # ── Celebration dancing ───────────────────────────────────

    def _draw_celebrating(self, surface):
        t  = self.celebrate_timer
        bx = self.x * GRID_SIZE + 30
        by = self.y * GRID_SIZE + 60 + 30

        # Bounce + side-to-side wiggle
        bounce = int(math.sin(t * 0.25) * 10)
        wiggle = int(math.sin(t * 0.18) * 7)
        cx = bx + wiggle
        cy = by + bounce

        # 4 wiggling limbs
        limbs = [
            (cx - 22 + int( math.sin(t * 0.30) * 8), cy + 4),
            (cx + 22 + int(-math.sin(t * 0.30) * 8), cy + 4),
            (cx - 8,  cy + 22 + int( math.cos(t * 0.30) * 8)),
            (cx + 8,  cy + 22 + int(-math.cos(t * 0.30) * 8)),
        ]
        for (lx, ly) in limbs:
            pygame.draw.ellipse(surface, GREEN, (lx - 9, ly - 6, 18, 12))

        # Shell body
        pygame.draw.ellipse(surface, GREEN,  (cx - 20, cy - 20, 40, 40))
        pygame.draw.ellipse(surface, YELLOW, (cx - 15, cy - 15, 30, 30))

        # Head with happy smile
        hy = cy - 23 + int(math.sin(t * 0.40) * 3)
        pygame.draw.circle(surface, GREEN, (cx, hy), 9)
        pygame.draw.circle(surface, BLACK, (cx - 3, hy - 2), 2)
        pygame.draw.circle(surface, BLACK, (cx + 3, hy - 2), 2)
        pygame.draw.arc(surface, BLACK, (cx - 5, hy + 1, 10, 6),
                        math.pi, 2 * math.pi, 2)   # smile

        # Orbiting sparkles (8, alternating yellow/orange)
        for i in range(8):
            angle = math.radians(i * 45 + t * 5)
            r     = 32 + int(math.sin(t * 0.2 + i) * 5)
            sx    = cx + int(math.cos(angle) * r)
            sy    = cy + int(math.sin(angle) * r)
            size  = 3 + int(math.sin(t * 0.35 + i) * 2)
            color = YELLOW if i % 2 == 0 else ORANGE
            pygame.draw.circle(surface, color, (sx, sy), max(1, size))

    def reset_position(self):
        self.x = 5
        self.y = 10

    def take_hit(self):
        self.lives -= 1
        self.flashing    = True
        self.flash_timer = 90

    def activate_invincibility(self):
        self.invincible = True
        self.inv_timer  = 300

    def get_rect(self):
        return pygame.Rect(
            self.x * GRID_SIZE + 8,
            self.y * GRID_SIZE + 60 + 8,
            44, 44
        )
