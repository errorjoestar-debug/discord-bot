import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_json(filename: str) -> list[dict]:
    filepath = DATA_DIR / filename
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def get_morning_azkar() -> list[dict]:
    return _load_json("azkar_morning.json")


def get_evening_azkar() -> list[dict]:
    return _load_json("azkar_evening.json")


def get_sleep_azkar() -> list[dict]:
    return _load_json("azkar_sleep.json")


def get_random_hadith() -> dict:
    hadiths = _load_json("hadith.json")
    return random.choice(hadiths)


def get_hadith_list() -> list[dict]:
    return _load_json("hadith.json")


def get_random_dua() -> dict:
    duas = _load_json("dua.json")
    return random.choice(duas)


def get_dua_list() -> list[dict]:
    return _load_json("dua.json")


def format_azkar(azkar_list: list[dict], title: str) -> str:
    lines = [f"🕌 **{title}**\n"]
    for i, z in enumerate(azkar_list, 1):
        count_str = f" (×{z['count']})" if z.get("count", 1) > 1 else ""
        source_str = f" [{z['source']}]" if z.get("source") else ""
        lines.append(f"**{i}.** {z['text']}{count_str}{source_str}")
    return "\n".join(lines)
