import random
import json
import os
import time

# ASCII art for visuals
PLAYER_ART = """
  O
 /|\\
 / \\
"""
ENEMY_ART = {
    'Goblin': """
   @@
  >\\/7
  -  -
    """,
    'Troll': """
   @@
  >==<
  / 0 \\
    """,
    'Dragon': """
   ^^
  >==<
  /~~~\\
    """
}

# Load JSON files with error handling
def load_json(file_name, default_data):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading {file_name}. Using default data.")
    else:
        print(f"{file_name} not found. Using default data.")
    return default_data

# Default data if JSON files are missing
DEFAULT_CONFIG = {
    'rarities': ['Common', 'Uncommon', 'Rare', 'Epic'],
    'weights': [60, 30, 8, 2],
    'player': {
        'health': 100,
        'level': 1,
        'xp': 0,
        'xp_to_level': 50,
        'weapon': ['Fists', 'Basic attack', 3],
        'armor': ['Rags', 'No effect', 0],
        'inventory': [],
        'pity_counter': 0,
        'epic_count': 0
    }
}
DEFAULT_ENEMIES = {
    '1': ['Goblin', 20, 3, 10],
    '2': ['Troll', 40, 5, 20],
    '3': ['Dragon', 60, 8, 30]
}
DEFAULT_ITEMS = {
    'weapons': {
        'Common': [['Dagger', 'Basic attack', 5], ['Club', 'Basic attack', 6]],
        'Uncommon': [['Shortbow', 'Double attack (10% chance)', 8]],
        'Rare': [['Flaming Sword', 'Burn (extra 5 damage)', 10]],
        'Epic': [['Thunder Axe', 'Crit (20% chance x2 damage)', 15]]
    },
    'armor': {
        'Common': [['Leather Vest', 'Basic defense', 5], ['Cloth Robe', 'Basic defense', 4]],
        'Uncommon': [['Chainmail', 'Reduce damage by 2', 7]],
        'Rare': [['Plate Armor', 'Regen 5 health per kill', 10]],
        'Epic': [['Mythril Cloak', '50% chance to dodge', 12]]
    }
}

# Load data
config = load_json('config.json', DEFAULT_CONFIG)
enemies = load_json('enemies.json', DEFAULT_ENEMIES)
items = load_json('items.json', DEFAULT_ITEMS)

# Initialize player - Load from save if exists
SAVE_FILE = 'player_save.json'
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, 'r') as f:
        player = json.load(f)
    print("Loaded saved game!")
else:
    player = config['player'].copy()
    player['inventory'] = []  # Ensure inventory is fresh
    player['pity_counter'] = 0
    player['epic_count'] = 0

def save_game():
    with open(SAVE_FILE, 'w') as f:
        json.dump(player, f)
    print("Game saved!")

def display_scene(enemy, enemy_health):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
    print(PLAYER_ART + f" (You: {player['health']} HP)")
    print(ENEMY_ART.get(enemy, ENEMY_ART['Goblin']) + f" ({enemy}: {enemy_health} HP)")
    print(f"Level: {player['level']} | XP: {player['xp']}/{player['xp_to_level']}")
    print(f"Weapon: {player['weapon'][0]} | Armor: {player['armor'][0]}")

def attack_enemy(enemy, enemy_health, damage):
    weapon_effect = player['weapon'][1]
    total_damage = damage
    if weapon_effect == 'Double attack (10% chance)' and random.random() < 0.1:
        total_damage *= 2
        print("Double attack triggered!")
    elif weapon_effect == 'Burn (extra 5 damage)':
        total_damage += 5
        print("Burn deals extra damage!")
    elif weapon_effect == 'Crit (20% chance x2 damage)':
        if random.random() < 0.2:
            total_damage *= 2
            print("Critical hit!")
    enemy_health -= total_damage
    print(f"You deal {total_damage} damage!")
    return enemy_health

def take_damage(damage):
    armor_effect = player['armor'][1]
    if armor_effect == 'Reduce damage by 2':
        damage = max(0, damage - 2)
    elif armor_effect == '50% chance to dodge' and random.random() < 0.5:
        damage = 0
        print("Dodged the attack!")
    player['health'] -= damage
    print(f"Enemy deals {damage} damage!")

def drop_loot():
    adjusted_weights = config['weights'].copy()
    if player['pity_counter'] >= 5:
        adjusted_weights[2:] = [w * 1.5 for w in adjusted_weights[2:]]
    rarity = random.choices(config['rarities'], weights=adjusted_weights)[0]
    if rarity == 'Common':
        player['pity_counter'] += 1
    else:
        player['pity_counter'] = 0
    item_type = random.choice(['weapons', 'armor'])
    item = random.choice(items[item_type][rarity])
    print(f"Dropped {rarity} {item_type[:-1]}: {item[0]} ({item[1]})")
    player['inventory'].append((rarity, item))
    if rarity == 'Epic':
        player['epic_count'] += 1

def equip_item():
    if not player['inventory']:
        print("Inventory empty!")
        return
    print("\nInventory:")
    for i, (rarity, item) in enumerate(player['inventory']):
        print(f"{i+1}. {rarity} {item[0]} ({item[1]})")
    choice = input("Enter number to equip (or 'cancel'): ").strip()
    if choice == 'cancel':
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(player['inventory']):
            rarity, item = player['inventory'].pop(idx)
            if any(item in items['weapons'][r] for r in config['rarities']):
                player['weapon'] = item
            else:
                player['armor'] = item
            print(f"Equipped {item[0]}!")
        else:
            print("Invalid choice.")
    except ValueError:
        print("Invalid input.")

def check_level_up():
    if player['xp'] >= player['xp_to_level']:
        player['level'] += 1
        player['xp'] = 0
        player['xp_to_level'] += 50
        player['health'] = 100 + player['level'] * 20
        print(f"Leveled up to {player['level']}! Health restored.")

def post_fight_menu(enemy_name, xp):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{enemy_name} defeated! +{xp} XP")
    if player['armor'][1] == 'Regen 5 health per kill':
        player['health'] += 5
        print("Regen +5 health!")
    check_level_up()
    if random.random() < 0.7:
        drop_loot()
    time.sleep(1)
    while True:
        print("\nPost-Fight Menu:")
        print("1) Equip items")
        print("2) Save game")
        print("3) Continue to next fight")
        if player['epic_count'] >= 5:
            print("\nYou collected 5 Epic items! You win!")
            break
        choice = input("Choose: ").strip()
        if choice == '1':
            equip_item()
        elif choice == '2':
            save_game()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

# Main game loop
print("Welcome to Loot Grind! Press Enter to attack, collect loot, and survive!")
current_enemy_health = None
while player['health'] > 0:
    # Select enemy based on player level
    enemy_data = enemies.get(str(min(player['level'], 3)), enemies['1'])
    enemy_name, max_enemy_health, enemy_dmg, xp = enemy_data
    # Reset enemy health when starting a new enemy
    if current_enemy_health is None or current_enemy_health <= 0:
        current_enemy_health = max_enemy_health
    # Display scene with current enemy health
    display_scene(enemy_name, current_enemy_health)
    action = input("\nPress Enter to attack, 'q' to quit: ").strip().lower()
    if action == '':
        current_enemy_health = attack_enemy(enemy_name, current_enemy_health, player['weapon'][2])
        time.sleep(1)  # Pause after attack
        if current_enemy_health <= 0:
            post_fight_menu(enemy_name, xp)
            if player['epic_count'] >= 5:
                break
            continue
        take_damage(enemy_dmg)
        time.sleep(1)  # Pause after enemy attack
    elif action == 'q':
        print("Game over.")
        break
    else:
        print("Invalid input.")
        time.sleep(1)
if player['health'] <= 0:
    print("\nYou died! Game over.")