

import json

from game.building import Building
from game.player import Player
from game.guard import Guard
from game.goal import StealItemGoal
from game.tile import TileType
from persistence.repository import GameRepository


MAP_PATH = "data/map.txt"
SAVE_PATH = "data/save.json"


def find_start_position(building):
    """Find the first floor tile for the player."""
    for y in range(building.height):
        for x in range(building.width):
            if building.grid[y][x].tile_type == TileType.FLOOR:
                return (x, y)

    raise ValueError("No walkable floor tiles found in map.")


def display_map(building, player, guard):
    """Display the map with the player and guard."""
    for y, row in enumerate(building.grid):
        line = ""

        for x, tile in enumerate(row):
            position = (x, y)

            if position == player.position:
                line += "P"
            elif position == guard.position:
                line += "G"
            else:
                line += tile.to_char()

        print(line)


def save_game(repo, player, guard):
    """Save the current player and guard state."""
    data = {
        "player": {
            "position": list(player.position),
            "inventory": list(player.inventory),
            "caught": player.caught,
        },
        "guard": guard.to_dict(),
    }

    repo.save(data, SAVE_PATH)
    print("\nGame saved.")


def load_game(repo, player, guard):
    """Load saved player and guard state."""
    try:
        data = repo.load(SAVE_PATH)

        player.position = tuple(data["player"]["position"])
        player.inventory = list(data["player"]["inventory"])
        player.caught = data["player"]["caught"]

        restored_guard = Guard.from_dict(
            data["guard"],
            patrol_path=guard.patrol_path,
        )

        guard._position = restored_guard.position
        guard._patrol_index = restored_guard._patrol_index
        guard._facing = restored_guard.facing

        print("\nGame loaded.")

    except (
        FileNotFoundError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ):
        print("\nNo valid save found.")


def main():
    """Start the game."""
    print("\n=== THE PERFECT HEIST ===")
    print("Steal the artifact and escape!\n")

    building = Building.from_file(MAP_PATH)
    repo = GameRepository()

    start_pos = find_start_position(building)
    player = Player(start_pos)

    # Guard patrol route
    guard_path = [
        (1, 4),
        (2, 4),
        (2, 6),
        (1, 6),
    ]

    guard = Guard(
        patrol_path=guard_path,
        vision_range=1,
    )

    goal = StealItemGoal("artifact")

    moves = {
        "w": (0, -1),
        "s": (0, 1),
        "a": (-1, 0),
        "d": (1, 0),
    }

    while True:
        print()
        display_map(building, player, guard)

        print(f"\nPlayer position: {player.position}")
        print(f"Inventory: {player.inventory}")
        print(f"Goal: {goal.describe()}")

        command = input(
            "\nMove (w/a/s/d), save, load, or 'q' to quit: "
        ).lower().strip()

        if command == "q":
            print("Thanks for playing!")
            break

        if command == "save":
            save_game(repo, player, guard)
            continue

        if command == "load":
            load_game(repo, player, guard)
            continue

        if command not in moves:
            print("Invalid move. Use w, a, s, d, save, load, or q.")
            continue

        dx, dy = moves[command]
        x, y = player.position
        new_position = (x + dx, y + dy)

        if not building.is_walkable(new_position):
            print("You cannot walk through a wall!")
            continue

        player.move_to(new_position)

        current_tile = building.grid[new_position[1]][new_position[0]]

        # Pick up the artifact
        if (
            current_tile.tile_type == TileType.ARTIFACT
            and not player.has_item("artifact")
        ):
            player.pick_up("artifact")
            print("\nYou found the artifact!")
            print("Now make it to the exit!")

        # Guard takes a turn
        guard.patrol_step()

        if guard.detects_player(player.position, building):
            player.mark_caught()
            print("\nYou were caught by the guard!")
            print("GAME OVER")
            break

        # Player wins after reaching the exit with the artifact
        if (
            player.has_item("artifact")
            and current_tile.tile_type == TileType.EXIT
        ):
            print("\nYou stole the artifact and escaped!")
            print("HEIST COMPLETE!")
            break


if __name__ == "__main__":
    main()
