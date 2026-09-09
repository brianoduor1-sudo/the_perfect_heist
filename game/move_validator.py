"""
MoveValidator skeleton (adjacency + walls only) + bare CLI.

Part of a larger stealth game whose concepts map to classes:
Player, Guard, Building, Tile, GameState, Goal, MoveValidator.

This file focuses ONLY on MoveValidator, plus the minimal Tile and Building
classes it depends on. Player/Guard/GameState/Goal are intentionally left
out for now -- other parts of the project will define those.

Design notes:
- Tile: knows which of its 4 sides ('n','s','e','w') have a wall.
- Building: a width x height grid of Tiles. Cells are addressed as
  (row, col). add_wall_between() marks a wall on BOTH tiles it touches,
  so wall data stays consistent regardless of which tile you check from.
- MoveValidator: takes a Building and checks two things only:
    1. Adjacency -> is `target` exactly one orthogonal step from `current`,
       and inside the grid?
    2. Walls     -> is there a wall blocking that specific edge?
  Its public method, is_valid_move(current, target), is meant to stay
  stable even as Tile/Building grow more features later (e.g. locked
  doors, item pickups) -- other classes like Player should be able to
  call it without caring about the internals.
"""

from typing import Tuple, Dict

Cell = Tuple[int, int]  # (row, col)

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "n": (-1, 0),
    "s": (1, 0),
    "e": (0, 1),
    "w": (0, -1),
}

OPPOSITE = {"n": "s", "s": "n", "e": "w", "w": "e"}


class Tile:
    """A single grid cell. Knows only which of its sides are walled."""

    def __init__(self):
        self.walls = set()  # subset of {'n', 's', 'e', 'w'}

    def has_wall(self, direction: str) -> bool:
        return direction in self.walls

    def add_wall(self, direction: str) -> None:
        self.walls.add(direction)


class Building:
    """A width x height grid of Tiles."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = [[Tile() for _ in range(width)] for _ in range(height)]

    def in_bounds(self, cell: Cell) -> bool:
        row, col = cell
        return 0 <= row < self.height and 0 <= col < self.width

    def get_tile(self, cell: Cell) -> Tile:
        row, col = cell
        return self.grid[row][col]

    def add_wall_between(self, cell_a: Cell, cell_b: Cell) -> None:
        """
        Marks a wall on the shared edge between two adjacent cells.
        Updates BOTH tiles so the wall is consistent from either side.
        """
        row_diff = cell_b[0] - cell_a[0]
        col_diff = cell_b[1] - cell_a[1]

        direction_from_a = None
        for direction, (d_row, d_col) in DIRECTIONS.items():
            if (d_row, d_col) == (row_diff, col_diff):
                direction_from_a = direction
                break

        if direction_from_a is None:
            raise ValueError(f"{cell_a} and {cell_b} are not orthogonally adjacent")

        self.get_tile(cell_a).add_wall(direction_from_a)
        self.get_tile(cell_b).add_wall(OPPOSITE[direction_from_a])


class MoveValidator:
    """Validates moves based only on grid adjacency and walls."""

    def __init__(self, building: Building):
        self.building = building

    def is_adjacent(self, current: Cell, target: Cell) -> bool:
        """True if target is exactly one orthogonal step from current."""
        if not self.building.in_bounds(target):
            return False
        row_diff = abs(current[0] - target[0])
        col_diff = abs(current[1] - target[1])
        return (row_diff + col_diff) == 1

    def get_direction(self, current: Cell, target: Cell) -> str:
        """Returns 'n'/'s'/'e'/'w' for the step from current to target."""
        row_diff = target[0] - current[0]
        col_diff = target[1] - current[1]
        for direction, (d_row, d_col) in DIRECTIONS.items():
            if (d_row, d_col) == (row_diff, col_diff):
                return direction
        return None

    def has_wall_between(self, current: Cell, target: Cell) -> bool:
        """True if a wall blocks the move from current to target."""
        direction = self.get_direction(current, target)
        if direction is None:
            return True  # not a single orthogonal step -- treat as blocked
        return self.building.get_tile(current).has_wall(direction)

    def is_valid_move(self, current: Cell, target: Cell) -> bool:
        """
        A move is valid only if:
          1. target is adjacent to current (and in bounds), AND
          2. there is no wall blocking that edge.
        """
        if not self.is_adjacent(current, target):
            return False
        if self.has_wall_between(current, target):
            return False
        return True


# ---------------------------------------------------------------------------
# Bare CLI: prints the map and takes manual input.
# ---------------------------------------------------------------------------

def print_map(building: Building, player: Cell) -> None:
    """
    Renders the grid as ASCII art.
    '@' = player, '.' = open cell, '|' = vertical wall, '-' = horizontal wall.
    """
    for row in range(building.height):
        row_line = ""
        for col in range(building.width):
            cell = (row, col)
            row_line += "@" if cell == player else "."
            if col < building.width - 1:
                wall = building.get_tile(cell).has_wall("e")
                row_line += "|" if wall else " "
        print(row_line)

        if row < building.height - 1:
            wall_line = ""
            for col in range(building.width):
                cell = (row, col)
                wall = building.get_tile(cell).has_wall("s")
                wall_line += "-" if wall else " "
                if col < building.width - 1:
                    wall_line += " "
            print(wall_line)


def build_example_building() -> Building:
    """A small 3x3 example building with a couple of walls, to demo the CLI."""
    building = Building(width=3, height=3)
    building.add_wall_between((0, 0), (0, 1))  # wall east of top-left
    building.add_wall_between((1, 1), (2, 1))  # wall south of middle-middle
    return building


def main() -> None:
    building = build_example_building()
    validator = MoveValidator(building)
    player: Cell = (0, 0)

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

        row_shift, col_shift = DIRECTIONS[move]
        target: Cell = (player[0] + row_shift, player[1] + col_shift)

        if validator.is_valid_move(player, target):
            player = target
        else:
            print("Invalid move: blocked by a wall or out of bounds.")

        print_map(building, player)


if __name__ == "__main__":
    main()