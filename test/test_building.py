import os

import pytest

from game.tile import Tile, TileType
from game.building import Building


MAP_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "map.txt"
)


def test_tile_from_char_walkable_types():
    assert Tile.from_char(".").is_walkable
    assert Tile.from_char("E").is_walkable
    assert Tile.from_char("A").is_walkable


def test_tile_from_char_wall_not_walkable():
    wall = Tile.from_char("#")
    assert wall.is_wall
    assert not wall.is_walkable


def test_tile_from_char_invalid_raises():
    with pytest.raises(ValueError):
        Tile.from_char("?")


def test_tile_to_char_round_trip():
    for ch in ["#", ".", "E", "A"]:
        assert Tile.from_char(ch).to_char() == ch


def test_building_rejects_empty_grid():
    with pytest.raises(ValueError):
        Building([])


def test_building_rejects_ragged_rows():
    grid = [
        [Tile(TileType.FLOOR), Tile(TileType.FLOOR)],
        [Tile(TileType.FLOOR)],
    ]
    with pytest.raises(ValueError):
        Building(grid)


def test_building_loads_from_map_file():
    building = Building.from_file(MAP_PATH)
    assert building.width == 10
    assert building.height == 8


def test_border_is_not_walkable():
    building = Building.from_file(MAP_PATH)
    assert not building.is_walkable((0, 0))
    assert not building.is_walkable((0, 4))


def test_interior_floor_is_walkable():
    building = Building.from_file(MAP_PATH)
    assert building.is_walkable((1, 1))
    assert building.is_walkable((5, 6))


def test_out_of_bounds_is_not_walkable():
    building = Building.from_file(MAP_PATH)
    assert not building.is_walkable((-1, 0))
    assert not building.is_walkable((100, 100))
    assert not building.is_walkable((0, 100))


def test_tile_at_out_of_bounds_raises():
    building = Building.from_file(MAP_PATH)
    with pytest.raises(ValueError):
        building.tile_at((-1, -1))


def test_is_wall():
    building = Building.from_file(MAP_PATH)
    assert building.is_wall((0, 0)) is True
    assert building.is_wall((1, 1)) is False


def test_find_label_locates_exit():
    building = Building.from_file(MAP_PATH)
    assert building.find_label(TileType.EXIT) == [(9, 6)]


def test_find_label_locates_artifact():
    building = Building.from_file(MAP_PATH)
    assert building.find_label(TileType.ARTIFACT) == [(3, 2)]


def test_find_label_returns_empty_list_when_absent():
    grid = [[Tile(TileType.FLOOR)] * 3 for _ in range(3)]
    building = Building(grid)
    assert building.find_label(TileType.EXIT) == []
