import pygame
import random

SCREEN_WIDTH  = 600
GRID_SIZE     = 60

RED           = (200, 30,  30)
TRUCK_BLUE    = (30,  60,  200)
SCHOOL_YELLOW = (255, 200, 0)
BUS_DARK      = (200, 150, 0)
WHITE         = (255, 255, 255)
BLACK         = (0,   0,   0)
PURPLE        = (148, 0,   211)
SKY_BLUE      = (135, 206, 235)


class Vehicle:
    def __init__(self, x, row, w, h, speed, vehicle_type):
        self.x            = x
        self.row          = row
        self.w            = w
        self.h            = h
        self.speed        = speed
        self.vehicle_type = vehicle_type   # 'car' | 'truck' | 'bus'

    def update(self):
        self.x += self.speed
        if self.speed > 0 and self.x > SCREEN_WIDTH:
            self.x = -self.w
        elif self.speed < 0 and self.x + self.w < 0:
            self.x = SCREEN_WIDTH

    def draw(self, surface):
        y = self.row * GRID_SIZE + 60 + (GRID_SIZE - self.h) // 2

        if self.vehicle_type == "bus":
            # Body
            pygame.draw.rect(surface, SCHOOL_YELLOW, (self.x, y, self.w, self.h), border_radius=6)
            # Hood / front cab (darker)
            hood_x = self.x + self.w - 18 if self.speed > 0 else self.x
            pygame.draw.rect(surface, BUS_DARK, (hood_x, y, 18, self.h), border_radius=6)
            # Windows (3 along the side)
            for i in range(3):
                wx = self.x + 8 + i * 30
                pygame.draw.rect(surface, SKY_BLUE, (wx, y + 5, 22, self.h - 16), border_radius=3)
            # Black bumper stripe
            pygame.draw.rect(surface, BLACK, (self.x, y + self.h - 6, self.w, 6), border_radius=6)

        elif self.vehicle_type == "truck":
            pygame.draw.rect(surface, TRUCK_BLUE, (self.x, y, self.w, self.h), border_radius=8)
            pygame.draw.rect(surface, WHITE, (self.x + 5,          y + 5, 20, self.h - 10), border_radius=3)
            pygame.draw.rect(surface, WHITE, (self.x + self.w - 25, y + 5, 20, self.h - 10), border_radius=3)

        else:  # car
            pygame.draw.rect(surface, RED, (self.x, y, self.w, self.h), border_radius=8)
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
        surface.blit(font.render("♥", True, WHITE), (px - 10, py - 14))

    def check_collect(self, tx, ty):
        return self.active and tx == self.x and ty == self.y

    def reset(self):
        self.active      = False
        self.spawn_timer = 600


_VEHICLE_SIZES = {"bus": (110, 44), "truck": (90, 40), "car": (50, 40)}


def make_vehicles(level):
    spd      = 1 + (level - 1) * 0.3
    vehicles = []

    for row in range(1, 10):
        direction = 1 if row % 2 == 0 else -1
        lane_spd  = round(spd * direction * random.uniform(0.8, 1.2), 2)

        # 0 or 1 extra car — keeps vehicle count at 2-3 so gaps stay generous:
        #   2 vehicles (bus+truck):       gap = (600-200)//2 = 200 px
        #   3 vehicles (bus+truck+car):   gap = (600-250)//3 = 116 px
        num_cars = random.randint(0, 1)
        types    = ["bus", "truck"] + ["car"] * num_cars
        random.shuffle(types)

        widths = [_VEHICLE_SIZES[t][0] for t in types]
        gap    = (SCREEN_WIDTH - sum(widths)) // len(types)

        x = 0
        for vtype, w in zip(types, widths):
            h = _VEHICLE_SIZES[vtype][1]
            vehicles.append(Vehicle(x, row, w, h, lane_spd, vtype))
            x += w + gap

    return vehicles
