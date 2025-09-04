import os
import json
import time
import random
from colorama import init, Fore, Style

from utils import load_json, save_json, DEFAULT_CONFIG, DEFAULT_ENEMIES, DEFAULT_GEAR, DEFAULT_ITEMS, DEFAULT_STATS, DEFAULT_PLAYER_STATS
from player import initialize_player, equip_item, check_level_up, use_consumable, use_skill, buy_item, learn_skill
from combat import display_scene, attack_enemy, take_damage, post_fight_menu
from shop import generate_shop_inventory
from trainer import generate_trainer_skills

# Initialize colorama for cross-platform colors
init()

# Load data
config = load_json('config.json', DEFAULT_CONFIG)
enemy_stats = load_json('enemy_stats.json', DEFAULT_ENEMIES)
gear = load_json('gear.json', DEFAULT_GEAR)
items = load_json('items.json', DEFAULT_ITEMS)
stats = load_json('stats.json', DEFAULT_STATS)
skills = load_json('skills.json', {'skills': []})
art = load_json('art.json', {
    'player': """
  ^ ^
   O
  /|\\
  / \\~
""",
    'enemies': {
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
})

# Start menu
print(f"{Fore.CYAN}Welcome to Loot Grind!{Style.RESET_ALL}")
while True:
    print(f"\n1) New Game\n2) Load Game")
    choice = input("Choose: ").strip()
    if choice in ['1', '2']:
        break
    print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")

# Initialize player
player, session_start = initialize_player(choice == '1')
stats['play_time'] += time.time() - session_start  # Will update on save

# Main game loop
print(f"{Fore.CYAN}Press 1-4 for skills, Enter to attack, q to quit!{Style.RESET_ALL}")
current_enemy_health = None
combat_log = []
while player['health'] > 0:
    # Select enemy based on player level
    enemy_data = enemy_stats.get(str(min(player['level'], 3)), enemy_stats['1'])
    enemy_name, max_enemy_health, enemy_dmg, xp = enemy_data
    # Reset enemy health when starting a new enemy
    if current_enemy_health is None or current_enemy_health <= 0:
        current_enemy_health = max_enemy_health
    # Display scene
    display_scene(enemy_name, current_enemy_health, player, stats, combat_log, art)
    action = input(f"\n{Fore.CYAN}Press 1-4 for skills, Enter to attack, q to quit: {Style.RESET_ALL}").strip().lower()
    if action == '':
        current_enemy_health = attack_enemy(enemy_name, current_enemy_health, player['weapon'][2:4], player, combat_log)
        if current_enemy_health <= 0:
            stats['kills'] += 1
            gold_earned = random.randint(5, 20) * player['level']
            player['gold'] += gold_earned
            stats['total_gold'] += gold_earned
            shop_inventory = generate_shop_inventory(config, gear, items)
            trainer_skills = generate_trainer_skills(skills)
            post_fight_menu(enemy_name, xp, gold_earned, player, stats, config, gear, items, skills, shop_inventory, trainer_skills)
            combat_log.clear()
            if player['epic_count'] >= 5:
                break
            continue
        take_damage(enemy_dmg, player, combat_log)
    elif action in ['1', '2', '3', '4']:
        current_enemy_health = use_skill(action, current_enemy_health, player, skills, combat_log)
        if current_enemy_health <= 0:
            stats['kills'] += 1
            gold_earned = random.randint(5, 20) * player['level']
            player['gold'] += gold_earned
            stats['total_gold'] += gold_earned
            shop_inventory = generate_shop_inventory(config, gear, items)
            trainer_skills = generate_trainer_skills(skills)
            post_fight_menu(enemy_name, xp, gold_earned, player, stats, config, gear, items, skills, shop_inventory, trainer_skills)
            combat_log.clear()
            if player['epic_count'] >= 5:
                break
            continue
        take_damage(enemy_dmg, player, combat_log)
    elif action == 'q':
        print(f"{Fore.RED}Game over.{Style.RESET_ALL}")
        save_json('player_save.json', player)
        stats['play_time'] += time.time() - session_start
        save_json('stats.json', stats)
        break
    else:
        combat_log.append(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
if player['health'] <= 0:
    print(f"\n{Fore.RED}You died! Game over.{Style.RESET_ALL}")
    save_json('player_save.json', player)
    stats['play_time'] += time.time() - session_start
    save_json('stats.json', stats)