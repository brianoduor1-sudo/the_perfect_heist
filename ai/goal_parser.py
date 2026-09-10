import json

from game.goal import StealItemGoal, ReachExitGoal, AvoidDetectionGoal, CompositeGoal


class ParsedAction:
    """
    What comes back once a raw AI response has been checked and is safe
    to hand to MoveValidator. Never build this directly from AI text
    without going through parse_and_validate_ai_response first.
    """

    VALID_DIRECTIONS = {"north", "south", "east", "west"}
    VALID_ACTIONS = {"move", "pick_up", "wait"}

    def __init__(self, action, direction=None):
        self.action = action
        self.direction = direction

    @property
    def move(self):
        # move actions expose their direction here, everything else
        # just exposes the action name itself
        if self.action == "move":
            return self.direction
        return self.action

    def model_dump(self):
        return {"action": self.action, "direction": self.direction}

    def __repr__(self):
        return f"ParsedAction(action={self.action!r}, direction={self.direction!r})"


class GoalParser:
    """
    Turns a fixed set of supported goal choices into Goal objects.
    Free-text natural language parsing was cut from scope, so this
    works off a small set of known keys rather than a sentence.
    """

    SUPPORTED_CHOICES = {
        "steal": lambda: StealItemGoal("artifact"),
        "escape": lambda: ReachExitGoal(),
        "stealth": lambda: AvoidDetectionGoal(),
        "steal_and_escape": lambda: CompositeGoal(
            [StealItemGoal("artifact"), ReachExitGoal()]
        ),
        "full_stealth_run": lambda: CompositeGoal(
            [StealItemGoal("artifact"), ReachExitGoal(), AvoidDetectionGoal()]
        ),
    }

    def parse(self, choice: str):
        builder = self.SUPPORTED_CHOICES.get(choice)
        if builder is None:
            return None
        return builder()

    @staticmethod
    def parse_and_validate_ai_response(raw_response: str):
        try:
            data = json.loads(raw_response)
        except (json.JSONDecodeError, TypeError):
            return None

        if not isinstance(data, dict):
            return None

        action = data.get("action")
        if action not in ParsedAction.VALID_ACTIONS:
            return None

        direction = data.get("direction")
        if action == "move" and direction not in ParsedAction.VALID_DIRECTIONS:
            return None

        return ParsedAction(action=action, direction=direction)


# module-level alias so `from goal_parser import parse_and_validate_ai_response`
# works too, in case strategist.py imports it directly instead of via the class
def parse_and_validate_ai_response(raw_response: str):
    return GoalParser.parse_and_validate_ai_response(raw_response)