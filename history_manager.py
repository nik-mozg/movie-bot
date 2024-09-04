import json
from typing import List, Dict, Union

HISTORY_FILE = "history.json"

def load_history() -> List[Dict[str, Union[str, int, bool]]]:
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
       
        return []

def save_history(history: List[Dict[str, Union[str, int, bool]]]) -> None:
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)

def add_to_history(movie: Dict[str, Union[str, int, bool]]) -> None:
    
    history = load_history()
    history.append(movie)
    save_history(history)

def get_history_by_date(date_str: str) -> List[Dict[str, Union[str, int, bool]]]:
    
    history = load_history()
    filtered_history = [entry for entry in history if entry["date"].startswith(date_str)]
    return filtered_history

def mark_movie_as_watched(movie_id: int, watched: bool) -> None:
    
    
    history = load_history()
    
    
    for entry in history:
        if entry['id'] == movie_id:
            entry['watched'] = watched
            break
    
   
    save_history(history)
