import pygame
import random

SCREEN_WIDTH = 600
GRID_SIZE    = 60

RED        = (200, 30, 30)
TRUCK_BLUE = (30, 60, 200)
WHITE      = (255, 255, 255)
PURPLE     = (148, 0, 211)
YELLOW     = (255, 220, 0)


class Vehicle:
    def __init__(self, x, row, w, h, speed, color, is_truck):
        self.x        = x
        self.row      = row
        self.w        = w
        self.h        = h
        self.speed    = speed
        self.color    = color
        self.is_truck = is_truck

    def update(self):
        self.x += self.speed
        if self.speed > 0 and self.x > SCREEN_WIDTH:
            self.x = -self.w
        elif self.speed < 0 and self.x + self.w < 0:
            self.x = SCREEN_WIDTH

    def draw(self, surface):
        y = self.row * GRID_SIZE + 60 + (GRID_SIZE - self.h) // 2
        pygame.draw.rect(surface, self.color, (self.x, y, self.w, self.h), border_radius=8)
        if self.is_truck:
            pygame.draw.rect(surface, WHITE, (self.x + 5,          y + 5, 20, self.h - 10), border_radius=3)
            pygame.draw.rect(surface, WHITE, (self.x + self.w - 25, y + 5, 20, self.h - 10), border_radius=3)
        else:
            pygame.draw.rect(surface, WHITE, (self.x + 8, y + 6, 15, self.h - 14), border_radius=3)

    def get_rect(self):
        y = self.row * GRID_SIZE + 60 + (GRID_SIZE - self.h) // 2
        return pygame.Rect(self.x, y, self.w, self.h)


class PowerUp:
    def __init__(self):
        self._spawn()
        self.spawn_timer = 600

    def _spawn(self):
        self.x      = random.randint(0, 9)
        self.y      = random.randint(1, 9)
        self.active = True
        self.timer  = 300

    def update(self):
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active      = False
                self.spawn_timer = 600
        else:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                self._spawn()

    def draw(self, surface, font):
        if not self.active:
            return
        px = self.x * GRID_SIZE + GRID_SIZE // 2
        py = self.y * GRID_SIZE + 60 + GRID_SIZE // 2
        pygame.draw.circle(surface, PURPLE, (px, py), 16)
        heart = font.render("♥", True, WHITE)
        surface.blit(heart, (px - 10, py - 14))

    def check_collect(self, tx, ty):
        return self.active and tx == self.x and ty == self.y

    def reset(self):
        self.active      = False
        self.spawn_timer = 600


def make_vehicles(level):
    spd      = 1 + (level - 1) * 0.3
    vehicles = []
    for row in range(1, 10):
        direction = 1 if row % 2 == 0 else -1
        count     = random.randint(2, 4)
        spacing   = SCREEN_WIDTH // count
        is_truck  = (row % 3 == 0)
        color     = TRUCK_BLUE if is_truck else RED
        w         = 90 if is_truck else 50
        h         = 40
        lane_spd  = round(spd * direction * random.uniform(0.8, 1.2), 2)
        for i in range(count):
            vehicles.append(Vehicle(i * spacing, row, w, h, lane_spd, color, is_truck))
    return vehicles
