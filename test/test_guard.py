

import pytest
from game.guard import Guard, Direction


@pytest.fixture
def stationary_guard():
    return Guard(patrol_path=[(5, 5)], vision_range=3)


@pytest.fixture
def patrolling_guard():
    return Guard(patrol_path=[(0, 0), (0, 3), (3, 3)], vision_range=2)


class FakeBuilding:
    """Minimal stand-in for Epic 3's Building — just needs is_wall()."""
    def __init__(self, wall_positions):
        self._walls = set(wall_positions)

    def is_wall(self, position):
        return position in self._walls


# -- patrol behaviour --
def test_guard_starts_at_first_patrol_point():
    assert Guard(patrol_path=[(1, 1), (4, 1)]).position == (1, 1)


def test_patrol_step_moves(patrolling_guard):
    start = patrolling_guard.position
    patrolling_guard.patrol_step()
    assert patrolling_guard.position != start


def test_patrol_reaches_every_waypoint_and_loops():
    guard = Guard(patrol_path=[(0, 0), (2, 0)])
    visited = {guard.position}
    for _ in range(10):
        visited.add(guard.patrol_step())
    assert (0, 0) in visited and (2, 0) in visited


def test_patrol_updates_facing():
    guard = Guard(patrol_path=[(0, 0), (5, 0)])
    guard.patrol_step()
    assert guard.facing == Direction.EAST


def test_empty_patrol_path_raises():
    with pytest.raises(ValueError):
        Guard(patrol_path=[])


# -- detection: radius + edge cases --
@pytest.mark.parametrize("player_position, expected", [
    ((5, 5), True),   
    ((6, 6), True),    
    ((8, 5), True),   
    ((9, 5), False),   
    ((20, 20), False), 
])
def test_detects_player_radius_cases(stationary_guard, player_position, expected):
    assert stationary_guard.detects_player(player_position) is expected


def test_detection_symmetric_in_all_directions(stationary_guard):
    for dx, dy in [(3, 0), (-3, 0), (0, 3), (0, -3)]:
        assert stationary_guard.detects_player((5 + dx, 5 + dy)) is True


# -- detection: line-of-sight --
def test_wall_blocks_detection_within_radius():
    guard = Guard(patrol_path=[(0, 0)], vision_range=5)
    wall = FakeBuilding([(2, 2)])
    assert guard.detects_player((4, 4), building=wall) is False


def test_clear_line_still_detects():
    guard = Guard(patrol_path=[(0, 0)], vision_range=5)
    wall = FakeBuilding([(2, 2)])
    assert guard.detects_player((4, 0), building=wall) is True


def test_detection_without_building_uses_radius_only():
    guard = Guard(patrol_path=[(0, 0)], vision_range=2)
    assert guard.detects_player((1, 1)) is True
    assert guard.detects_player((10, 10)) is False


# -- persistence round-trip --
def test_to_dict_matches_save_schema(patrolling_guard):
    data = patrolling_guard.to_dict()
    assert "position" in data and "patrol_index" in data
    assert isinstance(data["position"], list)  # JSON has no tuples


def test_from_dict_round_trip(patrolling_guard):
    patrolling_guard.patrol_step()
    patrolling_guard.patrol_step()
    saved = patrolling_guard.to_dict()
    restored = Guard.from_dict(saved, patrol_path=patrolling_guard.patrol_path)
    assert restored.position == patrolling_guard.position
    assert restored.facing == patrolling_guard.facing
