import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent.parent / "data" / "server_settings.json"


def _load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        return {}
    with open(SETTINGS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_settings(settings: dict):
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def get_server_settings(guild_id: int) -> dict:
    settings = _load_settings()
    return settings.get(str(guild_id), {})


def set_server_city(guild_id: int, city: str, country: str, method: int = 5):
    settings = _load_settings()
    gid = str(guild_id)
    if gid not in settings:
        settings[gid] = {}
    settings[gid]["city"] = city
    settings[gid]["country"] = country
    settings[gid]["method"] = method
    _save_settings(settings)


def get_server_city(guild_id: int) -> tuple[str, str, int] | None:
    s = get_server_settings(guild_id)
    if "city" in s:
        return s["city"], s.get("country", "EG"), s.get("method", 5)
    return None
