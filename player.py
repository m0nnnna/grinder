import os
import json
import time
from colorama import Fore, Style

from utils import load_json, save_json, DEFAULT_PLAYER_STATS

SAVE_FILE = 'player_save.json'

def initialize_player(new_game=False):
    session_start = time.time()
    if not new_game and os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            player = json.load(f)
        print(f"{Fore.GREEN}Loaded saved game!{Style.RESET_ALL}")
    else:
        player = load_json('player_stats.json', DEFAULT_PLAYER_STATS)
        player['skills'] = []
        player['cooldowns'] = {}
    return player, session_start

def equip_item(player, gear, config):
    if not player['inventory']:
        print(f"{Fore.RED}Inventory empty!{Style.RESET_ALL}")
        return
    print("\nInventory:")
    for i, (rarity, item_type, item) in enumerate(player['inventory']):
        print(f"{i+1}. {rarity} {item_type}: {item[0]} ({item[1]})")
    choice = input(f"{Fore.CYAN}Enter number to equip/use (or 'cancel'): {Style.RESET_ALL}").strip()
    if choice == 'cancel':
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(player['inventory']):
            rarity, item_type, item = player['inventory'].pop(idx)
            if item_type == 'consumable':
                use_consumable(player, item)
            else:
                # Determine slot and current item
                slot = 'weapon' if item_type == 'weapon' else 'armor'
                current_item = player[slot]
                # Find rarity of current item
                current_rarity = 'Common'  # Default for Fists/Rags
                gear_key = 'weapons' if item_type == 'weapon' else 'armor'
                for r in config['rarities']:
                    if current_item in gear[gear_key].get(r, []):
                        current_rarity = r
                        break
                # Swap current item to inventory if not default
                if current_item[0] not in ['Fists', 'Rags']:
                    player['inventory'].append((current_rarity, item_type, current_item))
                    print(f"{Fore.CYAN}Returned {current_item[0]} to inventory.{Style.RESET_ALL}")
                # Equip new item
                player[slot] = item
                print(f"{Fore.GREEN}Equipped {item[0]}!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")

def use_consumable(player, item):
    effect = item[1]
    value = item[2]
    if 'Restore' in effect:
        restore = value if value < 100 else player['health']
        player['health'] += restore
        print(f"{Fore.GREEN}Used {item[0]}: Restored {restore} HP!{Style.RESET_ALL}")
    # Add more effects as needed

def use_skill(skill_idx, enemy_health, player, skills, combat_log):
    idx = int(skill_idx) - 1
    if idx < 0 or idx >= len(player['skills']):
        combat_log.append(f"{Fore.RED}Invalid skill!{Style.RESET_ALL}")
        return enemy_health
    skill = player['skills'][idx]
    skill_name = skill[0]
    if player['cooldowns'].get(skill_name, 0) > 0:
        combat_log.append(f"{Fore.RED}{skill_name} is on cooldown ({player['cooldowns'][skill_name]} turns)!{Style.RESET_ALL}")
        return enemy_health
    effect, value, cooldown = skill[1], skill[2], skill[3]
    if effect == 'Damage':
        enemy_health -= value
        combat_log.append(f"{Fore.GREEN}Used {skill_name}: Dealt {value} damage!{Style.RESET_ALL}")
    elif effect == 'Heal':
        player['health'] += value
        combat_log.append(f"{Fore.GREEN}Used {skill_name}: Healed {value} HP!{Style.RESET_ALL}")
    elif effect == 'DamageBoost':
        player['weapon'][2] += value
        player['weapon'][3] += value
        combat_log.append(f"{Fore.GREEN}Used {skill_name}: Attack boosted by {value}!{Style.RESET_ALL}")
    elif effect == 'Shield':
        player['health'] += value
        combat_log.append(f"{Fore.GREEN}Used {skill_name}: Gained {value} temporary HP!{Style.RESET_ALL}")
    player['cooldowns'][skill_name] = cooldown
    return enemy_health

def buy_item(player, shop_inventory, config, stats):
    if not shop_inventory:
        print(f"{Fore.RED}Shop is empty!{Style.RESET_ALL}")
        return
    print("\nShop Inventory:")
    prices = config['shop_prices']
    for i, (rarity, item_type, item) in enumerate(shop_inventory):
        price = prices[rarity]
        print(f"{i+1}. {Fore.CYAN}{rarity} {item_type}: {item[0]} ({item[1]}) - {price} Gold{Style.RESET_ALL}")
    choice = input(f"{Fore.CYAN}Enter number to buy (or 'cancel'): {Style.RESET_ALL}").strip()
    if choice == 'cancel':
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(shop_inventory):
            rarity, item_type, item = shop_inventory[idx]
            price = prices[rarity]
            if player['gold'] >= price:
                player['gold'] -= price
                stats['total_gold_spent'] += price
                player['inventory'].append((rarity, item_type, item))
                print(f"{Fore.GREEN}Bought {item[0]} for {price} Gold!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Not enough gold! Need {price}, have {player['gold']}.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")

def learn_skill(player, trainer_skills, config, stats):
    if not trainer_skills:
        print(f"{Fore.RED}No skills available!{Style.RESET_ALL}")
        return
    print("\nSkill Trainer:")
    for i, skill in enumerate(trainer_skills, 1):
        name, effect, value, cooldown, level_required, gold_cost = skill
        status = f"{Fore.CYAN}Available{Style.RESET_ALL}" if player['level'] >= level_required else f"{Fore.RED}Locked (Level {level_required} required){Style.RESET_ALL}"
        print(f"{i}. {name} ({effect}, {value}, {cooldown} turns, Level {level_required}) - {gold_cost} Gold [{status}]")
    choice = input(f"{Fore.CYAN}Enter number to learn (or 'cancel'): {Style.RESET_ALL}").strip()
    if choice == 'cancel':
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(trainer_skills):
            skill = trainer_skills[idx]
            name, effect, value, cooldown, level_required, gold_cost = skill
            if player['level'] < level_required:
                print(f"{Fore.RED}You need to be level {level_required} to learn {name}!{Style.RESET_ALL}")
                return
            if player['gold'] < gold_cost:
                print(f"{Fore.RED}Not enough gold! Need {gold_cost}, have {player['gold']}.{Style.RESET_ALL}")
                return
            if len(player['skills']) >= 4:
                print(f"{Fore.YELLOW}You already have 4 skills! Choose a skill to replace:{Style.RESET_ALL}")
                for j, s in enumerate(player['skills'], 1):
                    print(f"{j}. {s[0]} ({s[1]}, {s[2]}, {s[3]} turns)")
                replace_choice = input(f"{Fore.CYAN}Enter number to replace (or 'cancel'): {Style.RESET_ALL}").strip()
                if replace_choice == 'cancel':
                    return
                try:
                    replace_idx = int(replace_choice) - 1
                    if 0 <= replace_idx < len(player['skills']):
                        old_skill = player['skills'][replace_idx]
                        player['skills'][replace_idx] = skill
                        player['cooldowns'].pop(old_skill[0], None)
                        player['cooldowns'][name] = 0
                        player['gold'] -= gold_cost
                        stats['total_gold_spent_on_skills'] += gold_cost
                        print(f"{Fore.GREEN}Replaced {old_skill[0]} with {name} for {gold_cost} Gold!{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
            else:
                player['skills'].append(skill)
                player['cooldowns'][name] = 0
                player['gold'] -= gold_cost
                stats['total_gold_spent_on_skills'] += gold_cost
                print(f"{Fore.GREEN}Learned {name} for {gold_cost} Gold!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")

def check_level_up(player, stats):
    if player['xp'] >= player['xp_to_level']:
        player['level'] += 1
        player['xp'] = 0
        player['xp_to_level'] += 50
        player['health'] = 100 + player['level'] * 20
        stats['max_level'] = max(stats['max_level'], player['level'])
        print(f"{Fore.GREEN}Leveled up to {player['level']}! Health restored.{Style.RESET_ALL}")