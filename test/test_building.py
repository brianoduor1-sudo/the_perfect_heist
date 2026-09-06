import os

import pytest

from game.tile import Tile, TileType
from game.building import Building


# Path to the sample map used in the tests
MAP_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "map.txt"
)


# ---- Tile -------------------------------------------------------------

def test_tile_from_char_walkable_types():
    # Floor, exit and artifact tiles should be walkable
    assert Tile.from_char(".").is_walkable
    assert Tile.from_char("E").is_walkable
    assert Tile.from_char("A").is_walkable


def test_tile_from_char_wall_not_walkable():
    # Walls should block movement
    wall = Tile.from_char("#")
    assert wall.is_wall
    assert not wall.is_walkable


def test_tile_from_char_invalid_raises():
    # Unknown map characters should raise an error
    with pytest.raises(ValueError):
        Tile.from_char("?")


def test_tile_to_char_round_trip():
    # Converting a tile to a character should keep the original value
    for ch in ["#", ".", "E", "A"]:
        assert Tile.from_char(ch).to_char() == ch


# ---- Building: construction -----------------------------------------

def test_building_rejects_empty_grid():
    # A Building needs at least one row
    with pytest.raises(ValueError):
        Building([])


def test_building_rejects_ragged_rows():
    # All rows in the map must have the same width
    grid = [
        [Tile(TileType.FLOOR), Tile(TileType.FLOOR)],
        [Tile(TileType.FLOOR)],
    ]

    with pytest.raises(ValueError):
        Building(grid)


# ---- Building: from_file / level loading ----------------------------

def test_building_loads_from_map_file():
    # Check that the sample map loads with the expected size
    building = Building.from_file(MAP_PATH)

    assert building.width == 10
    assert building.height == 9


# ---- Building: walkability / wall collision --------------------------

def test_border_is_not_walkable():
    building = Building.from_file(MAP_PATH)

    # Border tiles are walls in the MVP map
    assert not building.is_walkable((0, 0))
    assert not building.is_walkable((0, 4))


def test_interior_floor_is_walkable():
    building = Building.from_file(MAP_PATH)

    # Check that normal floor tiles can be entered
    assert building.is_walkable((1, 1))
    assert building.is_walkable((5, 5))


def test_out_of_bounds_is_not_walkable():
    building = Building.from_file(MAP_PATH)

    # Positions outside the map should not be walkable
    assert not building.is_walkable((-1, 0))
    assert not building.is_walkable((100, 100))
    assert not building.is_walkable((0, 100))


def test_tile_at_out_of_bounds_raises():
    building = Building.from_file(MAP_PATH)

    # Accessing an invalid position should raise an error
    with pytest.raises(ValueError):
        building.tile_at((-1, -1))


# ---- Building: find_label --------------------------------------------

def test_find_label_locates_exit():
    building = Building.from_file(MAP_PATH)

    # The exit should be found at the expected position
    assert building.find_label(TileType.EXIT) == [(8, 7)]


def test_find_label_locates_artifact():
    building = Building.from_file(MAP_PATH)

    # The artifact should be found at the expected position
    assert building.find_label(TileType.ARTIFACT) == [(4, 3)]


def test_find_label_returns_empty_list_when_absent():
    # A map without an exit should return an empty list
    grid = [[Tile(TileType.FLOOR)] * 3 for _ in range(3)]
    building = Building(grid)

    assert building.find_label(TileType.EXIT) == []