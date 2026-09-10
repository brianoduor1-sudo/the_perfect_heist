

from __future__ import annotations
from typing import List, Optional, Protocol
from game.guard import Guard, SupportsWallCheck
from game.player import Player, MOVES


class SupportsGoalCheck(Protocol):
    """Shape a Goal object needs — no import of goal.py required."""
    def is_reached(self, player: Player) -> bool: ...


class GameEngine:
    def __init__(self, player: Player, guards: List[Guard],
                 building: Optional[SupportsWallCheck] = None,
                 goal: Optional[SupportsGoalCheck] = None):
        self.player = player
        self.guards = guards
        self.building = building   
        self.goal = goal          
        self.status = "in_progress"  
        self.turn_count = 0

    def process_turn(self, direction: str) -> str:
        """One player move, then guards react, then check win/loss."""
        if self.status != "in_progress":
            return self.status 

        if not self._try_move_player(direction):
            return self.status 

        self.turn_count += 1
        self._step_guards()
        if self.status == "lost":
            return self.status

        self._check_goal()
        return self.status

    def _try_move_player(self, direction: str) -> bool:
        direction = direction.lower()
        if direction not in MOVES:
            raise ValueError(f"Invalid direction: {direction}")
        dx, dy = MOVES[direction]
        x, y = self.player.position
        target = (x + dx, y + dy)
        if self.building is not None and self.building.is_wall(target):
            return False  
        self.player.set_position(target)
        return True

    def _step_guards(self) -> None:
        for guard in self.guards:
            guard.patrol_step()
            if guard.detects_player(self.player.position, self.building):
                self.status = "lost"
                return

    def _check_goal(self) -> None:
        if self.goal is not None and self.goal.is_reached(self.player):
            self.status = "won"

    def is_game_over(self) -> bool:
        return self.status != "in_progress"