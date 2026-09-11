import unittest

from game.building import Building
from game.game_state import GameState


class FakePlayer:
    def __init__(self, position):
        self.position = position

    def move_to(self, position):
        self.position = position


class FakeGuard:
    """A guard whose behavior each turn is scripted by the test."""

    def __init__(self, position, moves_to_on_turn=None):
        self.position = position
        # Optional queue of positions to move to, one per take_turn() call.
        self._moves = list(moves_to_on_turn) if moves_to_on_turn else []
        self.turns_taken = 0

    def take_turn(self, state):
        self.turns_taken += 1
        if self._moves:
            self.position = self._moves.pop(0)


class FakeGoal:
    """Reports complete once told to, regardless of player position."""

    def __init__(self, complete_when=None):
        # complete_when: a callable(state) -> bool, or None (never complete)
        self._complete_when = complete_when or (lambda state: False)

    def is_complete(self, state):
        return self._complete_when(state)


def make_open_building(width=5, height=5):
    row = "#" + "." * (width - 2) + "#"
    lines = ["#" * width] + [row] * (height - 2) + ["#" * width]
    return Building.from_lines(lines)


class TestAttemptPlayerMove(unittest.TestCase):
    def setUp(self):
        self.building = make_open_building()
        self.player = FakePlayer(position=(1, 1))
        self.guard = FakeGuard(position=(3, 3))
        self.goal = FakeGoal()
        self.state = GameState(self.building, self.player, [self.guard], self.goal)

    def test_valid_move_returns_true_and_moves_player(self):
        moved = self.state.attempt_player_move("e")
        self.assertTrue(moved)
        self.assertEqual(self.player.position, (2, 1))

    def test_valid_move_advances_turn_count(self):
        self.state.attempt_player_move("e")
        self.assertEqual(self.state.turn_count, 1)

    def test_valid_move_gives_every_guard_a_turn(self):
        self.state.attempt_player_move("e")
        self.assertEqual(self.guard.turns_taken, 1)

    def test_invalid_direction_string_returns_false(self):
        moved = self.state.attempt_player_move("north")  # not 'n'
        self.assertFalse(moved)
        self.assertEqual(self.player.position, (1, 1))

    def test_move_into_wall_returns_false_and_does_not_move(self):
        # Player at (1,1); moving 'n' would step onto the border wall.
        moved = self.state.attempt_player_move("n")
        self.assertFalse(moved)
        self.assertEqual(self.player.position, (1, 1))

    def test_invalid_move_does_not_advance_turn_or_run_guards(self):
        self.state.attempt_player_move("n")  # blocked by wall
        self.assertEqual(self.state.turn_count, 0)
        self.assertEqual(self.guard.turns_taken, 0)


class TestGameOverByCapture(unittest.TestCase):
    def setUp(self):
        self.building = make_open_building()
        self.player = FakePlayer(position=(1, 1))
        # Guard steps onto the player's new position right after the move.
        self.guard = FakeGuard(position=(3, 1), moves_to_on_turn=[(2, 1)])
        self.goal = FakeGoal()
        self.state = GameState(self.building, self.player, [self.guard], self.goal)

    def test_guard_landing_on_player_ends_game_as_caught(self):
        self.state.attempt_player_move("e")  # player moves to (2, 1)
        self.assertTrue(self.state.is_game_over())
        self.assertEqual(self.state.outcome, "caught")

    def test_further_moves_are_blocked_after_capture(self):
        self.state.attempt_player_move("e")  # triggers capture
        moved_again = self.state.attempt_player_move("s")
        self.assertFalse(moved_again)


class TestGameOverByWinning(unittest.TestCase):
    def setUp(self):
        self.building = make_open_building()
        self.player = FakePlayer(position=(1, 1))
        self.guard = FakeGuard(position=(3, 3))  # never catches anyone here
        # Goal completes as soon as the player has moved at least once.
        self.goal = FakeGoal(complete_when=lambda state: state.player.position == (2, 1))
        self.state = GameState(self.building, self.player, [self.guard], self.goal)

    def test_reaching_the_goal_ends_game_as_won(self):
        self.state.attempt_player_move("e")
        self.assertTrue(self.state.is_game_over())
        self.assertEqual(self.state.outcome, "won")

    def test_further_moves_are_blocked_after_winning(self):
        self.state.attempt_player_move("e")  # triggers win
        moved_again = self.state.attempt_player_move("s")
        self.assertFalse(moved_again)


class TestGetStatus(unittest.TestCase):
    def setUp(self):
        self.building = make_open_building()
        self.player = FakePlayer(position=(1, 1))
        self.guard = FakeGuard(position=(3, 3))
        self.goal = FakeGoal()
        self.state = GameState(self.building, self.player, [self.guard], self.goal)

    def test_status_in_progress_shows_turn_count(self):
        self.state.attempt_player_move("e")
        status = self.state.get_status()
        self.assertIn("1", status)
        self.assertIn("progress", status.lower())

    def test_status_after_win_mentions_goal_and_turns(self):
        self.state.outcome = "won"
        self.state.turn_count = 4
        status = self.state.get_status()
        self.assertIn("4", status)
        self.assertIn("goal", status.lower())

    def test_status_after_caught_mentions_guard_and_turns(self):
        self.state.outcome = "caught"
        self.state.turn_count = 2
        status = self.state.get_status()
        self.assertIn("2", status)
        self.assertIn("caught", status.lower())


if __name__ == "__main__":
    unittest.main()