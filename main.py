import os
import json
import time
import random
from colorama import init, Fore, Style

from utils import load_json, save_json
from player import initialize_player, equip_item, check_level_up, use_consumable, use_skill, buy_item, learn_skill
from combat import display_scene, attack_enemy, take_damage, post_fight_menu
from shop import generate_shop_inventory
from trainer import generate_trainer_skills
from stats_manager import initialize_stats

# Initialize colorama for cross-platform colors
init()

# Load data
config = load_json('config.json')
enemies = load_json('enemies.json')
gear = load_json('gear.json')
items = load_json('items.json')
stats = initialize_stats()  # Use stats_manager to initialize
skills = load_json('skills.json')
monster_skills = load_json('monster_skills.json')
art = load_json('art.json')
zones = load_json('zones.json')

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
if choice == '1':
    save_json('player_save.json', player)  # Save immediately for new game to reset stats
stats['play_time'] += time.time() - session_start  # Will update on save

# Main game loop
print(f"{Fore.CYAN}Press 1-4 for skills, Enter to attack, q to quit!{Style.RESET_ALL}")
current_enemy_health = None
enemy_mp = None
enemy_max_mp = None
enemy_skills = None
enemy_cooldowns = {}
combat_log = []
while player['health'] > 0:
    # Select enemy from current zone
    current_zone = zones.get(player['current_zone'], zones['1'])  # Default to zone 1
    current_zone_name = current_zone['name']
    enemy_id = random.choice(current_zone['enemies'])
    enemy_data = enemies.get(str(enemy_id), enemies['1'])
    enemy_name, max_enemy_health, enemy_dmg, xp, enemy_max_mp, enemy_skills = enemy_data
    # Reset enemy state when starting a new enemy
    if current_enemy_health is None or current_enemy_health <= 0:
        current_enemy_health = max_enemy_health
        enemy_mp = enemy_max_mp
        enemy_cooldowns = {}
    # Display scene
    display_scene(enemy_name, current_enemy_health, player, stats, combat_log, art, enemy_mp, enemy_max_mp, enemy_cooldowns, current_zone_name)
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
            post_fight_menu(enemy_name, xp, gold_earned, player, stats, config, gear, items, skills, shop_inventory, trainer_skills, zones)
            combat_log.clear()
            if player['epic_count'] >= 5:
                break
            continue
        take_damage(enemy_dmg, player, combat_log, current_enemy_health, max_enemy_health, enemy_mp, enemy_max_mp, enemy_skills, monster_skills, enemy_cooldowns)
    elif action in ['1', '2', '3', '4']:
        current_enemy_health = use_skill(action, current_enemy_health, player, skills, combat_log)
        if current_enemy_health <= 0:
            stats['kills'] += 1
            gold_earned = random.randint(5, 20) * player['level']
            player['gold'] += gold_earned
            stats['total_gold'] += gold_earned
            shop_inventory = generate_shop_inventory(config, gear, items)
            trainer_skills = generate_trainer_skills(skills)
            post_fight_menu(enemy_name, xp, gold_earned, player, stats, config, gear, items, skills, shop_inventory, trainer_skills, zones)
            combat_log.clear()
            if player['epic_count'] >= 5:
                break
            continue
        take_damage(enemy_dmg, player, combat_log, current_enemy_health, max_enemy_health, enemy_mp, enemy_max_mp, enemy_skills, monster_skills, enemy_cooldowns)
    elif action == 'q':
        print(f"{Fore.RED}Game over.{Style.RESET_ALL}")
        save_json('player_save.json', player)
        stats['play_time'] += time.time() - session_start
        save_json('stats.json', stats)
        break
    else:
        combat_log.append(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
    # Regenerate MP and reduce stun duration if not casting a skill
    if action not in ['1', '2', '3', '4']:
        mp_regen = min(5, player['max_mp'] - player['mp'])
        player['mp'] += mp_regen
        if mp_regen > 0:
            combat_log.append(f"{Fore.CYAN}Regenerated {mp_regen} MP. MP: {player['mp']}/{player['max_mp']}{Style.RESET_ALL}")
if player['health'] <= 0:
    print(f"\n{Fore.RED}You died! Game over.{Style.RESET_ALL}")
    save_json('player_save.json', player)
    stats['play_time'] += time.time() - session_start
    save_json('stats.json', stats)