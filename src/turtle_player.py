import math
import pygame

GRID_SIZE = 60

GREEN        = (34,  139, 34)
YELLOW       = (255, 220, 0)
WHITE        = (255, 255, 255)
BLACK        = (0,   0,   0)
PINK         = (255, 182, 193)
ORANGE       = (255, 140, 0)
FROG_GREEN   = (50,  170, 50)
FROG_LIGHT   = (160, 220, 100)
BEAVER_BROWN = (139, 90,  43)
BEAVER_DARK  = (90,  55,  20)

CELEBRATE_DURATION = 180

_BASE_COLORS = {"turtle": GREEN, "frog": FROG_GREEN, "beaver": BEAVER_BROWN}


class TurtlePlayer:
    def __init__(self, character="turtle"):
        self.character = character
        self.x = 5
        self.y = 9
        self.lives = 5
        self.score = 0
        self.invincible      = False
        self.inv_timer       = 0
        self.flashing        = False
        self.flash_timer     = 0
        self.celebrating     = False
        self.celebrate_timer = 0

    def move(self, direction):
        if direction == "up" and self.y > 0:
            self.y -= 1
            self.score += 10
        elif direction == "down" and self.y < 9:
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
            return

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

    def _body_color(self):
        return PINK if self.invincible else _BASE_COLORS.get(self.character, GREEN)

    def _draw_normal(self, surface):
        x = self.x * GRID_SIZE
        y = self.y * GRID_SIZE + 60
        c = self._body_color()
        if self.character == "frog":
            TurtlePlayer._draw_frog_at(surface, x, y, c)
        elif self.character == "beaver":
            TurtlePlayer._draw_beaver_at(surface, x, y, c)
        else:
            TurtlePlayer._draw_turtle_at(surface, x, y, c)

    def _draw_celebrating(self, surface):
        t  = self.celebrate_timer
        bx = self.x * GRID_SIZE + 30
        by = self.y * GRID_SIZE + 60 + 30

        bounce = int(math.sin(t * 0.25) * 10)
        wiggle = int(math.sin(t * 0.18) * 7)
        cx = bx + wiggle
        cy = by + bounce
        color = _BASE_COLORS.get(self.character, GREEN)

        limbs = [
            (cx - 22 + int( math.sin(t * 0.30) * 8), cy + 4),
            (cx + 22 + int(-math.sin(t * 0.30) * 8), cy + 4),
            (cx - 8,  cy + 22 + int( math.cos(t * 0.30) * 8)),
            (cx + 8,  cy + 22 + int(-math.cos(t * 0.30) * 8)),
        ]
        for (lx, ly) in limbs:
            pygame.draw.ellipse(surface, color, (lx - 9, ly - 6, 18, 12))

        pygame.draw.ellipse(surface, color,  (cx - 20, cy - 20, 40, 40))
        pygame.draw.ellipse(surface, YELLOW, (cx - 15, cy - 15, 30, 30))

        hy = cy - 23 + int(math.sin(t * 0.40) * 3)
        pygame.draw.circle(surface, color, (cx, hy), 9)
        pygame.draw.circle(surface, BLACK, (cx - 3, hy - 2), 2)
        pygame.draw.circle(surface, BLACK, (cx + 3, hy - 2), 2)
        pygame.draw.arc(surface, BLACK, (cx - 5, hy + 1, 10, 6),
                        math.pi, 2 * math.pi, 2)

        for i in range(8):
            angle = math.radians(i * 45 + t * 5)
            r     = 32 + int(math.sin(t * 0.2 + i) * 5)
            sx    = cx + int(math.cos(angle) * r)
            sy    = cy + int(math.sin(angle) * r)
            size  = 3 + int(math.sin(t * 0.35 + i) * 2)
            col   = YELLOW if i % 2 == 0 else ORANGE
            pygame.draw.circle(surface, col, (sx, sy), max(1, size))

    def reset_position(self):
        self.x = 5
        self.y = 9

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

    # ── Static sprite helpers (used by _draw_normal and draw_preview) ─────

    @staticmethod
    def draw_preview(surface, character, x, y):
        """Draw character into a 60×60 cell with top-left at pixel (x, y)."""
        color = _BASE_COLORS.get(character, GREEN)
        if character == "frog":
            TurtlePlayer._draw_frog_at(surface, x, y, color)
        elif character == "beaver":
            TurtlePlayer._draw_beaver_at(surface, x, y, color)
        else:
            TurtlePlayer._draw_turtle_at(surface, x, y, color)

    @staticmethod
    def _draw_turtle_at(surface, x, y, color):
        pygame.draw.ellipse(surface, color,  (x + 10, y + 10, 40, 40))
        pygame.draw.ellipse(surface, YELLOW, (x + 15, y + 15, 30, 30))
        pygame.draw.circle(surface,  color,  (x + 30, y +  5),  8)
        pygame.draw.circle(surface,  BLACK,  (x + 27, y +  3),  2)
        pygame.draw.circle(surface,  BLACK,  (x + 33, y +  3),  2)

    @staticmethod
    def _draw_frog_at(surface, x, y, color):
        # Wide flat body
        pygame.draw.ellipse(surface, color,      (x +  5, y + 22, 50, 26))
        # Belly highlight
        pygame.draw.ellipse(surface, FROG_LIGHT, (x + 12, y + 26, 36, 18))
        # Eye bulges
        pygame.draw.circle(surface, color, (x + 15, y + 18), 10)
        pygame.draw.circle(surface, color, (x + 45, y + 18), 10)
        # Pupils
        pygame.draw.circle(surface, BLACK, (x + 15, y + 16),  6)
        pygame.draw.circle(surface, BLACK, (x + 45, y + 16),  6)
        # Eye shine
        pygame.draw.circle(surface, WHITE, (x + 12, y + 13),  2)
        pygame.draw.circle(surface, WHITE, (x + 42, y + 13),  2)
        # Smile
        pygame.draw.arc(surface, BLACK,
                        pygame.Rect(x + 19, y + 30, 22, 10),
                        math.pi, 2 * math.pi, 2)

    @staticmethod
    def _draw_beaver_at(surface, x, y, color):
        # Flat leathery tail at bottom
        pygame.draw.ellipse(surface, BEAVER_DARK, (x +  8, y + 46, 44, 12))
        # Body
        pygame.draw.ellipse(surface, color,        (x + 10, y + 22, 40, 26))
        # Head
        pygame.draw.circle(surface, color,         (x + 30, y + 18), 14)
        # Ears (dark inner)
        pygame.draw.circle(surface, color,       (x + 18, y +  7), 6)
        pygame.draw.circle(surface, BEAVER_DARK, (x + 18, y +  7), 4)
        pygame.draw.circle(surface, color,       (x + 42, y +  7), 6)
        pygame.draw.circle(surface, BEAVER_DARK, (x + 42, y +  7), 4)
        # Eyes
        pygame.draw.circle(surface, BLACK, (x + 24, y + 14), 3)
        pygame.draw.circle(surface, BLACK, (x + 36, y + 14), 3)
        pygame.draw.circle(surface, WHITE, (x + 23, y + 13), 1)
        pygame.draw.circle(surface, WHITE, (x + 35, y + 13), 1)
        # Nose
        pygame.draw.ellipse(surface, BEAVER_DARK, (x + 27, y + 21, 6, 4))
        # Buck teeth
        pygame.draw.rect(surface, WHITE,       (x + 24, y + 24, 6, 8), border_radius=2)
        pygame.draw.rect(surface, WHITE,       (x + 31, y + 24, 6, 8), border_radius=2)
        pygame.draw.line(surface, BEAVER_DARK, (x + 30, y + 24), (x + 30, y + 32), 1)
