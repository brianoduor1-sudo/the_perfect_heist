
import pytest
from game.engine import GameEngine
from game.player import Player
from game.guard import Guard


class FakeBuilding:
    """Minimal stand-in for Epic 3's Building — just needs is_wall()."""
    def __init__(self, walls):
        self._walls = set(walls)

    def is_wall(self, position):
        return position in self._walls


class FakeGoal:
    """Minimal stand-in for Epic 1's Goal — just needs is_reached()."""
    def __init__(self, target_position):
        self._target = target_position

    def is_reached(self, player):
        return player.position == self._target


@pytest.fixture
def player():
    return Player(start_position=(0, 0))



def test_move_updates_position_and_turn_count(player):
    engine = GameEngine(player, guards=[])
    status = engine.process_turn("east")
    assert player.position == (1, 0)
    assert status == "in_progress"
    assert engine.turn_count == 1


def test_invalid_direction_raises(player):
    engine = GameEngine(player, guards=[])
    with pytest.raises(ValueError):
        engine.process_turn("up")



def test_wall_blocks_move_and_does_not_spend_a_turn(player):
    building = FakeBuilding(walls=[(1, 0)])
    engine = GameEngine(player, guards=[], building=building)
    status = engine.process_turn("east")
    assert player.position == (0, 0)   # didn't move
    assert engine.turn_count == 0      # blocked move isn't a real turn
    assert status == "in_progress"


def test_guard_detection_sets_status_lost(player):
    guard = Guard(patrol_path=[(0, 0)], vision_range=5)  # stationary, sees everything
    engine = GameEngine(player, guards=[guard])
    status = engine.process_turn("east")
    assert status == "lost"
    assert engine.is_game_over() is True


def test_no_further_moves_once_lost(player):
    guard = Guard(patrol_path=[(0, 0)], vision_range=5)
    engine = GameEngine(player, guards=[guard])
    engine.process_turn("east")   # triggers loss
    pos_after_loss = player.position

    status = engine.process_turn("west") 
    assert status == "lost"
    assert player.position == pos_after_loss


def test_reaching_goal_sets_status_won():
    player = Player(start_position=(4, 0))
    goal = FakeGoal(target_position=(5, 0))
    engine = GameEngine(player, guards=[], goal=goal)
    status = engine.process_turn("east")
    assert status == "won"
    assert engine.is_game_over() is True


def test_not_reaching_goal_keeps_playing():
    player = Player(start_position=(0, 0))
    goal = FakeGoal(target_position=(5, 0))
    engine = GameEngine(player, guards=[], goal=goal)
    status = engine.process_turn("east")
    assert status == "in_progress"
    assert engine.is_game_over() is False


def test_wall_blocks_guard_line_of_sight_via_engine():
    player = Player(start_position=(4, 4))
    guard = Guard(patrol_path=[(0, 0)], vision_range=10)
    building = FakeBuilding(walls=[(1, 1)])  # sits between guard and player
    engine = GameEngine(player, guards=[guard], building=building)

    status = engine.process_turn("east")  # player moves but stays hidden
    assert status == "in_progress"