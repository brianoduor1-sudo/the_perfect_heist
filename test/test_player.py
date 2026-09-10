from game.player import Player

def test_pick_up_adds_item_to_inventory():
    player = Player(position=(0, 0))
    player.pick_up("artifact")
    assert player.has_item("artifact")

def test_pick_up_does_not_duplicate_items():
    player = Player(position=(0, 0))
    player.pick_up("artifact")
    player.pick_up("artifact")
    assert player.inventory.count("artifact") == 1

def test_has_item_returns_false_when_not_picked_up():
    player = Player(position=(0, 0))
    assert player.has_item("artifact") is False

def test_mark_caught_sets_caught_true():
    player = Player(position=(0, 0))
    player.mark_caught()
    assert player.caught is True