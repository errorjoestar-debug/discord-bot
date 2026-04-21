import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"

QURAN_AUDIO_API = "https://cdn.islamic.network/quran/audio/128"


def get_reciters() -> list[dict]:
    with open(DATA_DIR / "reciters.json", encoding="utf-8") as f:
        return json.load(f)


def get_reciter_by_id(reciter_id: str) -> dict | None:
    for r in get_reciters():
        if r["id"] == reciter_id:
            return r
    return None


def get_ayah_audio_url(ayah_number: int, reciter_id: str = "ar.alafasy") -> str:
    return f"{QURAN_AUDIO_API}/{reciter_id}/{ayah_number}.mp3"


def get_random_allah_name() -> dict:
    with open(DATA_DIR / "allah_names.json", encoding="utf-8") as f:
        names = json.load(f)
    return random.choice(names)
