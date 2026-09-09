"""
Test suite for move_validator.py

Run with:
    python -m unittest test.py -v
or simply:
    python test.py
"""

import unittest

from move_validator import Tile, Building, MoveValidator


class TestTile(unittest.TestCase):
    def test_new_tile_has_no_walls(self):
        tile = Tile()
        for direction in ("n", "s", "e", "w"):
            self.assertFalse(tile.has_wall(direction))

    def test_add_wall_sets_only_that_side(self):
        tile = Tile()
        tile.add_wall("n")
        self.assertTrue(tile.has_wall("n"))
        self.assertFalse(tile.has_wall("s"))
        self.assertFalse(tile.has_wall("e"))
        self.assertFalse(tile.has_wall("w"))


class TestBuilding(unittest.TestCase):
    def setUp(self):
        self.building = Building(width=3, height=3)

    def test_in_bounds(self):
        self.assertTrue(self.building.in_bounds((0, 0)))
        self.assertTrue(self.building.in_bounds((2, 2)))
        self.assertFalse(self.building.in_bounds((-1, 0)))
        self.assertFalse(self.building.in_bounds((0, 3)))
        self.assertFalse(self.building.in_bounds((3, 0)))

    def test_add_wall_between_marks_both_sides(self):
        self.building.add_wall_between((0, 0), (0, 1))
        self.assertTrue(self.building.get_tile((0, 0)).has_wall("e"))
        self.assertTrue(self.building.get_tile((0, 1)).has_wall("w"))
        # Unrelated sides remain open.
        self.assertFalse(self.building.get_tile((0, 0)).has_wall("s"))

    def test_add_wall_between_vertical_neighbors(self):
        self.building.add_wall_between((1, 1), (2, 1))
        self.assertTrue(self.building.get_tile((1, 1)).has_wall("s"))
        self.assertTrue(self.building.get_tile((2, 1)).has_wall("n"))

    def test_add_wall_between_non_adjacent_raises(self):
        with self.assertRaises(ValueError):
            self.building.add_wall_between((0, 0), (2, 2))

    def test_add_wall_between_same_cell_raises(self):
        with self.assertRaises(ValueError):
            self.building.add_wall_between((0, 0), (0, 0))


class TestMoveValidator(unittest.TestCase):
    def setUp(self):
        self.building = Building(width=3, height=3)
        self.validator = MoveValidator(self.building)

    # -- is_adjacent -------------------------------------------------
    def test_adjacent_orthogonal_step_is_true(self):
        self.assertTrue(self.validator.is_adjacent((1, 1), (1, 2)))
        self.assertTrue(self.validator.is_adjacent((1, 1), (0, 1)))

    def test_diagonal_step_is_not_adjacent(self):
        self.assertFalse(self.validator.is_adjacent((1, 1), (0, 0)))

    def test_same_cell_is_not_adjacent(self):
        self.assertFalse(self.validator.is_adjacent((1, 1), (1, 1)))

    def test_target_out_of_bounds_is_not_adjacent(self):
        self.assertFalse(self.validator.is_adjacent((0, 0), (-1, 0)))
        self.assertFalse(self.validator.is_adjacent((2, 2), (2, 3)))

    # -- get_direction -------------------------------------------------
    def test_get_direction_each_way(self):
        self.assertEqual(self.validator.get_direction((1, 1), (0, 1)), "n")
        self.assertEqual(self.validator.get_direction((1, 1), (2, 1)), "s")
        self.assertEqual(self.validator.get_direction((1, 1), (1, 2)), "e")
        self.assertEqual(self.validator.get_direction((1, 1), (1, 0)), "w")

    def test_get_direction_non_adjacent_returns_none(self):
        self.assertIsNone(self.validator.get_direction((1, 1), (2, 2)))

    # -- is_valid_move -------------------------------------------------
    def test_valid_move_no_wall(self):
        self.assertTrue(self.validator.is_valid_move((0, 0), (0, 1)))

    def test_invalid_move_out_of_bounds(self):
        self.assertFalse(self.validator.is_valid_move((0, 0), (-1, 0)))

    def test_invalid_move_not_orthogonal(self):
        self.assertFalse(self.validator.is_valid_move((0, 0), (1, 1)))

    def test_invalid_move_blocked_by_wall(self):
        self.building.add_wall_between((0, 0), (0, 1))
        self.assertFalse(self.validator.is_valid_move((0, 0), (0, 1)))
        # Wall blocks from the other side too.
        self.assertFalse(self.validator.is_valid_move((0, 1), (0, 0)))

    def test_wall_only_blocks_its_own_edge(self):
        self.building.add_wall_between((0, 0), (0, 1))
        # Moving south from (0,0) should still be fine.
        self.assertTrue(self.validator.is_valid_move((0, 0), (1, 0)))

    def test_matches_example_building_from_cli(self):
        # Same walls as build_example_building() in move_validator.py
        self.building.add_wall_between((0, 0), (0, 1))
        self.building.add_wall_between((1, 1), (2, 1))

        self.assertFalse(self.validator.is_valid_move((0, 0), (0, 1)))
        self.assertTrue(self.validator.is_valid_move((0, 0), (1, 0)))
        self.assertFalse(self.validator.is_valid_move((1, 1), (2, 1)))
        self.assertTrue(self.validator.is_valid_move((1, 1), (1, 2)))


if __name__ == "__main__":
    unittest.main()