from enum import Enum


class TileType(Enum):
    WALL = "wall"
    FLOOR = "floor"
    EXIT = "exit"
    ARTIFACT = "artifact"


CHAR_TO_TYPE = {
    "#": TileType.WALL,
    ".": TileType.FLOOR,
    "E": TileType.EXIT,
    "A": TileType.ARTIFACT,
}


class Tile:

    def __init__(self, tile_type):
        self.tile_type = tile_type

    @property
    def is_walkable(self):
        return self.tile_type != TileType.WALL

    @property
    def is_wall(self):
        return self.tile_type == TileType.WALL

    @classmethod
    def from_char(cls, char):
        if char not in CHAR_TO_TYPE:
            raise ValueError("Unknown map character")
        return cls(CHAR_TO_TYPE[char])

    def to_char(self):
        for char, tile_type in CHAR_TO_TYPE.items():
            if tile_type == self.tile_type:
                return char

    def __eq__(self, other):
        return isinstance(other, Tile) and self.tile_type == other.tile_type

    def __repr__(self):
        return f"Tile({self.tile_type.value})"
