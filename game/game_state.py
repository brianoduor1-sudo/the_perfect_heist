"""
GameState (Epic 5 - Peter).

Orchestrates a single turn of the game:
  1. Try to move the player (via MoveValidator).
  2. Let each guard take its turn.
  3. Check whether any guard has caught the player.
  4. Check whether the goal has been completed.
  5. Advance the turn counter and update game-over status.

GameState relies on exactly this interface from the other classes --
worth writing this up in interfaces.md for the team:
  - building : in_bounds(cell), get_tile(cell)                [Building]
  - player   : .position, .move_to(cell)                      [Player]
  - guards   : list of objects with .position, .take_turn(game_state) [Guard]
  - goal     : .is_complete(game_state) -> bool                [Goal / subclasses]

GameState doesn't implement guard AI or goal rules itself -- it only
calls out to them. That's what keeps it stable while Guard/Goal/Player
are built independently by teammates.
"""

from game.move_validator import MoveValidator

DIRECTIONS = {"n": (-1, 0), "s": (1, 0), "e": (0, 1), "w": (0, -1)}


class GameState:
    def __init__(self, building, player, guards, goal):
        self.building = building
        self.player = player
        self.guards = guards
        self.goal = goal
        self.move_validator = MoveValidator(building)

        self.turn_count = 0
        self.game_over = False
        self.outcome = None  # None, "won", or "caught"

    def attempt_player_move(self, direction: str) -> bool:
        """
        Tries to move the player one step in `direction` ('n'/'s'/'e'/'w').
        Returns True if the move happened, False if it was invalid or the
        game has already ended.
        """
        if self.game_over or direction not in DIRECTIONS:
            return False

        d_row, d_col = DIRECTIONS[direction]
        current = self.player.position
        target = (current[0] + d_row, current[1] + d_col)

        if not self.move_validator.is_valid_move(current, target):
            return False

        self.player.move_to(target)
        self._advance_turn()
        return True

    def _advance_turn(self) -> None:
        """Everything that happens after the player's move lands."""
        for guard in self.guards:
            guard.take_turn(self)

        if self._is_player_caught():
            self.game_over = True
            self.outcome = "caught"
        elif self.goal.is_complete(self):
            self.game_over = True
            self.outcome = "won"

        self.turn_count += 1

    def _is_player_caught(self) -> bool:
        return any(guard.position == self.player.position for guard in self.guards)

    def is_game_over(self) -> bool:
        return self.game_over

    def get_status(self) -> str:
        """Short human-readable status, e.g. for the CLI to print."""
        if self.outcome == "won":
            return f"You reached the goal in {self.turn_count} turns!"
        if self.outcome == "caught":
            return f"Caught by a guard after {self.turn_count} turns."
        return f"Turn {self.turn_count} -- still in progress."