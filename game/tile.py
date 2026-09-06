"""
A Tile represents one square on the game map.

Epic 3: Building, Map & Persistence
Author: Patricia Ndungu
"""

from enum import Enum


class TileType(Enum):
    """The four types of tiles used on the map."""

    WALL = "wall"
    FLOOR = "floor"
    EXIT = "exit"
    ARTIFACT = "artifact"


# Map symbols
CHAR_TO_TYPE = {
    "#": TileType.WALL,
    ".": TileType.FLOOR,
    "E": TileType.EXIT,
    "A": TileType.ARTIFACT,
}


class Tile:
    """Represents one square on the game map."""

    def __init__(self, tile_type: TileType):
        self.tile_type = tile_type

    @property
    def is_walkable(self) -> bool:
        # Walls cannot be walked on
        return self.tile_type != TileType.WALL

    @classmethod
    def from_char(cls, char: str) -> "Tile":
        """Creates a Tile from a map character."""

        # Rejects unknown characters
        if char not in CHAR_TO_TYPE:
            raise ValueError(f"Unknown map character: {char!r}")

        return cls(CHAR_TO_TYPE[char])

    def to_char(self) -> str:
        """Converts this Tile back to its map character."""

        # Find matching character
        for char, tile_type in CHAR_TO_TYPE.items():
            if tile_type == self.tile_type:
                return char

        # Catches invalid tile types
        raise ValueError(f"No character mapping for {self.tile_type}")

    def __eq__(self, other):
        # Compares tile types
        return isinstance(other, Tile) and self.tile_type == other.tile_type

    def __hash__(self):
        # Allows use in sets and dictionaries
        return hash(self.tile_type)

    def __repr__(self):
        # Makes Tiles readable in tests
        return f"Tile({self.tile_type.value})"