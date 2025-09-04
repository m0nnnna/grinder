import os
import random
import time
from colorama import Fore, Style

from player import equip_item, check_level_up, use_consumable, buy_item, learn_skill
from loot import drop_loot, drop_consumable
from utils import save_json

def display_scene(enemy, enemy_health, player, stats, combat_log, art):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
    print(f"{Fore.CYAN}{art['player']}{Style.RESET_ALL} (You: {player['health']} HP)")
    print("-------------")  # Divider between player and enemy
    print(f"{art['enemies'].get(enemy, art['enemies']['Goblin'])} ({enemy}: {enemy_health} HP)")
    print(f"Level: {player['level']} | XP: {player['xp']}/{player['xp_to_level']} | Gold: {Fore.YELLOW}{player['gold']}{Style.RESET_ALL}")
    print(f"Weapon: {player['weapon'][0]} ({player['weapon'][1]}) | Armor: {player['armor'][0]} ({player['armor'][1]})")
    print("\nCore Stats:")
    print(f"Attack: {player['weapon'][2]}-{player['weapon'][3]} | Defense: {player['armor'][2]}")
    print(f"Pity Counter: {player['pity_counter']} | Epic Count: {player['epic_count']}")
    print("\nSkills:")
    for i, skill in enumerate(player['skills'], 1):
        cd = player['cooldowns'].get(skill[0], 0)
        print(f"{i}. {skill[0]} ({skill[1]}, {skill[2]}, {skill[3]} turns) {'[Ready]' if cd == 0 else f'[Cooldown: {cd}]'}")
    print("\nGame Stats:")
    print(f"Monsters Killed: {stats['kills']}")
    print(f"Play Time: {int(stats['play_time'] // 3600)}h {int((stats['play_time'] % 3600) // 60)}m {int(stats['play_time'] % 60)}s")
    print(f"Max Level: {stats['max_level']} | Total XP: {stats['total_xp']} | Total Gold: {Fore.YELLOW}{stats['total_gold']}{Style.RESET_ALL}")
    print("\nCombat Log:")
    for msg in combat_log[-5:]:  # Show last 5 messages
        print(msg)

def attack_enemy(enemy, enemy_health, damage_range, player, combat_log):
    weapon_effect = player['weapon'][1]
    # Calculate base damage within range
    base_damage = random.randint(damage_range[0], damage_range[1])
    total_damage = base_damage
    # Check for miss (5% chance)
    if random.random() < 0.05:
        combat_log.append(f"{Fore.RED}You missed!{Style.RESET_ALL}")
        return enemy_health
    # Check for crit (10% chance)
    if random.random() < 0.10:
        total_damage *= 2
        combat_log.append(f"{Fore.GREEN}Critical hit!{Style.RESET_ALL}")
    # Apply weapon effects
    if 'Double attack' in weapon_effect and random.random() < 0.1:
        total_damage *= 2
        combat_log.append(f"{Fore.GREEN}Double attack triggered!{Style.RESET_ALL}")
    elif 'Burn' in weapon_effect:
        total_damage += 5
        combat_log.append(f"{Fore.RED}Burn deals extra damage!{Style.RESET_ALL}")
    elif 'Crit' in weapon_effect and random.random() < 0.2:
        total_damage *= 2
        combat_log.append(f"{Fore.GREEN}Weapon critical hit!{Style.RESET_ALL}")
    enemy_health -= total_damage
    combat_log.append(f"{Fore.GREEN}You deal {total_damage} damage!{Style.RESET_ALL}")
    return enemy_health

def take_damage(damage_range, player, combat_log):
    # Calculate base damage within range
    base_damage = random.randint(damage_range[0], damage_range[1])
    total_damage = base_damage
    # Check for miss (5% chance)
    if random.random() < 0.05:
        combat_log.append(f"{Fore.YELLOW}Enemy missed!{Style.RESET_ALL}")
        return
    # Check for crit (10% chance)
    if random.random() < 0.10:
        total_damage *= 2
        combat_log.append(f"{Fore.RED}Enemy critical hit!{Style.RESET_ALL}")
    # Apply armor effects
    armor_effect = player['armor'][1]
    if 'Reduce damage' in armor_effect:
        total_damage = max(0, total_damage - 2)
    elif 'dodge' in armor_effect and random.random() < 0.5:
        total_damage = 0
        combat_log.append(f"{Fore.GREEN}Dodged the attack!{Style.RESET_ALL}")
    player['health'] -= total_damage
    combat_log.append(f"{Fore.RED}Enemy deals {total_damage} damage!{Style.RESET_ALL}")

def post_fight_menu(enemy_name, xp, gold_earned, player, stats, config, gear, items, skills, shop_inventory, trainer_skills):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.MAGENTA}{enemy_name} defeated!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}+{xp} XP | +{gold_earned} Gold{Style.RESET_ALL}")
    player['xp'] += xp
    stats['total_xp'] += xp
    if 'Regen' in player['armor'][1]:
        player['health'] += 5
        print(f"{Fore.GREEN}Regen +5 health!{Style.RESET_ALL}")
    check_level_up(player, stats)
    # Drop loot
    dropped_gear = drop_loot(player, config, gear)
    if dropped_gear:
        print(f"{Fore.CYAN}Dropped gear: {dropped_gear[0]} ({dropped_gear[1]}){Style.RESET_ALL}")
        player['inventory'].append(('Epic' if 'Epic' in dropped_gear[0] else 'Other', 'gear', dropped_gear))
    dropped_item = drop_consumable(player, config, items)
    if dropped_item:
        print(f"{Fore.CYAN}Dropped item: {dropped_item[0]} ({dropped_item[1]}){Style.RESET_ALL}")
        player['inventory'].append(('Common', 'consumable', dropped_item))
    # Update cooldowns
    for skill in player['cooldowns']:
        player['cooldowns'][skill] = max(0, player['cooldowns'][skill] - 1)
    input(f"{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    while True:
        print("\nPost-Fight Menu:")
        print("1) Equip/Use items")
        print("2) Save game")
        print("3) Visit shop")
        print("4) Visit skill trainer")
        print("5) Continue to next fight")
        if player['epic_count'] >= 5:
            print(f"\n{Fore.GREEN}You collected 5 Epic items! You win!{Style.RESET_ALL}")
            break
        choice = input("Choose: ").strip()
        if choice == '1':
            equip_item(player, gear, config)
        elif choice == '2':
            save_json('player_save.json', player)
            save_json('stats.json', stats)
            print(f"{Fore.GREEN}Game saved!{Style.RESET_ALL}")
        elif choice == '3':
            buy_item(player, shop_inventory, config, stats)
        elif choice == '4':
            learn_skill(player, trainer_skills, config, stats)
        elif choice == '5':
            break
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")