
class Player:
    def __init__(self, position, inventory=None):
        self.position = position
        self.inventory = inventory or []
        self.caught = False
        self.noise_level = 0
 
    def move_to(self, new_position):
        self.position = new_position
 
    def pick_up(self, item_name):
        if item_name not in self.inventory:
            self.inventory.append(item_name)
 
    def has_item(self, item_name):
        return item_name in self.inventory
 
    def mark_caught(self):
        self.caught = True
 
    def __repr__(self):
        return f"Player(pos={self.position}, inventory={self.inventory}, caught={self.caught})"
 