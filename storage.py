import json
import os
import logging
from datetime import datetime
from config import DATA_DIR, NEWS_FILE, STATE_FILE, SUBREDDITS

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

NEWS_PATH = os.path.join(DATA_DIR, NEWS_FILE)
STATE_PATH = os.path.join(DATA_DIR, STATE_FILE)

def load_state():
    """
    Loads the state file which contains processed post IDs and last run time.
    """
    if not os.path.exists(STATE_PATH):
        return {"processed_ids": [], "last_run": None}
    
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading state: {e}")
        return {"processed_ids": [], "last_run": None}

def save_state(state):
    """
    Saves the state to disk.
    """
    state["last_run"] = datetime.now().isoformat()
    try:
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving state: {e}")

def load_news_data():
    """
    Loads existing news data.
    """
    if not os.path.exists(NEWS_PATH):
        return []
    
    try:
        with open(NEWS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading news data: {e}")
        return []

def append_news_data(new_entries):
    """
    Appends new entries to the news file.
    Sorts by datePosted (newest first).
    """
    if not new_entries:
        return

    data = load_news_data()
    data.extend(new_entries)
    
    # Sort by datePosted descending
    data.sort(key=lambda x: x.get('datePosted', ''), reverse=True)
    
    try:
        with open(NEWS_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info(f"Added {len(new_entries)} new entries to {NEWS_FILE}")
    except Exception as e:
        logging.error(f"Error saving news data: {e}")

def prune_data():
    """
    Removes news entries and state IDs older than 7 days.
    This is a simplification; a robust system might archive them.
    """
    # TODO: Implement pruning logic based on datePosted
    pass
