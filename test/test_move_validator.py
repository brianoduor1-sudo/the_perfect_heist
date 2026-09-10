import unittest

from game.building import Building
from game.move_validator import MoveValidator


def make_building(lines):
    """Small helper: build a Building straight from a list of map rows."""
    return Building.from_lines(lines)


class TestMoveValidatorAdjacency(unittest.TestCase):
    def setUp(self):
        # 5x5 open room, no interior walls -- isolates adjacency logic
        # from walkability logic.
        lines = [
            "#####",
            "#...#",
            "#...#",
            "#...#",
            "#####",
        ]
        self.building = make_building(lines)
        self.validator = MoveValidator(self.building)

    def test_orthogonal_step_is_adjacent(self):
        self.assertTrue(self.validator.is_adjacent((1, 1), (2, 1)))  # east
        self.assertTrue(self.validator.is_adjacent((1, 1), (1, 2)))  # south

    def test_diagonal_step_is_not_adjacent(self):
        self.assertFalse(self.validator.is_adjacent((1, 1), (2, 2)))

    def test_same_position_is_not_adjacent(self):
        self.assertFalse(self.validator.is_adjacent((1, 1), (1, 1)))

    def test_out_of_bounds_target_is_not_adjacent(self):
        self.assertFalse(self.validator.is_adjacent((0, 0), (-1, 0)))
        self.assertFalse(self.validator.is_adjacent((4, 4), (5, 4)))

    def test_get_direction_each_way(self):
        self.assertEqual(self.validator.get_direction((2, 2), (2, 1)), "n")
        self.assertEqual(self.validator.get_direction((2, 2), (2, 3)), "s")
        self.assertEqual(self.validator.get_direction((2, 2), (3, 2)), "e")
        self.assertEqual(self.validator.get_direction((2, 2), (1, 2)), "w")

    def test_get_direction_non_adjacent_returns_none(self):
        self.assertIsNone(self.validator.get_direction((1, 1), (3, 3)))


class TestMoveValidatorWalkability(unittest.TestCase):
    def setUp(self):
        # Interior wall at (2,1) and (2,2); exit at (3,3); artifact at (1,3).
        lines = [
            "#####",
            "#.#.#",
            "#.#.#",
            "#A.E#",
            "#####",
        ]
        self.building = make_building(lines)
        self.validator = MoveValidator(self.building)

    def test_move_between_two_floor_tiles_is_valid(self):
        self.assertTrue(self.validator.is_valid_move((1, 1), (1, 2)))

    def test_move_onto_wall_tile_is_invalid(self):
        self.assertFalse(self.validator.is_valid_move((1, 1), (2, 1)))

    def test_move_onto_exit_tile_is_valid(self):
        self.assertTrue(self.validator.is_valid_move((2, 3), (3, 3)))

    def test_move_onto_artifact_tile_is_valid(self):
        self.assertTrue(self.validator.is_valid_move((2, 3), (1, 3)))

    def test_move_out_of_bounds_is_invalid(self):
        self.assertFalse(self.validator.is_valid_move((0, 1), (-1, 1)))

    def test_move_that_is_not_a_single_step_is_invalid(self):
        # Two steps away, even though both ends are floor tiles.
        self.assertFalse(self.validator.is_valid_move((1, 1), (1, 3)))

    def test_wall_blocks_from_both_sides(self):
        # Symmetric: can't step onto the wall from either neighbor.
        self.assertFalse(self.validator.is_valid_move((1, 1), (2, 1)))
        self.assertFalse(self.validator.is_valid_move((3, 1), (2, 1)))


class TestMoveValidatorAgainstRealMapFile(unittest.TestCase):
    """
    Sanity check using Building.from_lines the same way Building.from_file
    would build a real map -- catches integration issues that isolated
    unit tests might miss (e.g. row/column mixups).
    """

    def setUp(self):
        lines = [
            "########",
            "#..#...#",
            "#..#.#.#",
            "#....#.#",
            "#.##.#.#",
            "#....#E#",
            "########",
        ]
        self.building = make_building(lines)
        self.validator = MoveValidator(self.building)

    def test_start_corner_is_walkable(self):
        self.assertTrue(self.building.is_walkable((1, 1)))

    def test_walking_a_short_path_to_the_right(self):
        path = [(1, 1), (2, 1)]
        self.assertTrue(self.validator.is_valid_move(*path))

    def test_cannot_cut_through_interior_wall(self):
        # (3,1) is '#' in row index 1
        self.assertFalse(self.validator.is_valid_move((2, 1), (3, 1)))

    def test_exit_is_reachable_as_a_valid_move(self):
        # Row "#....#E#": E is at x=6, y=5. Its only open neighbor is
        # (6,4), a floor tile directly above it in row "#.##.#.#".
        self.assertTrue(self.validator.is_valid_move((6, 4), (6, 5)))


if __name__ == "__main__":
    unittest.main()