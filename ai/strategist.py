import json
import logging
from typing import Dict, Any
from .goal_parser import parse_and_validate_ai_response
from .prompts import SYSTEM_PROMPT, STRATEGIST_TEMPLATE

logger = logging.getLogger(__name__)

FULL_WORD_TO_LETTER = {
    "north": "n", "south": "s", "east": "e", "west": "w"
}


class Strategist:
    """Task 2 & Task 4: Serializes game state and handles 3-strike fallback"""

    def __init__(self, ai_client, max_strikes: int = 3):
        self.ai_client = ai_client
        self.max_strikes = max_strikes

    def serialize_game_state(self, game_state: Any) -> str:
        """Task 2 : Design game_state_to_prompt_serializer."""
        if hasattr(game_state, "to_dict"):
            return json.dumps(game_state.to_dict(), indent=2)
        
        elif hasattr(game_state,"player") and hasattr(game_state,"guards"):
            return json.dumps({
                "player_pos": list(game_state.player.position),
                "guard_positions": [list(g.position) for g in game_state.guards],
                "goal": game_state.goal.description
            }, indent=2)
        return json.dumps(game_state, indent=2)

    def take_turn(self, game_state: Any, player_goal: str) -> Dict[str, Any]:
        """Task 4 :Implement 3-strikes fallback to manual mode."""
        if not hasattr(game_state, "strikes"):
            game_state.strikes = 0
            game_state.mode = "ai"

        serialized_state = self.serialize_game_state(game_state)
        prompt = STRATEGIST_TEMPLATE.format(game_state=serialized_state, player_goal=player_goal)

        try:
            raw_response = self.ai_client.generate(prompt=prompt, system=SYSTEM_PROMPT)
            validated = parse_and_validate_ai_response(raw_response)

            if validated:
                full_direction = getattr(validated, 'direction', None)
                action = getattr(validated, 'action', None)
                letter_move = None

                if action == 'move' and full_direction in FULL_WORD_TO_LETTER:
                    letter_move = FULL_WORD_TO_LETTER[full_direction]
                    move_success = game_state.attempt_player_move(letter_move)

                    if move_success:
                        game_state.strikes = 0
                        return {"mode": "ai", "data": {"status": "success", "narrative": "Ai moved", "move": letter_move}}

                    game_state.strikes += 1
                    logger.warning(f"Python rejected AI move {full_direction}. Strike {game_state.strikes} / {self.max_strikes}")
                else:
                    game_state.strikes += 1
                    logger.warning(f"Ai gave non-move action or invalid direction. Strike {game_state.strikes}/{self.max_strikes}")
            else:
                game_state.strikes += 1
                logger.warning(f"AI response validation failed. Strike {game_state.strikes} / {self.max_strikes}")
        except Exception as e:
            game_state.strikes += 1
            logger.error(f"AI client error during turn generation: {e}")

        if game_state.strikes >= self.max_strikes:
            logger.error("Max strikes reached. Falling back to manual mode.")
            game_state.mode = "manual"
            return self._manual_fallback_mode()

        return {"mode":"ai", "data":{"status": "pending", "narrative": f"Ai tried to move {full_direction} but was blocked"}}

    def _manual_fallback_mode(self) -> Dict[str, Any]:
        return {
            "mode":"manual",
            "data": {
                "status": "fallback",
                "narrative": "The Ai Game master is temporarily offline",
                "move": "",
                "status_updates": {},
                "next_options": ["Continue"]
            }
         
        }        