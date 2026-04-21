import discord
from discord import app_commands
from discord.ext import commands

from utils.azkar import (
    get_morning_azkar,
    get_evening_azkar,
    get_sleep_azkar,
    get_random_hadith,
    get_hadith_list,
    get_random_dua,
    get_dua_list,
    format_azkar,
)
from utils.azkar_counter import get_counter, increment_counter, reset_counter, set_counter

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

BOOK_ICON = "https://images.unsplash.com/photo-1576413329366-5b2c6e0463e4?w=800&q=80"
DUA_ICON = "https://images.unsplash.com/photo-1544027993-37dbfe43562a?w=800&q=80"


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
                embed.set_footer(text=f"الجزء {i+1} من {len(chunks)} ─ {config['footer']} • MuslimBot")
            else:
                embed.set_footer(text=f"{config['footer']} • MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="hadith", description="📖 حديث شريف عشوائي من الأحاديث الصحيحة")
    async def hadith(self, interaction: discord.Interaction):
        h = get_random_hadith()
        embed = discord.Embed(
            title=f"� حديث شريف",
            description=f"```\n{h['text']}\n```",
            color=0x8E44AD,
        )
        embed.set_thumbnail(url=BOOK_ICON)
        embed.add_field(name="الراوي", value=h["narrator"], inline=True)
        embed.add_field(name="المصدر", value=h["source"], inline=True)
        embed.set_footer(text="﴿ مَّن يُطِعِ ٱلرَّسُولَ فَقَدْ أَطَاعَ ٱللَّهَ ﴾ • MuslimBot")
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
        embed.set_footer(text="﴿ ادْعُونِي أَسْتَجِبْ لَكُمْ ﴾ • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hadith-list", description="📚 عرض قائمة الأحاديث الصحيحة")
    async def hadith_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        hadiths = get_hadith_list()
        chunks = self._chunk_text_hadith(hadiths)
        
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="📚 قائمة الأحاديث الصحيحة" if i == 0 else None,
                description=chunk,
                color=0x8E44AD,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text=f"الجزء {i+1} من {len(chunks)} • MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="dua-list", description="🤲 عرض قائمة الأدعية")
    async def dua_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        duas = get_dua_list()
        chunks = self._chunk_text_dua(duas)
        
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="🤲 قائمة الأدعية" if i == 0 else None,
                description=chunk,
                color=0x27AE60,
            )
            embed.set_thumbnail(url=DUA_ICON)
            embed.set_footer(text=f"الجزء {i+1} من {len(chunks)} • MuslimBot")
            await interaction.followup.send(embed=embed)

    @staticmethod
    def _chunk_text_hadith(hadiths: list[dict]) -> list[str]:
        chunks = []
        current = ""
        for i, h in enumerate(hadiths, 1):
            line = f"**{i}.** {h['text'][:100]}... ─ {h['narrator']}\n"
            if len(current) + len(line) > 4000:
                chunks.append(current)
                current = line
            else:
                current = current + line if current else line
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _chunk_text_dua(duas: list[dict]) -> list[str]:
        chunks = []
        current = ""
        for i, d in enumerate(duas, 1):
            line = f"**{i}.** {d['text'][:100]}... ─ {d['source']}\n"
            if len(current) + len(line) > 4000:
                chunks.append(current)
                current = line
            else:
                current = current + line if current else line
        if current:
            chunks.append(current)
        return chunks

    @app_commands.command(name="azkar-count", description="🔢 عداد ذكر شخصي")
    @app_commands.describe(action="الإجراء: show, increment, reset, set")
    @app_commands.describe(value="القيمة (للإجراء set فقط)")
    async def azkar_count(
        self,
        interaction: discord.Interaction,
        action: str = "show",
        value: int = 33,
    ):
        user_id = interaction.user.id

        if action == "show":
            count = get_counter(user_id)
            embed = discord.Embed(
                title="🔢 عداد الذكر",
                description=f"عدد ذكرك الحالي: **{count}**",
                color=0x3498DB,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="﴿ فَاذْكُرُونِي أَذْكُرْكُمْ ﴾ • MuslimBot")
            await interaction.response.send_message(embed=embed)
        
        elif action == "increment":
            count = increment_counter(user_id)
            embed = discord.Embed(
                title="✅ تم زيادة العداد",
                description=f"عدد ذكرك الجديد: **{count}**",
                color=0x27AE60,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="﴿ فَاذْكُرُونِي أَذْكُرْكُمْ ﴾ • MuslimBot")
            await interaction.response.send_message(embed=embed)
        
        elif action == "reset":
            count = reset_counter(user_id)
            embed = discord.Embed(
                title="🔄 تم تصفير العداد",
                description=f"عدد ذكرك: **{count}**",
                color=0xF39C12,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="﴿ فَاذْكُرُونِي أَذْكُرْكُمْ ﴾ • MuslimBot")
            await interaction.response.send_message(embed=embed)
        
        elif action == "set":
            count = set_counter(user_id, value)
            embed = discord.Embed(
                title="✅ تم تعيين العداد",
                description=f"عدد ذكرك: **{count}**",
                color=0x27AE60,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="﴿ فَاذْكُرُونِي أَذْكُرْكُمْ ﴾ • MuslimBot")
            await interaction.response.send_message(embed=embed)
        
        else:
            embed = discord.Embed(
                title="❌ إجراء غير صحيح",
                description="استخدم: show, increment, reset, set",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
