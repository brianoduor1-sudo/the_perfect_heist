
import pytest  # type: ignore

from game.tile import Tile, TileType


def test_tile_from_char():
    # Check that each map character creates the correct Tile type
    assert Tile.from_char("#").tile_type == TileType.WALL
    assert Tile.from_char(".").tile_type == TileType.FLOOR
    assert Tile.from_char("E").tile_type == TileType.EXIT
    assert Tile.from_char("A").tile_type == TileType.ARTIFACT


def test_tile_walkable():
    # Walls cannot be walked on
    assert Tile(TileType.WALL).is_walkable is False

    # Floor, exit and artifact tiles can be walked on
    assert Tile(TileType.FLOOR).is_walkable is True
    assert Tile(TileType.EXIT).is_walkable is True
    assert Tile(TileType.ARTIFACT).is_walkable is True


def test_invalid_char_raises_error():
    # Unknown map characters should raise a ValueError
    with pytest.raises(ValueError):
        Tile.from_char("X")


def test_tile_equality():
    # Tiles with the same type should be equal
    assert Tile(TileType.FLOOR) == Tile(TileType.FLOOR)

    # Tiles with different types should not be equal
    assert Tile(TileType.FLOOR) != Tile(TileType.WALL)


