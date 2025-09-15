JSON Data Guide for Loot Grind
This guide details the required structure and entries for all JSON files used in the "Loot Grind" text-based RPG. These files define game data such as gear, enemies, player stats, skills, and more. By editing these JSON files, you can add new items, gear, enemies, skills, or other content without changing the Python code. Each file's structure is described below, including required fields and examples of how to add new entries.
General Guidelines

File Location: Place all JSON files in the same directory as the Python scripts (main.py, loot_grind.py, stats_manager.py, etc.).
JSON Format: Ensure files are valid JSON. Use proper syntax (e.g., double quotes, commas, no trailing commas).
Error Handling: The game will raise an error if a file is missing or contains invalid JSON, with a message indicating the issue.
Adding Data: You can add new entries (e.g., weapons, enemies, skills, zones) as long as they follow the required structure for each file.
Stats Reset: The stats.json file resets to its initial state if player_save.json is modified (based on file modification time).

JSON Files and Their Structures
1. gear.json
Defines weapons and armor available in the game, categorized by rarity.
Required Structure:
{
    "weapons": {
        "RarityName": [
            ["ItemName", "EffectDescription", MinDamage, MaxDamage],
            ...
        ],
        ...
    },
    "armor": {
        "RarityName": [
            ["ItemName", "EffectDescription", DefenseValue],
            ...
        ],
        ...
    }
}


weapons: Object with rarity keys (e.g., "Common", "Uncommon"). Each rarity contains a list of weapon arrays.
Each weapon array: [Name, Effect, MinDamage, MaxDamage]
Name: String (e.g., "Dagger").
Effect: String describing the effect (e.g., "Basic attack", "Crit (20% chance x2 damage)").
MinDamage, MaxDamage: Integers for the damage range.




armor: Object with rarity keys. Each rarity contains a list of armor arrays.
Each armor array: [Name, Effect, DefenseValue]
Name: String (e.g., "Leather Vest").
Effect: String (e.g., "Basic defense", "50% chance to dodge").
DefenseValue: Integer for defense strength.




RarityName: Must match rarities defined in config.json (e.g., "Common", "Uncommon", "Rare", "Epic").

Example:
{
    "weapons": {
        "Common": [
            ["Dagger", "Basic attack", 5, 7],
            ["Club", "Basic attack", 6, 8]
        ],
        "Uncommon": [
            ["Shortbow", "Double attack (10% chance)", 7, 9]
        ],
        "Rare": [
            ["Flaming Sword", "Burn (extra 5 damage)", 8, 10]
        ],
        "Epic": [
            ["Thunder Axe", "Crit (20% chance x2 damage)", 12, 15],
            ["Frost Spear", "Freeze (10% chance to stun)", 11, 14]
        ]
    },
    "armor": {
        "Common": [
            ["Leather Vest", "Basic defense", 5],
            ["Cloth Robe", "Basic defense", 4]
        ],
        "Uncommon": [
            ["Chainmail", "Reduce damage by 2", 7]
        ],
        "Rare": [
            ["Plate Armor", "Regen 5 health per kill", 10]
        ],
        "Epic": [
            ["Mythril Cloak", "50% chance to dodge", 12],
            ["Dragon Scale", "Reflect 10% damage", 15]
        ]
    }
}

Adding New Items:

Add a new array to the appropriate rarity under weapons or armor.
Example: To add a new Epic weapon, append ["Star Blade", "Triple attack (5% chance)", 13, 16] to weapons.Epic.
Ensure RarityName exists in config.json's rarities list.
Points are awarded for drops: Common (1), Uncommon (10), Rare (20), Epic (30).

2. config.json
Defines game configuration, including rarities, loot drop weights, and shop prices.
Required Structure:
{
    "rarities": ["Rarity1", "Rarity2", ...],
    "weights": [Weight1, Weight2, ...],
    "shop_prices": {
        "Rarity1": Price1,
        "Rarity2": Price2,
        ...
    }
}


rarities: Array of strings defining rarity levels (e.g., ["Common", "Uncommon", "Rare", "Epic"]).
weights: Array of integers for loot drop probabilities, corresponding to rarities (e.g., [60, 30, 8, 2]).
shop_prices: Object mapping each rarity to an integer price for shop purchases.

Example:
{
    "rarities": ["Common", "Uncommon", "Rare", "Epic", "Legendary"],
    "weights": [50, 30, 15, 4, 1],
    "shop_prices": {
        "Common": 10,
        "Uncommon": 25,
        "Rare": 50,
        "Epic": 100,
        "Legendary": 200
    }
}

Adding New Data:

Add a new rarity to rarities (e.g., "Legendary") and a corresponding weight to weights.
Add the rarity to shop_prices with a price.
Update gear.json and items.json to include items for the new rarity.
Example: Add "Legendary" to rarities, 1 to weights, and "Legendary": 200 to shop_prices.

3. enemies.json
Defines enemies and their stats, including skills and MP.
Required Structure:
{
    "EnemyID": ["EnemyName", MaxHealth, [MinDamage, MaxDamage], XPReward, MaxMP, [SkillID1, SkillID2, ...]],
    ...
}


EnemyID: String key (e.g., "1", "2") for referencing in zones.json.
Each enemy array: [Name, MaxHealth, DamageRange, XPReward, MaxMP, SkillsList]
Name: String (e.g., "Goblin").
MaxHealth: Integer for enemy health.
DamageRange: Array of two integers [MinDamage, MaxDamage] for standard attacks.
XPReward: Integer for XP gained on defeat.
MaxMP: Integer for maximum mana (e.g., 30). Current MP starts at MaxMP.
SkillsList: Array of integers referencing skill IDs from monster_skills.json (e.g., [1, 3]).



Example:
{
    "1": ["Goblin", 20, [1, 3], 10, 30, [1]],
    "2": ["Troll", 40, [4, 6], 20, 50, [2, 3]],
    "3": ["Dragon", 60, [7, 9], 30, 80, [4, 5]]
}

Adding New Enemies:

Add a new key-value pair with a unique ID (e.g., "4") and an enemy array.
Example: Add "4": ["Dark Knight", 80, [10, 14], 50, 60, [6, 7]].
Reference the ID in zones.json's enemies list.
Update art.json to include ASCII art for the new enemy.

4. items.json
Defines consumable items, including HP and MP restoration.
Required Structure:
{
    "consumables": {
        "RarityName": [
            ["ItemName", "EffectDescription", EffectValue],
            ...
        ],
        ...
    }
}


consumables: Object with rarity keys (matching config.json's rarities).
Each consumable array: [Name, Effect, Value]
Name: String (e.g., "Health Potion").
Effect: String (e.g., "Restore 20 HP", "Restore 10 MP").
Value: Integer for the effect magnitude (e.g., 20 for HP or MP restored).



Example:
{
    "consumables": {
        "Common": [
            ["Health Potion", "Restore 20 HP", 20],
            ["Mana Potion", "Restore 10 MP", 10]
        ],
        "Uncommon": [
            ["Big Health Potion", "Restore 50 HP", 50]
        ],
        "Rare": [
            ["Revive Scroll", "Revive with 50 HP", 50]
        ],
        "Epic": [
            ["Elixir", "Restore 100 HP", 100]
        ]
    }
}

Adding New Consumables:

Add a new array to the appropriate rarity under consumables.
Example: Add ["Big Mana Potion", "Restore 30 MP", 30] to consumables.Uncommon.
Ensure the rarity exists in config.json.
Use "Restore X HP" or "Restore X MP" for effects to ensure compatibility with player.py.
Consumables award 1 point (Common) when dropped.

5. stats.json
Tracks game statistics, including the leaderboard score.
Required Structure:
{
    "kills": Integer,
    "play_time": Integer,
    "max_level": Integer,
    "total_xp": Integer,
    "total_gold": Integer,
    "total_gold_spent": Integer,
    "total_gold_spent_on_skills": Integer,
    "score": Integer
}


kills: Number of enemies defeated (1 point each).
play_time: Total play time in seconds.
max_level: Highest player level reached (10 points per level-up).
total_xp: Total XP earned.
total_gold: Total gold earned.
total_gold_spent: Total gold spent in the shop.
total_gold_spent_on_skills: Total gold spent on skills.
score: Total points for the leaderboard (sums points from kills, item drops, level-ups, and skill purchases).

Scoring Rules:

Beating a monster: 1 point
Finding a Common item: 1 point
Finding an Uncommon item: 10 points
Finding a Rare item: 20 points
Finding an Epic item: 30 points
Leveling up: 10 points
Buying a skill: 10 points

Example:
{
    "kills": 0,
    "play_time": 0,
    "max_level": 1,
    "total_xp": 0,
    "total_gold": 0,
    "total_gold_spent": 0,
    "total_gold_spent_on_skills": 0,
    "score": 0
}

Adding New Stats:

The game manages these fields automatically via stats_manager.py.
To track additional stats, modify stats_manager.py and update the code (e.g., main.py, combat.py) to increment them.

6. player_stats.json
Defines the initial player state for new games.
Required Structure:
{
    "health": Integer,
    "max_health": Integer,
    "level": Integer,
    "xp": Integer,
    "xp_to_level": Integer,
    "weapon": ["Name", "Effect", MinDamage, MaxDamage],
    "armor": ["Name", "Effect", DefenseValue],
    "inventory": [],
    "pity_counter": Integer,
    "epic_count": Integer,
    "gold": Integer,
    "mp": Integer,
    "max_mp": Integer,
    "stun_duration": Integer,
    "current_zone": String
}


health: Current health.
max_health: Maximum health (scales with level: 100 + 20 * level).
level: Current level.
xp: Current XP.
xp_to_level: XP needed to level up.
weapon: Array [Name, Effect, MinDamage, MaxDamage] for the starting weapon.
armor: Array [Name, Effect, DefenseValue] for the starting armor.
inventory: Empty array for starting inventory.
pity_counter: Counter for guaranteed Epic drops.
epic_count: Number of Epic items collected.
gold: Current gold.
mp: Current mana.
max_mp: Maximum mana (scales with level: 50 + 10 * level).
stun_duration: Number of turns the current enemy is stunned (0 if not stunned).
current_zone: String ID of the current zone (e.g., "1").

Example:
{
    "health": 100,
    "max_health": 100,
    "level": 1,
    "xp": 0,
    "xp_to_level": 50,
    "weapon": ["Fists", "Basic attack", 4, 6],
    "armor": ["Rags", "No effect", 0],
    "inventory": [],
    "pity_counter": 0,
    "epic_count": 0,
    "gold": 0,
    "mp": 50,
    "max_mp": 50,
    "stun_duration": 0,
    "current_zone": "1"
}

Adding New Fields:

Add fields like "stamina": 100 if you modify the game to support new mechanics.
Example: Add "stamina": 100 and update player.py to handle stamina.

7. skills.json
Defines available skills for the skill trainer, including MP costs and cooldowns.
Required Structure:
{
    "skills": [
        ["SkillName", "Effect", Value, Cooldown, LevelRequired, GoldCost, MPCost],
        ...
    ]
}


skills: Array of skill arrays.
Each skill array: [Name, Effect, Value, Cooldown, LevelRequired, GoldCost, MPCost]
Name: String (e.g., "Fireball").
Effect: String (e.g., "Damage", "Heal", "DamageBoost", "Shield", "Stun").
Value: Integer for effect magnitude (e.g., damage, heal amount, or stun duration).
Cooldown: Integer for turns until reusable after casting.
LevelRequired: Integer for minimum player level to learn.
GoldCost: Integer cost to learn (10 points when bought).
MPCost: Integer mana cost to cast.


Supported Effects:
Damage: Deals Value damage to the enemy.
Heal: Restores Value HP (up to max_health).
DamageBoost: Increases weapon damage by Value for the fight.
Shield: Adds Value temporary HP.
Stun: Prevents enemy attacks for Value turns.



Example:
{
    "skills": [
        ["Fireball", "Damage", 20, 3, 1, 50, 10],
        ["Heal", "Heal", 30, 4, 2, 75, 15],
        ["Power Strike", "DamageBoost", 5, 5, 3, 100, 20],
        ["Shield", "Shield", 20, 3, 2, 80, 12],
        ["Stun Bolt", "Stun", 1, 4, 4, 120, 25]
    ]
}

Adding New Skills:

Add a new skill array to skills.
Example: Add ["Ice Blast", "Damage", 25, 4, 3, 90, 15] for a new damage skill.
For new effect types (e.g., "Poison"), update player.py’s use_skill function.

8. monster_skills.json
Defines available skills for monsters, including MP costs, cooldowns, weights, and conditions.
Required Structure:
{
    "skills": {
        "SkillID": ["SkillName", "Effect", Value, Cooldown, MPCost, Weight, "Condition"],
        ...
    }
}


skills: Object with string keys as skill IDs (e.g., "1", "2", "10").
Each skill array: [Name, Effect, Value, Cooldown, MPCost, Weight, Condition]
Name: String (e.g., "Goblin Slash").
Effect: String (e.g., "Damage", "Heal", "Stun").
Value: Integer for effect magnitude (e.g., damage or stun duration).
Cooldown: Integer for turns until reusable.
MPCost: Integer mana cost to cast.
Weight: Integer (1-100) for the chance to select this skill (higher = more likely).
Condition: String for when to use (e.g., "low_hp" for healing when HP < 50%, "always" for standard use).


Supported Effects: Same as player skills (Damage, Heal, Stun, etc.).
Supported Conditions: "low_hp" (use if health < 50%), "always" (no condition).

Example:
{
    "skills": {
        "1": ["Bite", "Damage", 5, 2, 5, 70, "always"],
        "2": ["Regen", "Heal", 10, 4, 15, 30, "low_hp"],
        "3": ["Claw", "Damage", 8, 3, 10, 60, "always"],
        "4": ["Fire Breath", "Damage", 15, 5, 20, 50, "always"],
        "5": ["Tail Whip", "Stun", 1, 4, 25, 40, "always"]
    }
}

Adding New Monster Skills:

Add a new key-value pair with a unique ID (e.g., "6") and skill array.
Example: Add "6": ["Poison Spit", "Damage", 10, 3, 12, 55, "always"].
Reference the ID in enemies.json's SkillsList (e.g., [6]).

9. zones.json
Defines game zones with descriptions and associated enemies.
Required Structure:
{
    "ZoneID": {
        "name": "ZoneName",
        "description": "ZoneDescription",
        "enemies": [EnemyID1, EnemyID2, ...]
    },
    ...
}


ZoneID: String key (e.g., "1", "2") for referencing.
Each zone object: 
name: String (e.g., "Forest Clearing").
description: String (e.g., "A beginner-friendly zone with weak goblins. Recommended for levels 1-5.").
enemies: Array of integers referencing enemy IDs from enemies.json (e.g., [1, 2]).



Example:
{
    "1": {
        "name": "Forest Clearing",
        "description": "A beginner-friendly zone with weak goblins. Recommended for levels 1-5.",
        "enemies": [1]
    },
    "2": {
        "name": "Mountain Path",
        "description": "Rugged terrain with trolls. Recommended for levels 5-10.",
        "enemies": [1, 2]
    },
    "3": {
        "name": "Dragon's Lair",
        "description": "Dangerous caves with dragons and tougher foes. Recommended for levels 10+.",
        "enemies": [2, 3]
    }
}

Adding New Zones:

Add a new key-value pair with a unique ID (e.g., "4") and zone object.
Example: Add "4": {"name": "Desert Wastes", "description": "...", "enemies": [3, 4]}.

10. art.json
Defines ASCII art for the player and enemies.
Required Structure:
{
    "player": "ASCIIString",
    "enemies": {
        "EnemyName": "ASCIIString",
        ...
    }
}


player: String containing ASCII art for the player.
enemies: Object mapping enemy names (matching enemies.json) to ASCII art strings.

Example:
{
    "player": "\n  ^ ^\n   O\n  /|\\\n  / \\~\n",
    "enemies": {
        "Goblin": "\n   @@\n  >\\/7\n  -  -\n    ",
        "Troll": "\n   @@\n  >==<\n  / 0 \\\n    ",
        "Dragon": "\n   ^^\n  >==<\n  /~~~\\\n    ",
        "Dark Knight": "\n   ##\n  >==<\n  /| |\\\n    "
    }
}

Adding New Art:

Add a new key-value pair to enemies for each new enemy in enemies.json.
Example: Add "Dark Knight": "\n   ##\n  >==<\n  /| |\\\n    " to match a new enemy.

Tips for Adding New Data

Consistency: Ensure rarity names in gear.json and items.json match config.json’s rarities. Ensure enemy IDs in zones.json match enemies.json.
Monster Skills: Reference skill IDs in enemies.json from monster_skills.json. Higher Weight increases use chance, and "low_hp" conditions make healing skills intelligent.
Scoring: Points are awarded for kills (1), item drops (1/10/20/30 for Common/Uncommon/Rare/Epic), level-ups (10), and skill purchases (10). Modify stats_manager.py to adjust scoring rules.
Zones: Add new zones to zones.json for more exploration. Players can travel via the post-fight menu.
Stats Reset: Editing player_save.json resets stats.json to initial values (via stats_manager.py).
Testing: Run main.py to verify score updates in the combat UI. Test kills, drops, level-ups, skill purchases, and zone travel.
Error Handling: Check the console for errors about missing or invalid JSON files.
Extending Mechanics: To add new item effects (e.g., "Poison") or skill effects (e.g., "Multi-Hit"), update combat.py or player.py.
Backup Files: Back up JSON files before editing to avoid data loss.

Example: Adding a New Zone and Enemy

Update enemies.json:{
    "4": ["Dark Knight", 80, [10, 14], 50, 60, [6, 7]],
    ...
}


Update monster_skills.json (for skills 6 and 7):{
    "skills": {
        "6": ["Dark Slash", "Damage", 15, 3, 15, 60, "always"],
        "7": ["Shadow Heal", "Heal", 20, 5, 25, 40, "low_hp"],
        ...
    }
}


Update zones.json:{
    "4": {
        "name": "Dark Castle",
        "description": "A high-level zone with knights and shadows. Recommended for levels 15+.",
        "enemies": [3, 4]
    },
    ...
}


Update art.json:{
    "enemies": {
        "Dark Knight": "\n   ##\n  >==<\n  /| |\\\n    ",
        ...
    },
    ...
}



This guide should help you customize "Loot Grind" by editing JSON files. If you need assistance with specific additions or new mechanics, let me know!