import os
import json
from utils import load_json, save_json

STATS_FILE = 'stats.json'
PLAYER_SAVE_FILE = 'player_save.json'

def initialize_stats():
    """Initialize or reset stats.json, checking player_save.json's modification time."""
    initial_stats = {
        "kills": 0,
        "play_time": 0,
        "max_level": 1,
        "total_xp": 0,
        "total_gold": 0,
        "total_gold_spent": 0,
        "total_gold_spent_on_skills": 0,
        "score": 0
    }
    # Check if stats.json exists and player_save.json's modification time
    player_mtime = os.path.getmtime(PLAYER_SAVE_FILE) if os.path.exists(PLAYER_SAVE_FILE) else 0
    stats_mtime = os.path.getmtime(STATS_FILE) if os.path.exists(STATS_FILE) else 0
    if not os.path.exists(STATS_FILE) or player_mtime > stats_mtime:
        save_json(STATS_FILE, initial_stats)
        return initial_stats
    return load_json(STATS_FILE)

def update_score(stats, event, rarity=None):
    """Update the score based on game events."""
    points = 0
    if event == 'kill':
        points = 1
    elif event == 'item_drop':
        points = {'Common': 1, 'Uncommon': 10, 'Rare': 20, 'Epic': 30}.get(rarity, 0)
    elif event == 'level_up':
        points = 10
    elif event == 'buy_skill':
        points = 10
    stats['score'] += points
    save_json(STATS_FILE, stats)
    return points