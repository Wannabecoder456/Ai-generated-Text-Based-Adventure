
import datetime


class Player:
    def __init__(self, name="Zachor"):
        self.name = name
        self.health = 100
        self.max_health = 100
        self.strength = 7
        self.agility = 6
        self.luck = 5
        self.sanity = 10
        self.corruption = 0
        self.reputation = 0
        self.inventory = []
        self.last_login = datetime.datetime.now()
        
        # Add level system attributes
        self.level = 1
        self.stat_points = 0
        self.max_stat = 10
        self.hordes_unlocked = False
        self.available_roles = []

    def is_alive(self):
        return self.health > 0

    def to_dict(self):
        """Convert player to dictionary for level_up system compatibility"""
        return {
            'name': self.name,
            'level': self.level,
            'stat_points': self.stat_points,
            'max_stat': self.max_stat,
            'health': self.health,
            'max_health': self.max_health,
            'reputation': self.reputation,
            'corruption': self.corruption,
            'hordes_unlocked': self.hordes_unlocked,
            'available_roles': self.available_roles,
            'strength': self.strength,
            'agility': self.agility,
            'luck': self.luck,
            'sanity': self.sanity,
            'inventory': self.inventory
        }

    def from_dict(self, data):
        """Update player from dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def print_stats(self):
        print(f"\n== {self.name.upper()} ==")
        print(f"Level: {self.level}")
        print(f"Health: {self.health}/{self.max_health}")
        print(f"Strength: {self.strength}")
        print(f"Agility: {self.agility}")
        print(f"Luck: {self.luck}")
        print(f"Sanity: {self.sanity}")
        print(f"Corruption: {self.corruption}")
        print(f"Reputation: {self.reputation}")
        print(f"Stat Points: {self.stat_points}")
        print(f"Available Roles: {self.available_roles}")
