"""Tests for TurtlePlayer logic (no display required)."""
import pytest
from src.turtle_player import TurtlePlayer, CELEBRATE_DURATION


@pytest.fixture
def player():
    return TurtlePlayer()


# Movement — boundaries and scoring

def test_move_up_decrements_y_and_scores(player):
    player.y = 5
    player.score = 0
    player.move("up")
    assert player.y == 4
    assert player.score == 10


def test_move_up_clamps_at_zero(player):
    player.y = 0
    player.move("up")
    assert player.y == 0


def test_move_down_increments_y(player):
    player.y = 5
    player.move("down")
    assert player.y == 6


def test_move_down_clamps_at_ten(player):
    player.y = 10
    player.move("down")
    assert player.y == 10


def test_move_left_decrements_x(player):
    player.x = 5
    player.move("left")
    assert player.x == 4


def test_move_left_clamps_at_zero(player):
    player.x = 0
    player.move("left")
    assert player.x == 0


def test_move_right_increments_x(player):
    player.x = 5
    player.move("right")
    assert player.x == 6


def test_move_right_clamps_at_nine(player):
    player.x = 9
    player.move("right")
    assert player.x == 9


def test_move_down_does_not_score(player):
    player.score = 0
    player.move("down")
    assert player.score == 0


# Hit and invincibility

def test_take_hit_decrements_lives(player):
    initial = player.lives
    player.take_hit()
    assert player.lives == initial - 1


def test_take_hit_starts_flashing(player):
    player.take_hit()
    assert player.flashing is True
    assert player.flash_timer == 90


def test_activate_invincibility(player):
    player.activate_invincibility()
    assert player.invincible is True
    assert player.inv_timer == 300


def test_invincibility_expires_after_timer(player):
    player.activate_invincibility()
    for _ in range(300):
        player.update()
    assert player.invincible is False


def test_flash_expires_and_resets_position(player):
    player.x = 3
    player.y = 4
    player.take_hit()
    for _ in range(90):
        player.update()
    assert player.flashing is False
    assert player.x == 5
    assert player.y == 10


# Celebration

def test_celebrate_sets_state(player):
    player.celebrate()
    assert player.celebrating is True
    assert player.celebrate_timer == CELEBRATE_DURATION


def test_celebrate_freezes_inv_timer(player):
    player.activate_invincibility()
    inv_before = player.inv_timer
    player.celebrate()
    player.update()   # timer should NOT decrement while celebrating
    assert player.inv_timer == inv_before


def test_celebrate_timer_counts_down(player):
    player.celebrate()
    player.update()
    assert player.celebrate_timer == CELEBRATE_DURATION - 1


# Position reset

def test_reset_position(player):
    player.x = 0
    player.y = 0
    player.reset_position()
    assert player.x == 5
    assert player.y == 10


# Collision rect

def test_get_rect_pixel_bounds(player):
    player.x = 0
    player.y = 0
    r = player.get_rect()
    # x=0*60+8=8, y=0*60+60+8=68, w=44, h=44
    assert r.x == 8
    assert r.y == 68
    assert r.width == 44
    assert r.height == 44


def test_get_rect_mid_grid(player):
    player.x = 3
    player.y = 5
    r = player.get_rect()
    assert r.x == 3 * 60 + 8
    assert r.y == 5 * 60 + 60 + 8
