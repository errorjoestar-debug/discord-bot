import aiohttp

TAFSIR_API = "https://api.alquran.cloud/v1"


async def get_tafsir(surah: int, ayah: int) -> dict | None:
    edition = "ar.muyassar"
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{TAFSIR_API}/ayah/{surah}:{ayah}/{edition}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("code") != 200:
                    return None
                a = data["data"]
                return {
                    "text": a["text"],
                    "tafsir": a.get("tafsir", None),
                    "surah_name": a["surah"]["name"],
                    "surah_english": a["surah"]["englishName"],
                    "ayah_number": a["numberInSurah"],
                }
    except Exception:
        return None
