import random
import time
import os
def random_sleep(min_seconds=2, max_seconds=5):
    """Sleep for a random amount of time to simulate human behavior."""
    time.sleep(random.uniform(min_seconds, max_seconds))

def save_list(filename, data_list):
    folder = "information"
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    with open(filepath, "w") as f:
        for item in data_list:
            f.write(f"{item}\n")
    print(f"Saved {len(data_list)} items to {filepath}")

def read_list(filename):
    folder = "information"
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        # Fallback to checking current directory or if filename is a full path
        if os.path.exists(filename):
            filepath = filename
        else:
            return set()
    
    with open(filepath, "r") as f:
        return set(line.strip() for line in f if line.strip())

def log_action(filename, message):
    folder = "information"
    if not os.path.exists(folder):
        os.makedirs(folder)
    filepath = os.path.join(folder, filename)
    with open(filepath, "a") as f:
        f.write(f"{message}\n")
