import json
import logging
from typing import Dict, Any

from goal_parser import parse_and_validate_ai_response
from prompts import SYSTEM_PROMPT, STRATEGIST_TEMPLATE

logger = logging.getLogger(__name__)


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
                "guard_positions": (list(g.position) for g in game_state.guards),
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
            validated_response = parse_and_validate_ai_response(raw_response)

            if validated_response:
                move_success = game_state.attempt_player_move(validated_response.move)

                if move_success:
                    game_state.strikes = 0
                    return {"mode": "ai", "data": validated_response.model_dump()}
                else:
                    game_state.strikes += 1
                    logger.warning(f"Python rejected AI move {validated_response.move}. Strike {game_state.strikes} / {self.max_strikes}")
            else:
                game_state.strikes += 1
                logger.warning(f"AI response validation failed. Strike {game_state.strikes} / {self.max_strikes}")
        except Exception as e:
            game_state.strikes += 1
            logger.error(f"AI client error during turn generation: {e}")

        if game_state.strikes >= self.max_strikes:
            logger.error("Max strikes reached. Falling back to manual mode.")
            game_state.mode = "manual"
            return self._manual_fallback_mode(game_state, player_goal)

        return {"mode": game_state.mode, "data": None}

    def _manual_fallback_mode(self) -> Dict[str, Any]:
        return {
            "mode":"manual",
            "data": {
                "status": "fallback",
                "narrative": "The Ai Game master is temporarily offline",
                "move": "",
                "status_updates": {},
                "next_options": ["Continue", "Retry Ai"]
            }
         
        }        