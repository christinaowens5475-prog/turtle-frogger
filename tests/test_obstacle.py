"""Tests for Vehicle and PowerUp logic (no display required)."""
import pytest
from src.obstavle import Vehicle, PowerUp, make_vehicles, SCREEN_WIDTH, GRID_SIZE


@pytest.fixture
def car():
    return Vehicle(x=0, row=1, w=50, h=40, speed=2, vehicle_type="car")


@pytest.fixture
def car_rtl():
    return Vehicle(x=300, row=2, w=50, h=40, speed=-2, vehicle_type="car")


# Vehicle movement

def test_vehicle_moves_by_speed(car):
    car.x = 100
    car.update()
    assert car.x == 102


def test_vehicle_moves_rtl(car_rtl):
    car_rtl.update()
    assert car_rtl.x == 298


def test_vehicle_wraps_right(car):
    car.x = SCREEN_WIDTH + 1
    car.update()
    assert car.x == -car.w


def test_vehicle_wraps_left(car_rtl):
    car_rtl.x = -car_rtl.w - 1
    car_rtl.update()
    assert car_rtl.x == SCREEN_WIDTH


# Vehicle rect

def test_vehicle_get_rect(car):
    car.x = 10
    r = car.get_rect()
    expected_y = car.row * GRID_SIZE + 60 + (GRID_SIZE - car.h) // 2
    assert r.x == 10
    assert r.y == expected_y
    assert r.width == car.w
    assert r.height == car.h


# PowerUp

def test_powerup_collect_match():
    pu = PowerUp()
    pu.active = True
    pu.x = 3
    pu.y = 4
    assert pu.check_collect(3, 4) is True


def test_powerup_collect_miss():
    pu = PowerUp()
    pu.active = True
    pu.x = 3
    pu.y = 4
    assert pu.check_collect(3, 5) is False


def test_powerup_collect_inactive():
    pu = PowerUp()
    pu.active = False
    pu.x = 3
    pu.y = 4
    assert pu.check_collect(3, 4) is False


def test_powerup_deactivates_after_300_ticks():
    pu = PowerUp()
    pu.active = True
    pu.timer = 300
    for _ in range(300):
        pu.update()
    assert pu.active is False


def test_powerup_respawns_after_600_ticks():
    pu = PowerUp()
    pu.active = False
    pu.spawn_timer = 600
    for _ in range(600):
        pu.update()
    assert pu.active is True


def test_powerup_reset():
    pu = PowerUp()
    pu.active = True
    pu.reset()
    assert pu.active is False
    assert pu.spawn_timer == 600


# PowerUp spawn range

def test_powerup_never_spawns_on_start_pond():
    """PowerUp must not spawn on row 9 (the start pond)."""
    import random
    random.seed(42)
    for _ in range(200):
        pu = PowerUp()
        assert pu.y != 9, f"PowerUp spawned on start pond row 9 (y={pu.y})"


# make_vehicles

def test_make_vehicles_covers_rows_1_to_8():
    vehicles = make_vehicles(1)
    rows = {v.row for v in vehicles}
    assert rows == set(range(1, 9))


def test_make_vehicles_speed_scales_with_level():
    v1 = make_vehicles(1)
    v5 = make_vehicles(5)
    avg_speed_1 = sum(abs(v.speed) for v in v1) / len(v1)
    avg_speed_5 = sum(abs(v.speed) for v in v5) / len(v5)
    assert avg_speed_5 > avg_speed_1


def test_make_vehicles_direction_alternates_by_row():
    vehicles = make_vehicles(1)
    for v in vehicles:
        if v.row % 2 == 0:
            assert v.speed > 0, f"Row {v.row} should go right"
        else:
            assert v.speed < 0, f"Row {v.row} should go left"
