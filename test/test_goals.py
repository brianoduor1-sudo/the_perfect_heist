from game.player import Player
from game.goal import StealItemGoal, ReachExitGoal, AvoidDetectionGoal, CompositeGoal


class FakeBuilding:
    def find_label(self, label):
        return (9, 9) if label == "exit" else None


class FakeGameState:
    def __init__(self, player, building=None):
        self.player = player
        self.building = building or FakeBuilding()


def test_steal_item_goal_completes_when_item_in_inventory():
    player = Player(position=(0, 0))
    player.pick_up("artifact")
    state = FakeGameState(player)
    assert StealItemGoal("artifact").is_complete(state) is True

def test_steal_item_goal_not_complete_without_item():
    player = Player(position=(0, 0))
    state = FakeGameState(player)
    assert StealItemGoal("artifact").is_complete(state) is False

def test_reach_exit_goal_completes_at_exit_position():
    player = Player(position=(9, 9))
    state = FakeGameState(player)
    assert ReachExitGoal().is_complete(state) is True

def test_avoid_detection_goal_fails_once_caught():
    player = Player(position=(0, 0))
    player.mark_caught()
    state = FakeGameState(player)
    assert AvoidDetectionGoal().is_complete(state) is False

def test_composite_goal_requires_all_subgoals_complete():
    player = Player(position=(9, 9))
    player.pick_up("artifact")
    state = FakeGameState(player)
    combined = CompositeGoal([StealItemGoal("artifact"), ReachExitGoal()])
    assert combined.is_complete(state) is True
    