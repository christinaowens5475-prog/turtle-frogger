import pygame

GRID_SIZE = 60

GREEN  = (34, 139, 34)
YELLOW = (255, 220, 0)
BLACK  = (0, 0, 0)
PINK   = (255, 182, 193)


class TurtlePlayer:
    def __init__(self):
        self.x = 5
        self.y = 10
        self.lives = 3
        self.score = 0
        self.invincible = False
        self.inv_timer = 0
        self.flashing = False
        self.flash_timer = 0

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

    def update(self):
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
        x = self.x * GRID_SIZE
        y = self.y * GRID_SIZE + 60
        color = PINK if self.invincible else GREEN
        pygame.draw.ellipse(surface, color,  (x + 10, y + 10, 40, 40))
        pygame.draw.ellipse(surface, YELLOW, (x + 15, y + 15, 30, 30))
        pygame.draw.circle(surface,  color,  (x + 30, y + 5), 8)
        pygame.draw.circle(surface,  BLACK,  (x + 27, y + 3), 2)
        pygame.draw.circle(surface,  BLACK,  (x + 33, y + 3), 2)

    def reset_position(self):
        self.x = 5
        self.y = 10

    def take_hit(self):
        self.lives -= 1
        self.flashing = True
        self.flash_timer = 90

    def activate_invincibility(self):
        self.invincible = True
        self.inv_timer = 300

    def get_rect(self):
        return pygame.Rect(
            self.x * GRID_SIZE + 8,
            self.y * GRID_SIZE + 60 + 8,
            44, 44
        )
