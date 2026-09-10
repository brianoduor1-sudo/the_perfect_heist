import pytest

from game.tile import Tile, TileType


def test_tile_from_char():
    assert Tile.from_char("#").tile_type == TileType.WALL
    assert Tile.from_char(".").tile_type == TileType.FLOOR
    assert Tile.from_char("E").tile_type == TileType.EXIT
    assert Tile.from_char("A").tile_type == TileType.ARTIFACT


def test_tile_walkable():
    assert Tile(TileType.WALL).is_walkable is False
    assert Tile(TileType.FLOOR).is_walkable is True
    assert Tile(TileType.EXIT).is_walkable is True
    assert Tile(TileType.ARTIFACT).is_walkable is True


def test_invalid_char_raises_error():
    with pytest.raises(ValueError):
        Tile.from_char("X")


def test_tile_equality():
    assert Tile(TileType.FLOOR) == Tile(TileType.FLOOR)
    assert Tile(TileType.FLOOR) != Tile(TileType.WALL)
