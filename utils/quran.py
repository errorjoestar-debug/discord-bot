import aiohttp
import random


QURAN_API = "https://api.alquran.cloud/v1"


async def get_surah_list() -> list[dict] | None:
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{QURAN_API}/surah"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                return data["data"]
    except Exception:
        return None


async def get_random_verse() -> dict | None:
    edition = "quran-uthmani"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{QURAN_API}/ayah/random/editions/{edition}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                ayah = data["data"][0]
                return {
                    "text": ayah["text"],
                    "surah_name": ayah["surah"]["name"],
                    "surah_english": ayah["surah"]["englishName"],
                    "ayah_number": ayah["numberInSurah"],
                    "surah_number": ayah["surah"]["number"],
                    "absolute_number": ayah["number"],
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
                    "absolute_number": a["number"],
                }
    except Exception:
        return None


async def get_surah(surah: int) -> dict | None:
    edition = "quran-uthmani"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{QURAN_API}/surah/{surah}/{edition}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                s = data["data"]
                ayahs = s["ayahs"]
                return {
                    "name": s["name"],
                    "englishName": s["englishName"],
                    "englishNameTranslation": s["englishNameTranslation"],
                    "revelationType": s["revelationType"],
                    "numberOfAyahs": s["numberOfAyahs"],
                    "ayahs": [{"text": a["text"], "number": a["numberInSurah"]} for a in ayahs],
                }
    except Exception:
        return None


async def search_quran(keyword: str) -> list[dict] | None:
    edition = "quran-uthmani"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{QURAN_API}/search/{keyword}/all/{edition}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                results = data["data"][:10]  # Limit to 10 results
                return [
                    {
                        "text": r["text"],
                        "surah_name": r["surah"]["name"],
                        "surah_english": r["surah"]["englishName"],
                        "ayah_number": r["numberInSurah"],
                        "surah_number": r["surah"]["number"],
                    }
                    for r in results
                ]
    except Exception:
        return None
