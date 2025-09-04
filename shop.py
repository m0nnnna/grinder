import random

def generate_shop_inventory(config, gear, items):
    shop_inventory = []
    rarities = config['rarities']
    # Add 2 gear items
    for _ in range(2):
        rarity = random.choice(rarities)
        gear_type = random.choice(['weapon', 'armor'])
        # Use 'armor' instead of 'armors' for gear.json key
        key = 'weapons' if gear_type == 'weapon' else 'armor'
        item = random.choice(gear[key][rarity])
        shop_inventory.append((rarity, gear_type, item))
    # Add 2 consumables
    for _ in range(2):
        rarity = random.choice(rarities)
        item = random.choice(items['consumables'][rarity])
        shop_inventory.append((rarity, 'consumable', item))
    return shop_inventory