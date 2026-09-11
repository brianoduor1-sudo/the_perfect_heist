import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai.ollama_client import AiClient, StubAiClient
from ai.strategist import Strategist
from game.game_state import GameState
from game.building import Building
from game.guard import Guard
from game.move_validator import MoveValidator
from game.player import Player


class TestGoal:
    def __init__(self):
        self.description = "Steal the artifact and escape"

    def is_complete(self, state):
        return False


def _response_value(response, key, default=None):
    if callable(response):
        try:
            return response(key)
        except TypeError:
            pass
    if isinstance(response, dict):
        return response.get(key, default)
    return getattr(response, key, default)


def main():
    use_stub = "--stub" in sys.argv
    run_once = "--once" in sys.argv

    _ = MoveValidator

    if use_stub:
        print("--- Testing with STUB (no ollama) ---")
        ai_client = StubAiClient(canned_responses=[
            {"action": "move", "direction": "north"},
            {"action": "move", "direction": "south"},
            {"action": "move", "direction": "east"},
        ])
    else:
        print("--- Testing with Real Ollama ---")
        ai_client = AiClient(model="llama3", timeout=120)
        if not ai_client.check_connection():
            print("X Ollama offline")
            return

    building = Building.from_lines([
        "...",
        "...",
        "...",
    ])
    player = Player((0, 0))
    guard = Guard([(1, 1)])
    goal = TestGoal()

    game_state = GameState(building, player, [guard], goal)
    game_state.mode = "ai"
    strategist = Strategist(ai_client=ai_client, max_strikes=3)

    print("\nStarting Integration Test.")
    while not game_state.is_game_over() and game_state.mode != "manual":
        print(f"\n (Turn {game_state.turn_count} Mode: {game_state.mode})")

        response = strategist.take_turn(game_state, goal.description)

        if _response_value(response, "model") == "manual":
            print("3-Strike Fallback Success! AI failed 3 times switching to manual mode.")
            break

        data = _response_value(response, "data") or {}
        narrative = data.get("narrative", "No narrative") if isinstance(data, dict) else "No narrative"
        print(f"AI said: {narrative}")

        if run_once:
            print("One-turn test completed")
            break


if __name__ == "__main__":
    main()

