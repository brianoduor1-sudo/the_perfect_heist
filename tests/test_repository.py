from persistence.repository import GameRepository

EXAMPLE_STATE = {
    "player": {
        "position": [2, 4],
        "inventory": ["artifact"],
        "caught": False,
    },
    "guards": [
        {"position": [3, 3], "patrol_index": 1}
    ],
    "goal": "steal_and_escape",
    "items_collected": ["artifact"],
    "turn_count": 12,
}


def test_save_and_load_round_trip(tmp_path):
    repo = GameRepository()
    path = tmp_path / "save.json"

    repo.save(EXAMPLE_STATE, str(path))
    loaded = repo.load(str(path))

    assert loaded == EXAMPLE_STATE