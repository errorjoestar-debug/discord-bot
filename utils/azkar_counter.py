import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
COUNTER_FILE = DATA_DIR / "azkar_counters.json"


def _load_counters() -> dict:
    if not COUNTER_FILE.exists():
        return {}
    with open(COUNTER_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_counters(counters: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump(counters, f, ensure_ascii=False, indent=2)


def get_counter(user_id: int) -> int:
    counters = _load_counters()
    return counters.get(str(user_id), 0)


def increment_counter(user_id: int, amount: int = 1) -> int:
    counters = _load_counters()
    uid = str(user_id)
    counters[uid] = counters.get(uid, 0) + amount
    _save_counters(counters)
    return counters[uid]


def reset_counter(user_id: int) -> int:
    counters = _load_counters()
    uid = str(user_id)
    counters[uid] = 0
    _save_counters(counters)
    return 0


def set_counter(user_id: int, value: int) -> int:
    counters = _load_counters()
    uid = str(user_id)
    counters[uid] = value
    _save_counters(counters)
    return value
