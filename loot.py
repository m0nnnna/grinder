import random

def drop_loot(player, config, gear):
    adjusted_weights = config['weights'].copy()
    if player['pity_counter'] >= 5:
        adjusted_weights[2:] = [w * 1.5 for w in adjusted_weights[2:]]
    rarity = random.choices(config['rarities'], weights=adjusted_weights)[0]
    if rarity == 'Common':
        player['pity_counter'] += 1
    else:
        player['pity_counter'] = 0
    if random.random() < 0.5:  # 50% chance for gear drop
        gear_type = random.choice(['weapons', 'armor'])
        item = random.choice(gear[gear_type][rarity])
        if rarity == 'Epic':
            player['epic_count'] += 1
        return item
    return None

def drop_consumable(player, config, items):
    if random.random() < 0.3:  # 30% chance for consumable drop
        rarity = random.choices(config['rarities'], weights=config['weights'])[0]
        item = random.choice(items['consumables'][rarity])
        return item
    return None