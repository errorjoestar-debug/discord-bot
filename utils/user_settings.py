import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
USER_SETTINGS_FILE = DATA_DIR / "user_settings.json"


def _load_user_settings() -> dict:
    if not USER_SETTINGS_FILE.exists():
        return {}
    with open(USER_SETTINGS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_user_settings(settings: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_user_settings(user_id: int) -> dict:
    settings = _load_user_settings()
    return settings.get(str(user_id), {})


def set_user_setting(user_id: int, key: str, value: str | int):
    settings = _load_user_settings()
    uid = str(user_id)
    if uid not in settings:
        settings[uid] = {}
    settings[uid][key] = value
    _save_user_settings(settings)


def get_user_reciter(user_id: int) -> str | None:
    settings = get_user_settings(user_id)
    return settings.get("reciter")


def set_user_reciter(user_id: int, reciter: str):
    set_user_setting(user_id, "reciter", reciter)


def get_user_city(user_id: int) -> tuple[str, str] | None:
    settings = get_user_settings(user_id)
    city = settings.get("city")
    country = settings.get("country")
    if city and country:
        return city, country
    return None


def set_user_city(user_id: int, city: str, country: str):
    set_user_setting(user_id, "city", city)
    set_user_setting(user_id, "country", country)
