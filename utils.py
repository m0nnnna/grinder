import json
import os

def load_json(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Error: {filename} not found. Please create the file with valid game data.")
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error: {filename} contains invalid JSON. Details: {str(e)}")

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)