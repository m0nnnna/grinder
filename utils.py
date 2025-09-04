import json
import os

def load_json(filename, default):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return default
    except json.JSONDecodeError:
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

DEFAULT_CONFIG = {
    "rarities": ["Common", "Uncommon", "Rare", "Epic"],
    "weights": [60, 30, 8, 2],
    "shop_prices": {
        "Common": 10,
        "Uncommon": 25,
        "Rare": 50,
        "Epic": 100
    }
}

DEFAULT_ENEMIES = {
    "//": "Format: [name, max_health, damage_range, xp_reward]",
    "1": ["Goblin", 20, [1, 3], 10],
    "2": ["Troll", 40, [4, 6], 20],
    "3": ["Dragon", 60, [7, 9], 30]
}

DEFAULT_GEAR = {
    "weapons": {
        "Common": [
            ["Club", "Basic attack", 6, 8],
            ["Dagger", "Basic attack", 5, 7]
        ],
        "Uncommon": [
            ["Sword", "Double attack", 8, 10]
        ],
        "Rare": [
            ["Axe", "Crit", 10, 12]
        ],
        "Epic": [
            ["Thunder Axe", "Crit", 15, 20]
        ]
    },
    "armor": {
        "Common": [
            ["Cloth Robe", "Basic defense", 4],
            ["Leather Vest", "Basic defense", 5]
        ],
        "Uncommon": [
            ["Chainmail", "Reduce damage", 6]
        ],
        "Rare": [
            ["Plate Armor", "Reduce damage", 8]
        ],
        "Epic": [
            ["Mythril Armor", "Regen", 10]
        ]
    }
}

DEFAULT_ITEMS = {
    "consumables": [
        ["Health Potion", "Restore 20 HP", 20],
        ["Big Health Potion", "Restore 50 HP", 50]
    ]
}

DEFAULT_STATS = {
    "kills": 0,
    "play_time": 0,
    "max_level": 1,
    "total_xp": 0,
    "total_gold": 0,
    "total_gold_spent": 0,
    "total_gold_spent_on_skills": 0
}

DEFAULT_PLAYER_STATS = {
    "health": 100,
    "level": 1,
    "xp": 0,
    "xp_to_level": 50,
    "weapon": ["Fists", "Basic attack", 4, 6],
    "armor": ["Rags", "No effect", 0],
    "inventory": [],
    "pity_counter": 0,
    "epic_count": 0,
    "gold": 0
}