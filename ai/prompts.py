SYSTEM_PROMPT = """You are the Ai Game Master. You Must respond ONLY with valid JSON matching the  requested schema
 Don't include extra markdown prose outside the JSON block
"""

STRATEGIST_TEMPLATE = """Current Game State[Coordinates are[x,y]]:
 {game_state}

Player's Current Goal:
 {player_goal}

Determine the next strategic move.
ONLY respond with "n", "s", "e", or "w" inside the "move" field.
Provide the output in the strict JSON format specified.
"""