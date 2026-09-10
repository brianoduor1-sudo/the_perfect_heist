import json


class GameRepository:

    def save(self, state, path):
        with open(path, "w") as file:
            json.dump(state, file, indent=2)

    def load(self, path):
        with open(path, "r") as file:
            return json.load(file)
