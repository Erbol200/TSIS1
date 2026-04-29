import json, os
def load_data(filename, default):
    if not os.path.exists(filename): return default
    with open(filename, 'r') as f: return json.load(f)
def save_data(filename, data):
    with open(filename, 'w') as f: json.dump(data, f, indent=4)