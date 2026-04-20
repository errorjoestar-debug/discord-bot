import aiohttp
import random


QURAN_API = "https://api.alquran.cloud/v1"


async def get_random_verse() -> dict | None:
    edition = "quran-uthmani"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{QURAN_API}/ayah/{edition}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                ayah = data["data"]
                return {
                    "text": ayah["text"],
                    "surah_name": ayah["surah"]["name"],
                    "surah_english": ayah["surah"]["englishName"],
                    "ayah_number": ayah["numberInSurah"],
                    "surah_number": ayah["surah"]["number"],
                }
    except Exception:
        return None


async def get_verse(surah: int, ayah: int) -> dict | None:
    edition = "quran-uthmani"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{QURAN_API}/ayah/{surah}:{ayah}/{edition}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                a = data["data"]
                return {
                    "text": a["text"],
                    "surah_name": a["surah"]["name"],
                    "surah_english": a["surah"]["englishName"],
                    "ayah_number": a["numberInSurah"],
                    "surah_number": a["surah"]["number"],
                }
    except Exception:
        return None
