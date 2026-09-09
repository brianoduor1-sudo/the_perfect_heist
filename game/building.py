from typing import List, Tuple
from .tile import Tile, TileType

Position = Tuple[int, int]


class Building:

    def __init__(self, grid: List[List[Tile]]):
        if not grid or not grid[0]:
            raise ValueError("Grid must be non-empty")

        width = len(grid[0])
        for row in grid:
            if len(row) != width:
                raise ValueError("All rows must have equal width")

        self.grid = grid
        self.height = len(grid)
        self.width = width

    @classmethod
    def from_file(cls, path: str) -> "Building":
        with open(path, "r", encoding="utf-8") as file:
            lines = [line.rstrip("\n") for line in file]

        while lines and not lines[-1]:
            lines.pop()

        return cls.from_lines(lines)

    @classmethod
    def from_lines(cls, lines: List[str]) -> "Building":
        grid = [[Tile.from_char(char) for char in line] for line in lines]
        return cls(grid)

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, position: Position) -> Tile:
        if not self.in_bounds(position):
            raise ValueError(f"Position {position} is out of bounds")
        x, y = position
        return self.grid[y][x]

    def get_tile(self, position: Position) -> Tile:
        return self.tile_at(position)

    def is_walkable(self, position: Position) -> bool:
        return self.in_bounds(position) and self.tile_at(position).is_walkable

    def is_wall(self, position: Position) -> bool:
        return self.in_bounds(position) and self.tile_at(position).is_wall

    def find_label(self, tile_type: TileType) -> List[Position]:
        return [
            (x, y)
            for y, row in enumerate(self.grid)
            for x, tile in enumerate(row)
            if tile.tile_type is tile_type
        ]

    def __repr__(self):
        return f"Building({self.width}x{self.height})"
