SYSTEM_PROMPT = """You are the Ai Game Master.You MUST respond ONLY with valid json matching the 
the requested SCHEMA.Do not include extre markdown prose outside the JSON block.
"""
STRATEGIST_TEMPLATE = """Current Game State(Coordinates are now (row, col)):
{game_state}

Player's Current Goal:
{player_goal}

Determine the next strategic move
Only respond with "nort", "south", "east", or "west"inside the direction field
Provide the output in the strict JSON format specified
"""
