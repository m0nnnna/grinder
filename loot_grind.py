import random
import json
import os
import time

from loot import drop_loot, drop_consumable

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

# Load JSON files
config = load_json('config.json')
enemies = load_json('enemies.json')
gear = load_json('gear.json')

# Initialize player - Load from save if exists
SAVE_FILE = 'player_save.json'
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, 'r') as f:
        player = json.load(f)
    print("Loaded saved game!")
else:
    player = load_json('player_stats.json')
    player['inventory'] = []  # Ensure inventory is fresh
    player['pity_counter'] = 0
    player['epic_count'] = 0
    # Ensure mp and max_mp are initialized
    if 'mp' not in player:
        player['mp'] = player.get('max_mp', 50)
    if 'max_mp' not in player:
        player['max_mp'] = 50
    if 'max_health' not in player:
        player['max_health'] = player.get('health', 100)

def save_game():
    with open(SAVE_FILE, 'w') as f:
        json.dump(player, f)
    print("Game saved!")

def display_scene(enemy, enemy_health):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
    print(PLAYER_ART + f" (You: {player['health']}/{player['max_health']} HP, {player['mp']}/{player['max_mp']} MP)")
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
    # Regenerate MP
    mp_regen = min(5, player['max_mp'] - player['mp'])
    player['mp'] += mp_regen
    if mp_regen > 0:
        print(f"Regenerated {mp_regen} MP. MP: {player['mp']}/{player['max_mp']}")
    return enemy_health

def take_damage(damage):
    armor_effect = player['armor'][1]
    if armor_effect == 'Reduce damage by 2':
        damage = max(0, damage - 2)
    elif armor_effect == '50% chance to dodge' and random.random() < 0.5:
        damage = 0
        print("Dodged the attack!")
    player['health'] = max(0, player['health'] - damage)
    print(f"Enemy deals {damage} damage!")

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
            if any(item in gear['weapons'][r] for r in config['rarities']):
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
        player['max_health'] = 100 + player['level'] * 20
        player['health'] = player['max_health']
        player['max_mp'] = 50 + player['level'] * 10
        player['mp'] = player['max_mp']
        print(f"Leveled up to {player['level']}! Health and MP restored.")

def post_fight_menu(enemy_name, xp):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{enemy_name} defeated! +{xp} XP")
    if player['armor'][1] == 'Regen 5 health per kill':
        player['health'] = min(player['health'] + 5, player['max_health'])
        print("Regen +5 health!")
    check_level_up()
    dropped_gear = drop_loot(player, config, gear)
    if dropped_gear:
        item_type = 'weapon' if dropped_gear in [item for r in gear['weapons'].values() for item in r] else 'armor'
        rarity = next(r for r, items in gear[item_type + 's'].items() if dropped_gear in items)
        print(f"Dropped {rarity} {item_type}: {dropped_gear[0]} ({dropped_gear[1]})")
        player['inventory'].append((rarity, dropped_gear))
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