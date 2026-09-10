
from typing import Optional, Tuple

from game.building import Building
from game.move_validator import MoveValidator, DIRECTIONS
from game.player import Player
from game.guard import Guard
from game.goal import Goal
from game.game_state import GameState
from ai.strategist import Strategist

Suggestion = Optional[Tuple[str, str]]  # (direction, reasoning) or None


def print_map(state: GameState) -> None:
    """Renders the grid: '@' player, 'G' guard, 'X' goal, '.' open floor."""
    building = state.building
    for row in range(building.height):
        row_line = ""
        for col in range(building.width):
            cell = (row, col)
            if cell == state.player.position:
                row_line += "@"
            elif any(cell == g.position for g in state.guards):
                row_line += "G"
            elif state.goal.is_reached(cell):
                row_line += "X"
            else:
                row_line += "."

            if col < building.width - 1:
                wall = building.get_tile(cell).has_wall("e")
                row_line += "|" if wall else " "
        print(row_line)

        if row < building.height - 1:
            wall_line = ""
            for col in range(building.width):
                cell = (row, col)
                wall = building.get_tile(cell).has_wall("s")
                wall_line += "-" if wall else " "
                if col < building.width - 1:
                    wall_line += " "
            print(wall_line)


def build_default_state() -> GameState:
    """
    Placeholder setup until map loading (data/map.txt) is wired in.
    Swap this for a real Building.from_file(...) / map parser later.
    """
    building = Building(width=5, height=5)
    player = Player(position=(0, 0))
    guards = [Guard(position=(4, 4), patrol_route=None)]
    goal = Goal(position=(4, 0))
    return GameState(building=building, player=player, guards=guards, goal=goal)


def get_ai_suggestion(state: GameState) -> Suggestion:
    """
    Asks the strategist for a move. Returns None (instead of raising) if
    the AI is unavailable, so the CLI can fall back to manual play cleanly.
    """
    try:
        strategist = Strategist(state)
        direction, reasoning = strategist.suggest_move()
        return direction, reasoning
    except Exception as exc:
        print(f"(AI suggestion unavailable: {exc})")
        return None


def describe_verdict(state: GameState, validator: MoveValidator, direction: str) -> str:
    """Human-readable explanation of whether `direction` is currently legal."""
    current = state.player.position
    row_shift, col_shift = DIRECTIONS[direction]
    target = (current[0] + row_shift, current[1] + col_shift)

    if not validator.building.in_bounds(target):
        return f"'{direction}' -> INVALID (out of bounds)"
    if not validator.is_adjacent(current, target):
        return f"'{direction}' -> INVALID (not a single step)"
    if validator.has_wall_between(current, target):
        return f"'{direction}' -> INVALID (blocked by wall)"
    return f"'{direction}' -> VALID"


def list_valid_moves(state: GameState, validator: MoveValidator) -> list:
    """All directions that are currently legal moves, for manual fallback."""
    current = state.player.position
    valid = []
    for direction, (row_shift, col_shift) in DIRECTIONS.items():
        target = (current[0] + row_shift, current[1] + col_shift)
        if validator.is_valid_move(current, target):
            valid.append(direction)
    return valid


def print_turn_info(state: GameState, validator: MoveValidator) -> None:
    suggestion = get_ai_suggestion(state)
    if suggestion is not None:
        direction, reasoning = suggestion
        print(f"\nAI suggests: '{direction}' -- {reasoning}")
        print(f"Validator verdict: {describe_verdict(state, validator, direction)}")
    else:
        print("\nNo AI suggestion this turn.")

    valid_moves = list_valid_moves(state, validator)
    if valid_moves:
        print(f"Manual fallback -- valid moves right now: {', '.join(valid_moves)}")
    else:
        print("Manual fallback -- no valid moves from this position!")


def prompt_move() -> str:
    return input("\nMove (n/s/e/w) or q to quit: ").strip().lower()


def run() -> None:
    state = build_default_state()
    validator = MoveValidator(state.building)

    print("Stealth CLI -- reach 'X' without a guard seeing you. 'q' to quit.")
    print_map(state)

    while True:
        print_turn_info(state, validator)
        move = prompt_move()

        if move == "q":
            print("Goodbye!")
            return

        if move not in DIRECTIONS:
            print("Unrecognized command. Use n, s, e, w, or q.")
            continue

        row_shift, col_shift = DIRECTIONS[move]
        current = state.player.position
        target = (current[0] + row_shift, current[1] + col_shift)

        if not validator.is_valid_move(current, target):
            print("Invalid move: blocked by a wall or out of bounds.")
            print_map(state)
            continue

        state.player.move_to(target)
        state.tick()  # let guards move / react
        print_map(state)

        if any(g.sees(state.player.position) for g in state.guards):
            print("Spotted! Game over.")
            return

        if state.is_over():
            print("You reached the goal!" if state.won() else "Game over.")
            return


if __name__ == "__main__":
    run()