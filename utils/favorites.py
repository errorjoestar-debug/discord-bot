import json
import time
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
FAVORITES_FILE = DATA_DIR / "favorites.json"


def _load_favorites() -> dict:
    """Load favorites from file."""
    if not FAVORITES_FILE.exists():
        return {}
    with open(FAVORITES_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_favorites(favorites: dict):
    """Save favorites to file."""
    with open(FAVORITES_FILE, encoding="utf-8", mode="w") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)


def add_favorite(user_id: int, item_type: str, item_id: str, content: str, metadata: dict = None):
    """Add an item to user's favorites."""
    favorites = _load_favorites()
    uid = str(user_id)
    
    if uid not in favorites:
        favorites[uid] = []
    
    # Check if already exists
    for fav in favorites[uid]:
        if fav["type"] == item_type and fav["id"] == item_id:
            return False  # Already exists
    
    favorites[uid].append({
        "type": item_type,
        "id": item_id,
        "content": content,
        "metadata": metadata or {},
        "added_at": str(time.time())
    })
    
    _save_favorites(favorites)
    return True


def remove_favorite(user_id: int, item_type: str, item_id: str) -> bool:
    """Remove an item from user's favorites."""
    favorites = _load_favorites()
    uid = str(user_id)
    
    if uid not in favorites:
        return False
    
    for i, fav in enumerate(favorites[uid]):
        if fav["type"] == item_type and fav["id"] == item_id:
            favorites[uid].pop(i)
            _save_favorites(favorites)
            return True
    
    return False


def get_favorites(user_id: int, item_type: str = None) -> list[dict]:
    """Get user's favorites, optionally filtered by type."""
    favorites = _load_favorites()
    uid = str(user_id)
    
    if uid not in favorites:
        return []
    
    if item_type:
        return [fav for fav in favorites[uid] if fav["type"] == item_type]
    
    return favorites[uid]


def clear_favorites(user_id: int) -> bool:
    """Clear all user's favorites."""
    favorites = _load_favorites()
    uid = str(user_id)
    
    if uid not in favorites:
        return False
    
    favorites[uid] = []
    _save_favorites(favorites)
    return True


def search_favorites(user_id: int, keyword: str) -> list[dict]:
    """Search in user's favorites by keyword."""
    favorites = get_favorites(user_id)
    keyword_lower = keyword.lower()
    
    results = []
    for fav in favorites:
        if keyword_lower in fav["content"].lower():
            results.append(fav)
    
    return results
