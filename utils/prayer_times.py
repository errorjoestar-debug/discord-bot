import aiohttp
import os
from datetime import datetime


ALADHAN_API = "https://api.aladhan.com/v1/timingsByCity"

PRAYER_NAMES_AR = {
    "Fajr": "الفجر",
    "Sunrise": "الشروق",
    "Dhuhr": "الظهر",
    "Asr": "العصر",
    "Maghrib": "المغرب",
    "Isha": "العشاء",
}

PRAYER_EMOJIS = {
    "Fajr": "🌙",
    "Sunrise": "🌅",
    "Dhuhr": "☀️",
    "Asr": "🌤️",
    "Maghrib": "🌇",
    "Isha": "🌃",
}


async def get_prayer_times(
    city: str | None = None,
    country: str | None = None,
    method: int | None = None,
) -> dict | None:
    city = city or os.getenv("PRAYER_CITY", "Cairo")
    country = country or os.getenv("PRAYER_COUNTRY", "EG")
    method = method or int(os.getenv("PRAYER_METHOD", "5"))

    params = {"city": city, "country": country, "method": method}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ALADHAN_API, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                return data["data"]["timings"]
    except Exception:
        return None


async def get_hijri_date(
    city: str | None = None,
    country: str | None = None,
    method: int | None = None,
) -> dict | None:
    city = city or os.getenv("PRAYER_CITY", "Cairo")
    country = country or os.getenv("PRAYER_COUNTRY", "EG")
    method = method or int(os.getenv("PRAYER_METHOD", "5"))

    params = {"city": city, "country": country, "method": method}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ALADHAN_API, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                return data["data"]["date"]["hijri"]
    except Exception:
        return None


def format_prayer_times(timings: dict) -> str:
    lines = []
    for key, emoji in PRAYER_EMOJIS.items():
        time_24 = timings.get(key, "--:--")
        ar_name = PRAYER_NAMES_AR.get(key, key)
        try:
            dt = datetime.strptime(time_24.split()[0], "%H:%M")
            time_12 = dt.strftime("%I:%M %p")
        except (ValueError, IndexError):
            time_12 = time_24
        lines.append(f"{emoji} **{ar_name}**: {time_12} ({time_24.split()[0]})")
    return "\n".join(lines)


def get_next_prayer(timings: dict) -> tuple[str, str] | None:
    now = datetime.now()
    now_minutes = now.hour * 60 + now.minute

    for key in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        time_str = timings.get(key, "")
        try:
            t = datetime.strptime(time_str.split()[0], "%H:%M")
            prayer_minutes = t.hour * 60 + t.minute
            if prayer_minutes > now_minutes:
                remaining = prayer_minutes - now_minutes
                hours, mins = divmod(remaining, 60)
                return key, f"{hours} ساعة و {mins} دقيقة"
        except (ValueError, IndexError):
            continue
    return None
