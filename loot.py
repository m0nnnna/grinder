import random
from stats_manager import update_score

def drop_loot(player, config, gear):
    """Determine if loot is dropped and what type."""
    # Pity system: guarantee Epic after 10 non-Epic drops
    if player['pity_counter'] >= 10:
        player['pity_counter'] = 0
        player['epic_count'] += 1
        return random.choice(gear['weapons']['Epic'] + gear['armor']['Epic'])

    # Random drop chance (30%)
    if random.random() < 0.3:
        # Choose rarity based on weights
        rarity = random.choices(config['rarities'], config['weights'], k=1)[0]
        # Choose item type (weapon or armor)
        item_type = random.choice(['weapons', 'armor'])
        # Choose item from the selected rarity
        dropped_item = random.choice(gear[item_type][rarity])
        player['pity_counter'] += 1
        if rarity == 'Epic':
            player['pity_counter'] = 0
            player['epic_count'] += 1
        return dropped_item
    return None

def drop_consumable(player, config, items):
    """Determine if a consumable is dropped."""
    if random.random() < 0.2:  # 20% chance to drop a consumable
        rarity = random.choices(config['rarities'], config['weights'], k=1)[0]
        if items['consumables'].get(rarity):
            return random.choice(items['consumables'][rarity])
    return None