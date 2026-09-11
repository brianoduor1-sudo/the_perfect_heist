import pytest

from ai.goal_parser import GoalParser, parse_and_validate_ai_response
from game.goal import StealItemGoal, ReachExitGoal, AvoidDetectionGoal, CompositeGoal


def test_parse_returns_steal_item_goal():
    goal = GoalParser().parse("steal")
    assert isinstance(goal, StealItemGoal)
    assert goal.item_name == "artifact"


def test_parse_returns_reach_exit_goal():
    goal = GoalParser().parse("escape")
    assert isinstance(goal, ReachExitGoal)


def test_parse_returns_avoid_detection_goal():
    goal = GoalParser().parse("stealth")
    assert isinstance(goal, AvoidDetectionGoal)


def test_parse_returns_composite_goal_for_steal_and_escape():
    goal = GoalParser().parse("steal_and_escape")
    assert isinstance(goal, CompositeGoal)
    assert len(goal.goals) == 2


def test_parse_returns_none_for_unsupported_choice():
    goal = GoalParser().parse("do a backflip")
    assert goal is None


def test_parse_and_validate_ai_response_accepts_valid_move():
    action = GoalParser.parse_and_validate_ai_response('{"action": "move", "direction": "north"}')
    assert action is not None
    assert action.move == "north"
    assert action.model_dump() == {"action": "move", "direction": "north"}


def test_parse_and_validate_ai_response_rejects_malformed_json():
    action = GoalParser.parse_and_validate_ai_response("this is not json")
    assert action is None


def test_parse_and_validate_ai_response_rejects_unknown_action():
    action = GoalParser.parse_and_validate_ai_response('{"action": "teleport"}')
    assert action is None


def test_parse_and_validate_ai_response_rejects_invalid_direction():
    action = GoalParser.parse_and_validate_ai_response('{"action": "move", "direction": "up"}')
    assert action is None


def test_parse_and_validate_ai_response_accepts_non_move_action_without_direction():
    action = GoalParser.parse_and_validate_ai_response('{"action": "wait"}')
    assert action is not None
    assert action.move == "wait"


def test_parse_and_validate_ai_response_rejects_non_dict_json():
    action = GoalParser.parse_and_validate_ai_response('["move", "north"]')
    assert action is None


def test_module_level_function_matches_classmethod_behavior():
    raw = '{"action": "pick_up"}'
    from_function = parse_and_validate_ai_response(raw)
    from_classmethod = GoalParser.parse_and_validate_ai_response(raw)
    assert from_function.model_dump() == from_classmethod.model_dump()