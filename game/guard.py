"""
game/guard.py — Epic 2: Guard patrol + detection (owner: Brian)

Concepts used: Enum, encapsulation (_underscore attrs), @property,
@staticmethod, @classmethod, Protocol (duck typing), tuples for
positions.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Protocol, Tuple


class Direction(Enum):
    """Fixed set of facing values (safer than raw strings)."""
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)


class SupportsWallCheck(Protocol):
    """Shape Building must have for line-of-sight — no import needed."""
    def is_wall(self, position: Tuple[int, int]) -> bool: ...


class Guard:
    def __init__(self, patrol_path: List[Tuple[int, int]],
                 vision_range: int = 3, facing: Direction = Direction.SOUTH):
        if not patrol_path:
            raise ValueError("Guard requires at least one patrol point.")
        self._patrol_path = list(patrol_path)   # copy, don't alias caller's list
        self._patrol_index = 0
        self._position = self._patrol_path[0]
        self._vision_range = vision_range
        self._facing = facing

    # -- read-only access --
    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @property
    def vision_range(self) -> int:
        return self._vision_range

    @property
    def facing(self) -> Direction:
        return self._facing

    @property
    def patrol_path(self) -> List[Tuple[int, int]]:
        return list(self._patrol_path)  # copy so callers can't mutate the real route

    # -- Story 1: patrol --
    def patrol_step(self) -> Tuple[int, int]:
        """Move 1 tile toward the next waypoint; loop back at the end."""
        target = self._patrol_path[self._patrol_index]
        if self._position == target:
            self._patrol_index = (self._patrol_index + 1) % len(self._patrol_path)
            target = self._patrol_path[self._patrol_index]
        self._position = self._move_one_step_toward(self._position, target)
        self._update_facing(target)
        return self._position

    @staticmethod
    def _move_one_step_toward(current, target) -> Tuple[int, int]:
        cx, cy = current
        tx, ty = target
        dx = (tx > cx) - (tx < cx)
        dy = (ty > cy) - (ty < cy)
        return (cx + dx, cy + dy)

    def _update_facing(self, target: Tuple[int, int]) -> None:
        dx, dy = target[0] - self._position[0], target[1] - self._position[1]
        if abs(dx) >= abs(dy):
            self._facing = Direction.EAST if dx >= 0 else Direction.WEST
        else:
            self._facing = Direction.SOUTH if dy >= 0 else Direction.NORTH

    # -- Story 2: detection --
    def detects_player(self, player_position: Tuple[int, int],
                        building: Optional[SupportsWallCheck] = None) -> bool:
        """Radius-based detection; optional wall check if building is given."""
        distance = self._chebyshev_distance(self._position, player_position)
        if distance > self._vision_range:
            return False
        if building is not None and self._line_of_sight_blocked(player_position, building):
            return False
        return True

    @staticmethod
    def _chebyshev_distance(a, b) -> int:
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def _line_of_sight_blocked(self, player_position, building) -> bool:
        return any(building.is_wall(t) for t in self._tiles_between(self._position, player_position))

    @staticmethod
    def _tiles_between(start, end) -> List[Tuple[int, int]]:
        """Tiles strictly between start and end (straight line)."""
        x0, y0 = start
        x1, y1 = end
        steps = max(abs(x1 - x0), abs(y1 - y0))
        if steps == 0:
            return []
        return [(round(x0 + (x1 - x0) * i / steps), round(y0 + (y1 - y0) * i / steps))
                for i in range(1, steps)]

    # -- Story 3 note: GameState (Epic 5) calls detects_player() each turn
    # and sets status="lost" — Guard itself never touches GameState. --

    # -- persistence, matches Epic 3's save schema --
    def to_dict(self) -> dict:
        return {"position": list(self._position), "patrol_index": self._patrol_index,
                "vision_range": self._vision_range, "facing": self._facing.name}

    @classmethod
    def from_dict(cls, data: dict, patrol_path: List[Tuple[int, int]]) -> "Guard":
        guard = cls(patrol_path, vision_range=data.get("vision_range", 3),
                     facing=Direction[data.get("facing", "SOUTH")])
        guard._position = tuple(data["position"])
        guard._patrol_index = data.get("patrol_index", 0)
        return guard

    def __repr__(self) -> str:
        return f"Guard(position={self._position}, facing={self._facing.name})"