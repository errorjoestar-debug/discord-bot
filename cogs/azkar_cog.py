import discord
from discord import app_commands
from discord.ext import commands

from utils.azkar import (
    get_morning_azkar,
    get_evening_azkar,
    get_sleep_azkar,
    get_random_hadith,
    get_random_dua,
    format_azkar,
)

AZKAR_CONFIG = {
    "morning": {
        "title": "☀️ أذكار الصباح",
        "color": 0xFF8C00,
        "footer": "لا تنسَ ذكر الله ☀️ ﴿ وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ طُلُوعِ الشَّمْسِ ﴾",
    },
    "evening": {
        "title": "🌇 أذكار المساء",
        "color": 0x7B68EE,
        "footer": "لا تنسَ ذكر الله 🌇 ﴿ وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ غُرُوبِ الشَّمْسِ ﴾",
    },
    "sleep": {
        "title": "🌙 أذكار النوم",
        "color": 0x1A237E,
        "footer": "لا تنسَ ذكر الله قبل النوم 🌙 ﴿ إِنَّ فِي خَلْقِ السَّمَاوَاتِ وَالْأَرْضِ ﴾",
    },
}

BOOK_ICON = "https://cdn-icons-png.flaticon.com/512/2998/2998551.png"
DUA_ICON = "https://cdn-icons-png.flaticon.com/512/4825/4825426.png"


class AzkarCog(commands.Cog, name="الأذكار"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="morning-azkar", description="☀️ أذكار الصباح للأذكار والورد الصباحي")
    async def morning_azkar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        azkar = get_morning_azkar()
        await self._send_azkar(interaction, azkar, "morning")

    @app_commands.command(name="evening-azkar", description="🌇 أذكار المساء للأذكار والورد المسائي")
    async def evening_azkar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        azkar = get_evening_azkar()
        await self._send_azkar(interaction, azkar, "evening")

    @app_commands.command(name="sleep-azkar", description="🌙 أذكار النوم قبل المنام")
    async def sleep_azkar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        azkar = get_sleep_azkar()
        await self._send_azkar(interaction, azkar, "sleep")

    async def _send_azkar(self, interaction, azkar, azkar_type):
        config = AZKAR_CONFIG[azkar_type]
        text = format_azkar(azkar, config["title"])
        chunks = self._chunk_text(text, 4096)

        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=config["title"] if i == 0 else None,
                description=chunk,
                color=config["color"],
            )
            if i == 0:
                embed.set_thumbnail(url=BOOK_ICON)
            if len(chunks) > 1:
                embed.set_footer(text=f"الجزء {i+1} من {len(chunks)} ─ {config['footer']}")
            else:
                embed.set_footer(text=config["footer"])
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="hadith", description="📖 حديث شريف عشوائي من الأحاديث الصحيحة")
    async def hadith(self, interaction: discord.Interaction):
        h = get_random_hadith()
        embed = discord.Embed(
            title="📖 حديث شريف",
            description=f"```\n{h['text']}\n```",
            color=0x27AE60,
        )
        embed.set_thumbnail(url=BOOK_ICON)
        embed.add_field(name="الراوي", value=h["narrator"], inline=True)
        embed.add_field(name="المصدر", value=h["source"], inline=True)
        embed.set_footer(text="﴿ مَّن يُطِعِ ٱلرَّسُولَ فَقَدْ أَطَاعَ ٱللَّهَ ﴾")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dua", description="🤲 دعاء عشوائي من أدعية القرآن الكريم")
    async def dua(self, interaction: discord.Interaction):
        d = get_random_dua()
        embed = discord.Embed(
            title="🤲 دعاء",
            description=f"```\n{d['text']}\n```",
            color=0x1ABC9C,
        )
        embed.set_thumbnail(url=DUA_ICON)
        embed.add_field(name="المصدر", value=d["source"], inline=False)
        embed.set_footer(text="﴿ ادْعُونِي أَسْتَجِبْ لَكُمْ ﴾")
        await interaction.response.send_message(embed=embed)

    @staticmethod
    def _chunk_text(text: str, max_len: int) -> list[str]:
        if len(text) <= max_len:
            return [text]
        chunks = []
        lines = text.split("\n")
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > max_len:
                chunks.append(current)
                current = line
            else:
                current = current + "\n" + line if current else line
        if current:
            chunks.append(current)
        return chunks


async def setup(bot: commands.Bot):
    await bot.add_cog(AzkarCog(bot))
