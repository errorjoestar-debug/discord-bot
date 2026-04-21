import aiohttp
import os
from datetime import datetime, timezone, timedelta


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

PRAYER_COLORS = {
    "Fajr": 0x1A237E,
    "Sunrise": 0xFF6F00,
    "Dhuhr": 0xF9A825,
    "Asr": 0xFF8F00,
    "Maghrib": 0xE65100,
    "Isha": 0x0D47A1,
}


def _clean_time(time_str: str) -> str:
    return time_str.split()[0]


async def get_prayer_times(
    city: str | None = None,
    country: str | None = None,
    method: int | None = None,
) -> dict | None:
    city = city or os.getenv("PRAYER_CITY", "Cairo")
    country = country or os.getenv("PRAYER_COUNTRY", "EG")
    if method is None:
        method = int(os.getenv("PRAYER_METHOD", "5"))

    params = {"city": city, "country": country, "method": method}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ALADHAN_API, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                result = dict(data["data"]["timings"])
                result["_timezone"] = data["data"].get("meta", {}).get("timezone", "UTC")
                result["_date"] = data["data"].get("date", {})
                return result
    except Exception:
        return None


async def get_hijri_date(
    city: str | None = None,
    country: str | None = None,
    method: int | None = None,
) -> dict | None:
    city = city or os.getenv("PRAYER_CITY", "Cairo")
    country = country or os.getenv("PRAYER_COUNTRY", "EG")
    if method is None:
        method = int(os.getenv("PRAYER_METHOD", "5"))

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
        time_24 = _clean_time(timings.get(key, "--:--"))
        ar_name = PRAYER_NAMES_AR.get(key, key)
        try:
            dt = datetime.strptime(time_24, "%H:%M")
            h = dt.hour
            period = "ص" if h < 12 else "م"
            h12 = h % 12 or 12
            time_12 = f"{h12}:{dt.minute:02d} {period}"
        except ValueError:
            time_12 = time_24
        lines.append(f"{emoji} **{ar_name}** ─ {time_12} ─ `{time_24}`")
    return "\n".join(lines)


def _to_12h(time_24: str) -> str:
    """Convert HH:MM 24-hour to Arabic 12-hour format."""
    try:
        dt = datetime.strptime(time_24, "%H:%M")
        h = dt.hour
        period = "ص" if h < 12 else "م"
        h12 = h % 12 or 12
        return f"{h12}:{dt.minute:02d} {period}"
    except ValueError:
        return time_24


def get_next_prayer(timings: dict) -> tuple[str, str, str] | None:
    """Returns (key, remaining_text, actual_time_12h) or None."""
    tz_name = timings.get("_timezone", "UTC")
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo(tz_name))
    except Exception:
        now = datetime.now(timezone.utc)

    now_minutes = now.hour * 60 + now.minute

    for key in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
        time_str = timings.get(key, "")
        try:
            time_24 = _clean_time(time_str)
            t = datetime.strptime(time_24, "%H:%M")
            prayer_minutes = t.hour * 60 + t.minute
            if prayer_minutes > now_minutes:
                remaining = prayer_minutes - now_minutes
                hours, mins = divmod(remaining, 60)
                time_12h = _to_12h(time_24)
                if hours > 0:
                    return key, f"{hours} ساعة و {mins} دقيقة", time_12h
                return key, f"{mins} دقيقة", time_12h
        except ValueError:
            continue
    
    # If no prayer left today, return Fajr for tomorrow
    fajr_time = timings.get("Fajr", "")
    if fajr_time:
        try:
            time_24 = _clean_time(fajr_time)
            t = datetime.strptime(time_24, "%H:%M")
            fajr_minutes = t.hour * 60 + t.minute
            remaining = (24 * 60 - now_minutes) + fajr_minutes
            hours, mins = divmod(remaining, 60)
            time_12h = _to_12h(time_24)
            if hours > 0:
                return "Fajr", f"{hours} ساعة و {mins} دقيقة", time_12h
            return "Fajr", f"{mins} دقيقة", time_12h
        except ValueError:
            pass
    
    return None


async def get_sun_times(
    city: str | None = None,
    country: str | None = None,
    method: int | None = None,
) -> dict | None:
    city = city or os.getenv("PRAYER_CITY", "Cairo")
    country = country or os.getenv("PRAYER_COUNTRY", "EG")
    if method is None:
        method = int(os.getenv("PRAYER_METHOD", "5"))

    params = {"city": city, "country": country, "method": method}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ALADHAN_API, params=params) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                timings = data["data"]["timings"]
                return {
                    "sunrise": timings.get("Sunrise", "").split()[0],
                    "sunset": timings.get("Sunset", "").split()[0],
                    "midday": timings.get("Dhuhr", "").split()[0],
                    "timezone": data["data"]["meta"].get("timezone", "UTC"),
                }
    except Exception:
        return None
