import os
import random
import time
from colorama import Fore, Style

from player import equip_item, check_level_up, use_consumable, buy_item, learn_skill
from loot import drop_loot, drop_consumable
from utils import save_json

def display_scene(enemy, enemy_health, player, stats, combat_log, art, enemy_mp, enemy_max_mp, enemy_cooldowns, current_zone_name):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
    print(f"{Fore.CYAN}{art['player']}{Style.RESET_ALL} (You: {player['health']}/{player['max_health']} HP, {player['mp']}/{player['max_mp']} MP)")
    print("-------------")  # Divider between player and enemy
    stun_status = " (Stunned)" if player['stun_duration'] > 0 else ""
    print(f"{art['enemies'].get(enemy, art['enemies']['Goblin'])} ({enemy}: {enemy_health} HP{stun_status}, {enemy_mp}/{enemy_max_mp} MP)")
    print(f"Current Zone: {current_zone_name}")
    print(f"Level: {player['level']} | XP: {player['xp']}/{player['xp_to_level']} | Gold: {Fore.YELLOW}{player['gold']}{Style.RESET_ALL}")
    print(f"Weapon: {player['weapon'][0]} ({player['weapon'][1]}) | Armor: {player['armor'][0]} ({player['armor'][1]})")
    print("\nCore Stats:")
    print(f"Attack: {player['weapon'][2]}-{player['weapon'][3]} | Defense: {player['armor'][2]}")
    print(f"Pity Counter: {player['pity_counter']} | Epic Count: {player['epic_count']}")
    print("\nSkills:")
    for i, skill in enumerate(player['skills'], 1):
        cd = player['cooldowns'].get(skill[0], 0)
        mp_cost = skill[6]
        status = '[Ready]' if cd == 0 else f'[Cooldown: {cd} turns]'
        print(f"{i}. {skill[0]} ({skill[1]}, {skill[2]}, {skill[3]} turns, {mp_cost} MP) {status}")
    print("\nGame Stats:")
    print(f"Score: {stats['score']}")
    print(f"Play Time: {int(stats['play_time'] // 3600)}h {int((stats['play_time'] % 3600) // 60)}m {int(stats['play_time'] % 60)}s")
    print(f"Max Level: {stats['max_level']} | Total XP: {stats['total_xp']} | Total Gold: {Fore.YELLOW}{stats['total_gold']}{Style.RESET_ALL}")
    print("\nCombat Log:")
    for msg in combat_log[-5:]:  # Show last 5 messages
        print(msg)
    # Reduce cooldowns and stun duration each turn
    for skill in player['cooldowns']:
        player['cooldowns'][skill] = max(0, player['cooldowns'][skill] - 1)
    player['stun_duration'] = max(0, player['stun_duration'] - 1)
    for skill_id in enemy_cooldowns:
        enemy_cooldowns[skill_id] = max(0, enemy_cooldowns[skill_id] - 1)

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
    # Regenerate MP
    mp_regen = min(5, player['max_mp'] - player['mp'])
    player['mp'] += mp_regen
    if mp_regen > 0:
        combat_log.append(f"{Fore.CYAN}Regenerated {mp_regen} MP. MP: {player['mp']}/{player['max_mp']}{Style.RESET_ALL}")
    return enemy_health

def take_damage(damage_range, player, combat_log, enemy_health, max_enemy_health, enemy_mp, enemy_max_mp, enemy_skills, monster_skills, enemy_cooldowns):
    # Skip enemy attack if stunned
    if player['stun_duration'] > 0:
        combat_log.append(f"{Fore.GREEN}Enemy is stunned and cannot attack!{Style.RESET_ALL}")
        return
    # Decide if enemy uses a skill or standard attack
    if random.random() < 0.5 and enemy_skills:  # 50% chance to attempt skill use
        # Filter usable skills (off cooldown, enough MP, meets condition)
        usable_skills = []
        for skill_id in enemy_skills:
            cd = enemy_cooldowns.get(skill_id, 0)
            if cd > 0:
                continue
            skill = monster_skills['skills'].get(str(skill_id))
            if not skill:
                continue
            name, effect, value, cooldown, mp_cost, weight, condition = skill
            if enemy_mp < mp_cost:
                continue
            if condition == "low_hp" and enemy_health >= 0.5 * max_enemy_health:
                continue
            usable_skills.extend([skill_id] * weight)  # Repeat based on weight
        if usable_skills:
            chosen_skill_id = random.choice(usable_skills)
            skill = monster_skills['skills'][str(chosen_skill_id)]
            name, effect, value, cooldown, mp_cost, _, _ = skill
            enemy_mp -= mp_cost
            enemy_cooldowns[chosen_skill_id] = cooldown
            if effect == 'Damage':
                total_damage = value
                player['health'] = max(0, player['health'] - total_damage)
                combat_log.append(f"{Fore.RED}Enemy uses {name}: Deals {total_damage} damage!{Style.RESET_ALL}")
            elif effect == 'Heal':
                restore = min(value, max_enemy_health - enemy_health)
                enemy_health += restore
                combat_log.append(f"{Fore.RED}Enemy uses {name}: Heals {restore} HP!{Style.RESET_ALL}")
            elif effect == 'Stun':
                player['stun_duration'] = value
                combat_log.append(f"{Fore.RED}Enemy uses {name}: You are stunned for {value} turn(s)!{Style.RESET_ALL}")
            combat_log.append(f"{Fore.RED}Enemy used {mp_cost} MP. MP: {enemy_mp}/{enemy_max_mp}{Style.RESET_ALL}")
            return
    # Standard attack if no skill used
    base_damage = random.randint(damage_range[0], damage_range[1])
    total_damage = base_damage
    if random.random() < 0.05:
        combat_log.append(f"{Fore.YELLOW}Enemy missed!{Style.RESET_ALL}")
        return
    if random.random() < 0.10:
        total_damage *= 2
        combat_log.append(f"{Fore.RED}Enemy critical hit!{Style.RESET_ALL}")
    armor_effect = player['armor'][1]
    if 'Reduce damage' in armor_effect:
        total_damage = max(0, total_damage - 2)
    elif 'dodge' in armor_effect and random.random() < 0.5:
        total_damage = 0
        combat_log.append(f"{Fore.GREEN}Dodged the attack!{Style.RESET_ALL}")
    player['health'] = max(0, player['health'] - total_damage)
    combat_log.append(f"{Fore.RED}Enemy deals {total_damage} damage!{Style.RESET_ALL}")

def post_fight_menu(enemy_name, xp, gold_earned, player, stats, config, gear, items, skills, shop_inventory, trainer_skills, zones):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Fore.MAGENTA}{enemy_name} defeated!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}+{xp} XP | +{gold_earned} Gold{Style.RESET_ALL}")
    player['xp'] += xp
    stats['total_xp'] += xp
    from stats_manager import update_score
    update_score(stats, 'kill')  # Add 1 point for killing an enemy
    if 'Regen' in player['armor'][1]:
        player['health'] = min(player['health'] + 5, player['max_health'])
        print(f"{Fore.GREEN}Regen +5 health!{Style.RESET_ALL}")
    check_level_up(player, stats)
    # Fully restore player HP and MP after each fight
    player['health'] = player.get('max_health', player['health'])
    player['mp'] = player.get('max_mp', player.get('mp', 0))
    player['stun_duration'] = 0
    print(f"{Fore.GREEN}HP and MP fully restored!{Style.RESET_ALL}")
    # Drop loot
    dropped_gear = drop_loot(player, config, gear)
    if dropped_gear:
        item_type = 'weapon' if dropped_gear in [item for r in gear['weapons'].values() for item in r] else 'armor'
        rarity = next(r for r, items in gear[item_type + 's'].items() if dropped_gear in items)
        print(f"{Fore.CYAN}Dropped {rarity} {item_type}: {dropped_gear[0]} ({dropped_gear[1]}){Style.RESET_ALL}")
        player['inventory'].append((rarity, item_type, dropped_gear))
        update_score(stats, 'item_drop', rarity)  # Add points for item drop
    dropped_item = drop_consumable(player, config, items)
    if dropped_item:
        print(f"{Fore.CYAN}Dropped item: {dropped_item[0]} ({dropped_item[1]}){Style.RESET_ALL}")
        player['inventory'].append(('Common', 'consumable', dropped_item))
        update_score(stats, 'item_drop', 'Common')  # Add 1 point for consumable
    input(f"{Fore.LIGHTWHITE_EX}Press Enter to continue...{Style.RESET_ALL}")
    while True:
        print("\nPost-Fight Menu:")
        print("1) Equip/Use items")
        print("2) Save game")
        print("3) Visit shop")
        print("4) Visit skill trainer")
        print("5) Continue to next fight")
        print("6) Travel to Zone")
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
        elif choice == '6':
            print("\nAvailable Zones:")
            for zone_id, zone in zones.items():
                print(f"{zone_id}. {zone['name']} - {zone['description']}")
            zone_choice = input("Enter zone number (or 'cancel'): ").strip()
            if zone_choice == 'cancel':
                continue
            if zone_choice in zones:
                player['current_zone'] = zone_choice
                print(f"{Fore.GREEN}Traveled to {zones[zone_choice]['name']}!{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Invalid zone.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")