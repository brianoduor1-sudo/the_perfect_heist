SYSTEM_PROMPT = """You are the Ai Game Master.You MUST respond ONLY with valid json matching the 
the requested SCHEMA.Do not include extre markdown prose outside the JSON block.
"""
STRATEGIST_TEMPLATE = """Current Game State(Coordinates are now (row, col)):
{game_state}

Player's Current Goal:
{player_goal}

Determine the next strategic move
You MUST respond with a strict JSON Object in this EXACT format:
{{"action": "move", "direction": "north"}}

The 'action' must be 'move', 'pick_up'or 'wait'.
The 'direction' must be 'north','south','east', or 'west' (only if action is 'move')
"""
