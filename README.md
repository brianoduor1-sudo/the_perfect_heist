# 🕵️ The Perfect Heist

**AI-Powered Terminal Stealth Game: Python + OOP**

> **AI proposes. The engine decides.**

## Overview

A terminal-based stealth game where you navigate a building, avoid guards, grab an artifact, and reach the exit undetected. A locally running AI (via **Ollama**) suggests moves as a strategic assistant, but the Python game engine validates every move against the rules before executing it. The AI never controls the game directly.

## Objective

1. Navigate the building
2. Avoid guards
3. Collect the artifact
4. Reach the exit
5. Avoid detection throughout

## AI Integration

```
AI → Strategist → Game Engine → Move Validation → Execute or Reject
```

The AI proposes moves based on game state; the engine decides whether they're legal. If Ollama is unavailable or repeatedly returns invalid moves, the game falls back to manual play.

## Gameplay Elements

- **Player**: position, inventory, movement, caught/detected state
- **Guards**: patrol routes, detection logic
- **Building**: map grid, tile access, boundary checks
- **Goals**: `StealItemGoal`, `ReachExitGoal`, `AvoidDetectionGoal`, `CompositeGoal`

## Map Legend

| Symbol | Meaning |
|---|---|
| `#` | Wall |
| `.` | Floor |
| `A` | Artifact |
| `E` | Exit |

## Architecture

```
CLI → GameState (Player, Guard, Goal, MoveValidator)
Ollama → Strategist → GameState → MoveValidator → Game Rules
```

AI logic stays separate from domain logic; every suggestion passes through the same rules as a human move.

## Project Structure

```
the_perfect_heist/
├── ai/          (goal_parser, ollama_client, prompts, strategist)
├── cli/         (interface)
├── data/        (map.txt)
├── game/        (building, game_state, goal, guard, move_validator, player, tile)
├── persistence/ (repository)
├── test/
├── config.py, main.py, requirements.txt
```

## Persistence

Game data is saved/loaded as JSON via a repository layer, kept separate from game rules.

## Testing

```bash
pytest -v
```
Covers player/guard/building behavior, goals, validation, game state, AI integration, and persistence.

## Setup

```bash
git clone https://github.com/brianoduor1-sudo/the_perfect_heist.git
cd the_perfect_heist
python -m venv venv && source venv/bin/activate   
pip install -r requirements.txt
ollama pull llama3   
python main.py
```

## Turn Flow

State → Move proposed (player/AI) → Validate → Execute/Reject → Guards update → Detection check → Goal check → Continue/Win/Lose

## Tech Stack

Python · OOP · Ollama · JSON · pytest · Git/GitHub · CLI

## Team

| Member | Role |
|---|---|
| Ralph Njuguna | Player & Goal System / Product Owner |
| Brian Oduor | Guard Movement & Detection / Scrum Master |
| Patricia Ndung'u | Building, Map & Persistence |
| Joy Dannah | Ollama AI Integration |
| Peter Ng'ang'a | Game Service, Validation & CLI |
| Nicole Jada | Integration, Testing & Documentation |

## Future Improvements

Multiple levels, smarter guard AI, additional objectives, difficulty levels, GUI, multiplayer, procedural maps, save slots.

## License

MIT © 2026 The Perfect Heist Team

**Repo:** https://github.com/brianoduor1-sudo/the_perfect_heist

---
> **AI proposes. The engine decides.**
