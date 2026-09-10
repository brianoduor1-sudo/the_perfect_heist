from typing import Tuple, Dict, Optional

from .building import Building

Position = Tuple[int, int]  # (x, y)

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "n": (0, -1),
    "s": (0, 1),
    "e": (1, 0),
    "w": (-1, 0),
}


class MoveValidator:
    """Validates moves using only grid adjacency and tile walkability."""

    def __init__(self, building: Building):
        self.building = building

    def is_adjacent(self, current: Position, target: Position) -> bool:
        """True if target is exactly one orthogonal step from current."""
        if not self.building.in_bounds(target):
            return False
        dx = abs(current[0] - target[0])
        dy = abs(current[1] - target[1])
        return (dx + dy) == 1

    def get_direction(self, current: Position, target: Position) -> Optional[str]:
        """Returns 'n'/'s'/'e'/'w' for the step from current to target."""
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        for direction, (step_x, step_y) in DIRECTIONS.items():
            if (step_x, step_y) == (dx, dy):
                return direction
        return None

    def is_valid_move(self, current: Position, target: Position) -> bool:
        """
        A move is valid only if:
          1. target is adjacent to current (and in bounds), AND
          2. the target tile is walkable (not a WALL tile).
        """
        if not self.is_adjacent(current, target):
            return False
        return self.building.is_walkable(target)


# ---------------------------------------------------------------------------
# Bare CLI: prints the map (using each tile's own char) and takes manual input.
# ---------------------------------------------------------------------------

def print_map(building: Building, player: Position) -> None:
    """
    Renders the grid using each Tile's to_char(), with '@' for the player
    overlaid on top of whatever tile they're standing on.
    """
    for y in range(building.height):
        row_line = ""
        for x in range(building.width):
            position = (x, y)
            if position == player:
                row_line += "@"
            else:
                row_line += building.get_tile(position).to_char()
        print(row_line)


def main() -> None:
    building = Building.from_file("data/map.txt")
    validator = MoveValidator(building)
    player: Position = (0, 0)  # TODO: read a real start position from the map

    print("MoveValidator CLI -- commands: n/s/e/w to move, q to quit")
    print_map(building, player)

    while True:
        move = input("\nEnter move (n/s/e/w/q): ").strip().lower()

        if move == "q":
            print("Goodbye!")
            break

        if move not in DIRECTIONS:
            print("Unrecognized command. Use n, s, e, w, or q.")
            continue

        step_x, step_y = DIRECTIONS[move]
        target: Position = (player[0] + step_x, player[1] + step_y)

        if validator.is_valid_move(player, target):
            player = target
        else:
            print("Invalid move: wall or out of bounds.")

        print_map(building, player)


if __name__ == "__main__":
    main()