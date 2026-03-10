import pygame
import sys
import random

# ── Constants ──────────────────────────────────────────────
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 660
GRID_SIZE = 60
FPS = 60

# Colors
WHITE      = (255, 255, 255)
GREEN      = (34, 139, 34)
YELLOW     = (255, 220, 0)
BLACK      = (0, 0, 0)
RED        = (200, 30, 30)
TRUCK_BLUE = (30, 60, 200)
PURPLE     = (148, 0, 211)
GRAY       = (50, 50, 50)
PINK       = (255, 182, 193)
ROAD_BLACK = (30, 30, 30)
POND_BLUE  = (30, 144, 255)
POND_DARK  = (0, 90, 180)
LILY_GREEN = (0, 160, 60)

# ── Setup ───────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Turtle Frogger")
clock = pygame.time.Clock()
font       = pygame.font.SysFont("Arial", 28, bold=True)
small_font = pygame.font.SysFont("Arial", 20)

# ── Game State ──────────────────────────────────────────────
turtle_x    = 5
turtle_y    = 10
lives       = 3
score       = 0
level       = 1
invincible  = False
inv_timer   = 0
flash_timer = 0
flashing    = False

# ── Vehicles ────────────────────────────────────────────────
def make_vehicles(level):
    spd = 1 + (level - 1) * 0.3
    vehicles = []
    for row in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        direction = 1 if row % 2 == 0 else -1
        count = random.randint(2, 4)
        spacing = SCREEN_WIDTH // count
        is_truck = (row % 3 == 0)
        color = TRUCK_BLUE if is_truck else RED
        w = 90 if is_truck else 50
        h = 40
        lane_spd = round(spd * direction * random.uniform(0.8, 1.2), 2)
        for i in range(count):
            start_x = i * spacing
            vehicles.append([start_x, row, w, h, lane_spd, color, is_truck])
    return vehicles

vehicles = make_vehicles(level)

# ── Power-up ────────────────────────────────────────────────
def spawn_powerup():
    return {
        "x": random.randint(0, 9),
        "y": random.randint(1, 9),
        "active": True,
        "timer": 300
    }

powerup = spawn_powerup()
powerup_spawn_timer = 600

# ── Draw: Road Lanes ────────────────────────────────────────
def draw_road_lanes(surface):
    for row in range(1, 11):
        y = row * GRID_SIZE + 60
        # Black road base
        pygame.draw.rect(surface, ROAD_BLACK, (0, y, SCREEN_WIDTH, GRID_SIZE))
        # White dashed lane stripes at top of each lane
        dash_y = y + 2
        for dx in range(0, SCREEN_WIDTH, 40):
            pygame.draw.rect(surface, WHITE, (dx, dash_y, 20, 4))
        # Solid white line at bottom of each lane
        pygame.draw.rect(surface, WHITE, (0, y + GRID_SIZE - 3, SCREEN_WIDTH, 3))

# ── Draw: Pond Goal Zone ─────────────────────────────────────
def draw_pond(surface):
    y = 60
    # Pond background
    pygame.draw.rect(surface, POND_BLUE, (0, y, SCREEN_WIDTH, GRID_SIZE))

    # Ripple effect (concentric ovals)
    for i in range(4):
        ripple_x = 80 + i * 130
        pygame.draw.ellipse(surface, POND_DARK,
                            (ripple_x - 35, y + 10, 70, 40), 2)
        pygame.draw.ellipse(surface, POND_DARK,
                            (ripple_x - 20, y + 18, 40, 22), 2)

    # Lily pads
    lily_positions = [50, 170, 300, 430, 550]
    for lx in lily_positions:
        pygame.draw.ellipse(surface, LILY_GREEN,
                            (lx - 15, y + 15, 30, 22))
        # Lily pad notch
        pygame.draw.polygon(surface, POND_BLUE,
                            [(lx, y + 26), (lx - 6, y + 15), (lx + 6, y + 15)])
        # Small white flower
        pygame.draw.circle(surface, WHITE, (lx, y + 26), 4)
        pygame.draw.circle(surface, YELLOW, (lx, y + 26), 2)

    # "POND" label
    txt = small_font.render("🐸  SWIM TO SAFETY  🐸", True, WHITE)
    surface.blit(txt, (SCREEN_WIDTH // 2 - 100, y + 38))

# ── Draw: Turtle ────────────────────────────────────────────
def draw_turtle(surface, grid_x, grid_y, inv):
    x = grid_x * GRID_SIZE
    y = grid_y * GRID_SIZE + 60
    color = PINK if inv else GREEN
    pygame.draw.ellipse(surface, color,   (x+10, y+10, 40, 40))
    pygame.draw.ellipse(surface, YELLOW,  (x+15, y+15, 30, 30))
    pygame.draw.circle(surface,  color,   (x+30, y+5),  8)
    pygame.draw.circle(surface,  BLACK,   (x+27, y+3),  2)
    pygame.draw.circle(surface,  BLACK,   (x+33, y+3),  2)

# ── Draw: Vehicle ────────────────────────────────────────────
def draw_vehicle(surface, v):
    x, row, w, h, spd, color, is_truck = v
    y = row * GRID_SIZE + 60 + (GRID_SIZE - h) // 2
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=8)
    if is_truck:
        pygame.draw.rect(surface, WHITE, (x+5,    y+5, 20, h-10), border_radius=3)
        pygame.draw.rect(surface, WHITE, (x+w-25, y+5, 20, h-10), border_radius=3)
    else:
        pygame.draw.rect(surface, WHITE, (x+8, y+6, 15, h-14), border_radius=3)

# ── Draw: Power-up ───────────────────────────────────────────
def draw_powerup(surface, pu):
    if pu["active"]:
        px = pu["x"] * GRID_SIZE + GRID_SIZE // 2
        py = pu["y"] * GRID_SIZE + 60 + GRID_SIZE // 2
        pygame.draw.circle(surface, PURPLE, (px, py), 16)
        heart = font.render("♥", True, WHITE)
        surface.blit(heart, (px - 10, py - 14))

# ── Draw: HUD ────────────────────────────────────────────────
def draw_hud(surface, lives, score, level, inv, inv_timer):
    pygame.draw.rect(surface, GRAY, (0, 0, SCREEN_WIDTH, 60))
    score_txt = font.render(f"Score: {score}", True, WHITE)
    level_txt = font.render(f"Level: {level}", True, WHITE)
    surface.blit(score_txt, (10, 15))
    surface.blit(level_txt, (220, 15))
    for i in range(lives):
        heart = small_font.render("♥", True, RED)
        surface.blit(heart, (422 + i * 35, 18))
    if inv:
        inv_txt = small_font.render(f"INVINCIBLE! {inv_timer//60+1}s", True, YELLOW)
        surface.blit(inv_txt, (SCREEN_WIDTH//2 - 70, 35))

# ── Collision ────────────────────────────────────────────────
def check_collision(tx, ty, vehicles):
    t_rect = pygame.Rect(tx * GRID_SIZE + 8, ty * GRID_SIZE + 60 + 8, 44, 44)
    for v in vehicles:
        x, row, w, h, spd, color, is_truck = v
        v_rect = pygame.Rect(x, row * GRID_SIZE + 60 + (GRID_SIZE-h)//2, w, h)
        if t_rect.colliderect(v_rect):
            return True
    return False

def check_powerup(tx, ty, pu):
    if not pu["active"]:
        return False
    return tx == pu["x"] and ty == pu["y"]

# ── Main Game Loop ───────────────────────────────────────────
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and not flashing:
            if event.key == pygame.K_UP and turtle_y > 0:
                turtle_y -= 1
                score += 10
            if event.key == pygame.K_DOWN and turtle_y < 10:
                turtle_y += 1
            if event.key == pygame.K_LEFT and turtle_x > 0:
                turtle_x -= 1
            if event.key == pygame.K_RIGHT and turtle_x < 9:
                turtle_x += 1

    # Move vehicles
    for v in vehicles:
        v[0] += v[4]
        if v[4] > 0 and v[0] > SCREEN_WIDTH:
            v[0] = -v[2]
        elif v[4] < 0 and v[0] + v[2] < 0:
            v[0] = SCREEN_WIDTH

    # Invincibility timer
    if invincible:
        inv_timer -= 1
        if inv_timer <= 0:
            invincible = False

    # Flash timer
    if flashing:
        flash_timer -= 1
        if flash_timer <= 0:
            flashing = False
            turtle_x, turtle_y = 5, 10

    # Power-up timer
    if powerup["active"]:
        powerup["timer"] -= 1
        if powerup["timer"] <= 0:
            powerup["active"] = False
    else:
        powerup_spawn_timer -= 1
        if powerup_spawn_timer <= 0:
            powerup = spawn_powerup()
            powerup_spawn_timer = 600

    # Collect power-up
    if check_powerup(turtle_x, turtle_y, powerup):
        invincible  = True
        inv_timer   = 300
        powerup["active"] = False
        powerup_spawn_timer = 600

    # Check collision
    if not invincible and not flashing:
        if check_collision(turtle_x, turtle_y, vehicles):
            lives -= 1
            flashing    = True
            flash_timer = 90
            if lives <= 0:
                screen.fill(BLACK)
                go_txt = font.render("GAME OVER", True, RED)
                sc_txt = font.render(f"Final Score: {score}", True, WHITE)
                re_txt = small_font.render("Close and rerun to play again!", True, GRAY)
                screen.blit(go_txt, (SCREEN_WIDTH//2 - 80, 250))
                screen.blit(sc_txt, (SCREEN_WIDTH//2 - 90, 310))
                screen.blit(re_txt, (SCREEN_WIDTH//2 - 130, 370))
                pygame.display.flip()
                pygame.time.wait(4000)
                pygame.quit()
                sys.exit()

    # Goal reached
    if turtle_y == 0:
        score += 100
        level += 1
        vehicles = make_vehicles(level)
        turtle_x, turtle_y = 5, 10

    # ── Draw ─────────────────────────────────────────────────
    screen.fill(BLACK)
    draw_pond(screen)
    draw_road_lanes(screen)
    for v in vehicles:
        draw_vehicle(screen, v)
    draw_powerup(screen, powerup)
    if not flashing or flash_timer % 10 < 5:
        draw_turtle(screen, turtle_x, turtle_y, invincible)
    draw_hud(screen, lives, score, level, invincible, inv_timer)

    pygame.display.flip()
    