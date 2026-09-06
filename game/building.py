"""
Building  the map grid: loads a level, answers walkability and
wall-collision questions, and finds special tiles (exit, artifact).

Part of Epic 3 (Building, Map & Persistence) — PH-3.
"""
from typing import List, Tuple

from .tile import Tile, TileType

# Positions use (x, y) coordinates
Position = Tuple[int, int]


class Building:
    """Represents the game's map as a grid of Tiles."""

    def __init__(self, grid: List[List[Tile]]):
        # The map must contain at least one tile
        if not grid or not grid[0]:
            raise ValueError("Grid must be non-empty")

        width = len(grid[0])

        # Make sure all rows have the same width
        for row in grid:
            if len(row) != width:
                raise ValueError("All rows in the map must have equal width")

        self.grid = grid
        self.height = len(grid)
        self.width = width

    @classmethod
    def from_file(cls, path: str) -> "Building":
        """Load a level from a text map file."""
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.rstrip("\n") for line in f]

        # Remove empty lines at the end of the map
        while lines and lines[-1] == "":
            lines.pop()

        # Convert each map character into a Tile
        grid = [[Tile.from_char(ch) for ch in line] for line in lines]

        return cls(grid)

    def in_bounds(self, position: Position) -> bool:
        # Check if a position is inside the map
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, position: Position) -> Tile:
        """Return the tile at a given position."""
        if not self.in_bounds(position):
            raise ValueError(f"Position {position} is out of bounds")

        x, y = position
        return self.grid[y][x]

    def is_walkable(self, position: Position) -> bool:
        """Check if a position can be entered."""
        # Walls and positions outside the map cannot be entered
        return self.in_bounds(position) and self.tile_at(position).is_walkable

    def find_label(self, tile_type: TileType) -> List[Position]:
        """Find all positions containing a specific tile type."""
        # Useful for finding the exit or artifact
        return [
            (x, y)
            for y, row in enumerate(self.grid)
            for x, tile in enumerate(row)
            if tile.tile_type is tile_type
        ]

    def __repr__(self):
        # Helpful when checking the Building during debugging
        return f"Building({self.width}x{self.height})"