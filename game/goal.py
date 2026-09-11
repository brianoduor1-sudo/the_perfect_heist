from abc import ABC, abstractmethod


class Goal(ABC):
    @abstractmethod
    def is_complete(self, game_state) -> bool:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass


class StealItemGoal(Goal):
    def __init__(self, item_name):
        self.item_name = item_name

    def is_complete(self, game_state):
        return game_state.player.has_item(self.item_name)

    def describe(self):
        return f"Steal the {self.item_name}"


class ReachExitGoal(Goal):
    def is_complete(self, game_state):
        exit_tile = game_state.building.find_label("exit")
        return game_state.player.position == exit_tile

    def describe(self):
        return "Reach the exit"


class AvoidDetectionGoal(Goal):
    def is_complete(self, game_state):
        return not game_state.player.caught

    def describe(self):
        return "Escape without being detected"


class CompositeGoal(Goal):
    """
    Bundles multiple goals together so GameState only has to
    check one is_complete() call instead of looping over a list itself.
    This is how "steal the artifact and escape" ends up represented.
    """

    def __init__(self, goals):
        self.goals = goals

    def is_complete(self, game_state):
        return all(goal.is_complete(game_state) for goal in self.goals)

    def describe(self):
        return " and ".join(goal.describe() for goal in self.goals)