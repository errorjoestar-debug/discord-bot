import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_events() -> list[dict]:
    with open(DATA_DIR / "islamic_events.json", encoding="utf-8") as f:
        return json.load(f)


def get_upcoming_events(hijri_month: int, hijri_day: int, days_ahead: int = 30) -> list[dict]:
    events = _load_events()
    upcoming = []

    for event in events:
        event_month = event["hijri_month"]
        event_day = event["hijri_day"]

        diff_months = event_month - hijri_month
        if diff_months < 0:
            diff_months += 12

        diff_days = diff_months * 30 + (event_day - hijri_day)
        if 0 <= diff_days <= days_ahead:
            event_copy = dict(event)
            event_copy["days_until"] = diff_days
            upcoming.append(event_copy)

    upcoming.sort(key=lambda e: e["days_until"])
    return upcoming


def get_today_events(hijri_month: int, hijri_day: int) -> list[dict]:
    events = _load_events()
    return [
        e for e in events
        if e["hijri_month"] == hijri_month and e["hijri_day"] == hijri_day
    ]
