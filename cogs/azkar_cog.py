import io
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
from utils.quran_image import create_azkar_image, create_hadith_image, create_dua_image
from utils.views import PaginationView, AzkarCounterView, AyahHadithView
from utils.favorites import get_favorites, clear_favorites, search_favorites

AZKAR_CONFIG = {
    "morning": {
        "title": "☀️ أذكار الصباح",
        "color": 0xFF8C00,
        "color_hex": "#FF8C00",
        "footer": "لا تنسَ ذكر الله ☀️ ﴿ وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ طُلُوعِ الشَّمْسِ ﴾",
    },
    "evening": {
        "title": "🌇 أذكار المساء",
        "color": 0x7B68EE,
        "color_hex": "#7B68EE",
        "footer": "لا تنسَ ذكر الله 🌇 ﴿ وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ غُرُوبِ الشَّمْسِ ﴾",
    },
    "sleep": {
        "title": "🌙 أذكار النوم",
        "color": 0x1A237E,
        "color_hex": "#1A237E",
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

        # Try to send as images first
        try:
            images = await create_azkar_image(
                config["title"], azkar, f"{config['footer']} • MuslimBot", config["color_hex"]
            )
            if images:
                for img_bytes in images:
                    file = discord.File(io.BytesIO(img_bytes), filename="azkar.png")
                    embed = discord.Embed(color=config["color"])
                    embed.set_image(url="attachment://azkar.png")
                    await interaction.followup.send(embed=embed, file=file)
                return
        except Exception:
            pass

        # Fallback to text
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
                embed.set_footer(text=f"الجزء {i+1}/{len(chunks)} ─ {config['footer']} • MuslimBot")
            else:
                embed.set_footer(text=f"{config['footer']} • MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="hadith", description="📖 حديث شريف عشوائي من الأحاديث الصحيحة")
    async def hadith(self, interaction: discord.Interaction):
        h = get_random_hadith()
        hadith_id = f"{h['narrator']}_{h['source'][:20]}"
        content = f"{h['text']}\n\nالراوي: {h['narrator']}\nالمصدر: {h['source']}"
        metadata = {"narrator": h["narrator"], "source": h["source"]}

        # Try image first
        try:
            img_bytes = await create_hadith_image(h['text'], h['narrator'], h['source'])
            if img_bytes:
                file = discord.File(io.BytesIO(img_bytes), filename="hadith.png")
                embed = discord.Embed(color=0x8E44AD)
                embed.set_image(url="attachment://hadith.png")
                embed.set_footer(text="﴿ مَّن يُطِعِ ٱلرَّسُولَ فَقَدْ أَطَاعَ ٱللَّهَ ﴾ • MuslimBot")
                view = AyahHadithView(interaction.user.id, "hadith", hadith_id, content, metadata)
                await interaction.response.send_message(embed=embed, file=file, view=view)
                return
        except Exception:
            pass

        # Fallback to text
        embed = discord.Embed(
            title="📖 حديث شريف",
            description=f"```\n{h['text']}\n```",
            color=0x8E44AD,
        )
        embed.set_thumbnail(url=BOOK_ICON)
        embed.add_field(name="الراوي", value=h["narrator"], inline=True)
        embed.add_field(name="المصدر", value=h["source"], inline=True)
        embed.set_footer(text="﴿ مَّن يُطِعِ ٱلرَّسُولَ فَقَدْ أَطَاعَ ٱللَّهَ ﴾ • MuslimBot")
        view = AyahHadithView(interaction.user.id, "hadith", hadith_id, content, metadata)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="dua", description="🤲 دعاء عشوائي من أدعية القرآن الكريم")
    async def dua(self, interaction: discord.Interaction):
        d = get_random_dua()
        dua_id = f"dua_{d['source'][:20]}"
        content = f"{d['text']}\n\nالمصدر: {d['source']}"
        metadata = {"source": d["source"]}

        # Try image first
        try:
            img_bytes = await create_dua_image(d['text'], d['source'])
            if img_bytes:
                file = discord.File(io.BytesIO(img_bytes), filename="dua.png")
                embed = discord.Embed(color=0x1ABC9C)
                embed.set_image(url="attachment://dua.png")
                embed.set_footer(text="﴿ ادْعُونِي أَسْتَجِبْ لَكُمْ ﴾ • MuslimBot")
                view = AyahHadithView(interaction.user.id, "dua", dua_id, content, metadata)
                await interaction.response.send_message(embed=embed, file=file, view=view)
                return
        except Exception:
            pass

        # Fallback to text
        embed = discord.Embed(
            title="🤲 دعاء",
            description=f"```\n{d['text']}\n```",
            color=0x1ABC9C,
        )
        embed.set_thumbnail(url=DUA_ICON)
        embed.add_field(name="المصدر", value=d["source"], inline=False)
        embed.set_footer(text="﴿ ادْعُونِي أَسْتَجِبْ لَكُمْ ﴾ • MuslimBot")
        view = AyahHadithView(interaction.user.id, "dua", dua_id, content, metadata)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="hadith-list", description="📚 عرض قائمة الأحاديث الصحيحة")
    async def hadith_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        hadiths = get_hadith_list()
        chunks = self._chunk_text_hadith(hadiths)
        
        view = PaginationView(chunks, "📚 قائمة الأحاديث الصحيحة", 0x8E44AD)
        await view.send(interaction)

    @app_commands.command(name="dua-list", description="🤲 عرض قائمة الأدعية")
    async def dua_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        duas = get_dua_list()
        chunks = self._chunk_text_dua(duas)
        
        view = PaginationView(chunks, "🤲 قائمة الأدعية", 0x27AE60)
        await view.send(interaction)

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

    @app_commands.command(name="azkar-count", description="🔢 عداد ذكر شخصي تفاعلي")
    async def azkar_count(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id
        count = get_counter(user_id)
        view = AzkarCounterView(user_id, count)
        await view.send(interaction)

    @app_commands.command(name="favorites", description="⭐ عرض المفضلة المحفوظة")
    @app_commands.describe(type="نوع المفضلة: all, ayah, hadith, dua")
    async def show_favorites(self, interaction: discord.Interaction, type: str = "all"):
        await interaction.response.defer()
        
        favorites = get_favorites(interaction.user.id, type if type != "all" else None)
        
        if not favorites:
            embed = discord.Embed(
                title="⭐ المفضلة",
                description="لم تحفظ أي عناصر بعد",
                color=0xF39C12,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="استخدم الأزرار لحفظ الآيات والأحاديث • MuslimBot")
            await interaction.followup.send(embed=embed)
            return
        
        # Format favorites
        lines = []
        for i, fav in enumerate(favorites, 1):
            type_emoji = {"ayah": "📖", "hadith": "📚", "dua": "🤲"}.get(fav["type"], "📌")
            content = fav["content"][:100] + "..." if len(fav["content"]) > 100 else fav["content"]
            lines.append(f"{type_emoji} **{i}.** {content}")
        
        text = "\n".join(lines)
        chunks = self._chunk_text(text, 4000)
        
        if len(chunks) > 1:
            view = PaginationView(chunks, "⭐ المفضلة المحفوظة", 0xF39C12)
            await view.send(interaction)
        else:
            embed = discord.Embed(
                title="⭐ المفضلة المحفوظة",
                description=text,
                color=0xF39C12,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text=f"المجموع: {len(favorites)} • MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="clear-favorites", description="🗑️ مسح جميع المفضلة")
    async def clear_favorites_cmd(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        success = clear_favorites(interaction.user.id)
        
        if success:
            embed = discord.Embed(
                title="✅ تم مسح المفضلة",
                description="تم مسح جميع العناصر المحفوظة",
                color=0x27AE60,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="ℹ️ المفضلة فارغة",
                description="لا توجد عناصر لمسحها",
                color=0x3498DB,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="search-favorites", description="🔍 البحث في المفضلة المحفوظة")
    @app_commands.describe(keyword="الكلمة المراد البحث عنها")
    async def search_favorites_cmd(self, interaction: discord.Interaction, keyword: str):
        await interaction.response.defer()
        
        results = search_favorites(interaction.user.id, keyword)
        
        if not results:
            embed = discord.Embed(
                title="🔍 نتائج البحث",
                description=f"لم يتم العثور على نتائج لـ: **{keyword}**",
                color=0xF39C12,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text="المفضلة • MuslimBot")
            await interaction.followup.send(embed=embed)
            return
        
        # Format results
        lines = []
        for i, fav in enumerate(results, 1):
            type_emoji = {"ayah": "📖", "hadith": "📚", "dua": "🤲"}.get(fav["type"], "📌")
            content = fav["content"][:100] + "..." if len(fav["content"]) > 100 else fav["content"]
            lines.append(f"{type_emoji} **{i}.** {content}")
        
        text = "\n".join(lines)
        chunks = self._chunk_text(text, 4000)
        
        if len(chunks) > 1:
            view = PaginationView(chunks, f"🔍 نتائج البحث: {keyword}", 0xF39C12)
            await view.send(interaction)
        else:
            embed = discord.Embed(
                title=f"🔍 نتائج البحث: {keyword}",
                description=text,
                color=0xF39C12,
            )
            embed.set_thumbnail(url=BOOK_ICON)
            embed.set_footer(text=f"المجموع: {len(results)} • MuslimBot")
            await interaction.followup.send(embed=embed)

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
