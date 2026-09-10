import json

from game.bulding import Building
from game.player import Player
from game.guard import Guard
from game.goal import StealItemGoal
from game.tile import TileType
from persistence.repository import GameRepository
from ai.ollama_client import AiClient, StubAiClient
from ai.strategist import Strategist


MAP_PATH = "data/map.txt"
SAVE_PATH = "data/save.json"


def find_start_position(building):
    for y in range(building.height):
        for x in range(building.width):
            if building.grid[y][x].tile_type == TileType.FLOOR:
                return (x, y)

    raise ValueError("No floor tile found.")


def display_map(building, player, guard):
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

    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        print("\nNo valid save found.")


def build_strategist():
    ai_client = AiClient(model="llama3")

    if ai_client.check_connection():
        return Strategist(ai_client)

    print("\nOllama is not running. Using the offline AI stub.")
    return Strategist(StubAiClient())


def get_ai_move(strategist, player, guard, goal):
    state = {
        "player_pos": list(player.position),
        "guard_pos": list(guard.position),
        "inventory": list(player.inventory),
        "goal": goal.describe(),
    }

    result = strategist.decide_move(state, goal.describe())

    if result["mode"] == "manual":
        print("\nAI is offline. Switching to manual play.")
        return None

    if result["status"] != "success":
        print("\nAI gave an invalid move.")
        return None

    direction = {
        "n": "w",
        "s": "s",
        "e": "d",
        "w": "a",
    }

    move = direction[result["move"]]

    print(f"\nAI chose '{result['move']}'.")
    return move


def main():
    print("\n=== THE PERFECT HEIST ===")
    print("Steal the artifact and escape!\n")

    building = Building.from_file(MAP_PATH)
    repo = GameRepository()

    player = Player(find_start_position(building))

    guard = Guard(
        patrol_path=[
            (1, 4),
            (2, 4),
            (2, 6),
            (1, 6),
        ],
        vision_range=1,
    )

    goal = StealItemGoal("artifact")
    strategist = build_strategist()

    moves = {
        "w": (0, -1),
        "s": (0, 1),
        "a": (-1, 0),
        "d": (1, 0),
    }

    while True:
        display_map(building, player, guard)

        print(f"\nPlayer: {player.position}")
        print(f"Inventory: {player.inventory}")
        print(f"Goal: {goal.describe()}")

        command = input(
            "\nMove (w/a/s/d), ai, save, load, or q: "
        ).strip().lower()

        if command == "q":
            print("Thanks for playing!")
            break

        if command == "save":
            save_game(repo, player, guard)
            continue

        if command == "load":
            load_game(repo, player, guard)
            continue

        if command == "ai":
            command = get_ai_move(
                strategist,
                player,
                guard,
                goal,
            )

            if command is None:
                continue

        if command not in moves:
            print("Invalid command.")
            continue

        dx, dy = moves[command]
        x, y = player.position
        new_position = (x + dx, y + dy)

        if not building.is_walkable(new_position):
            print("You cannot walk through a wall!")
            continue

        player.move_to(new_position)

        tile = building.grid[new_position[1]][new_position[0]]

        if (
            tile.tile_type == TileType.ARTIFACT
            and not player.has_item("artifact")
        ):
            player.pick_up("artifact")
            print("\nYou found the artifact!")
            print("Now reach the exit!")

        guard.patrol_step()

        if guard.detects_player(player.position, building):
            player.mark_caught()
            print("\nYou were caught by the guard!")
            print("GAME OVER")
            break

        if (
            player.has_item("artifact")
            and tile.tile_type == TileType.EXIT
        ):
            print("\nYou stole the artifact and escaped!")
            print("HEIST COMPLETE!")
            break


if __name__ == "__main__":
    main()
