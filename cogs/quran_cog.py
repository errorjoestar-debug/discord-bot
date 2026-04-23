import io
import discord
from discord import app_commands
from discord.ext import commands

from utils.quran import get_random_verse, get_verse, get_surah, search_quran, get_surah_list
from utils.quran_image import create_ayah_image
from utils.views import SurahSelectView

QURAN_ICON = "https://images.unsplash.com/photo-1576413329366-5b2c6e0463e4?w=800&q=80"

# Surah names for autocomplete
SURAH_NAMES = {
    1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
    6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
    11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
    16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
    21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
    26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
    31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
    36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
    41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
    46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
    51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
    56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
    61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
    66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
    71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
    76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
    81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
    86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
    91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
    96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
    101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
    106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
    111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس",
}


class QuranCog(commands.Cog, name="القرآن"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def surah_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice]:
        """Autocomplete for surah number."""
        choices = []
        for num, name in SURAH_NAMES.items():
            label = f"{num} - {name}"
            if not current or current in str(num) or current in name:
                choices.append(app_commands.Choice(name=label, value=num))
        return choices[:25]

    async def _send_ayah(self, interaction: discord.Interaction, verse: dict):
        """Send an ayah as image with text fallback."""
        try:
            image_bytes = await create_ayah_image(
                verse['text'],
                verse['surah_name'],
                verse['ayah_number'],
                verse['surah_number']
            )
            if image_bytes:
                file = discord.File(io.BytesIO(image_bytes), filename="ayah.png")
                embed = discord.Embed(title="📖 آية قرآنية", color=0x0984E3)
                embed.add_field(name="📍 السورة", value=f"**{verse['surah_name']}** ({verse['surah_english']})", inline=True)
                embed.add_field(name="🔢 رقم الآية", value=str(verse["ayah_number"]), inline=True)
                embed.set_image(url="attachment://ayah.png")
                embed.set_footer(text="﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾ • MuslimBot")
                await interaction.followup.send(embed=embed, file=file)
                return
        except Exception:
            pass
        # Fallback to text
        embed = discord.Embed(title="📖 آية قرآنية", description=f"\n{verse['text']}\n", color=0x0984E3)
        embed.set_thumbnail(url=QURAN_ICON)
        embed.add_field(name="📍 السورة", value=f"**{verse['surah_name']}** ({verse['surah_english']})", inline=True)
        embed.add_field(name="🔢 رقم الآية", value=str(verse["ayah_number"]), inline=True)
        embed.set_footer(text="﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ayah", description="📖 آية قرآنية عشوائية من القرآن الكريم")
    async def random_verse(self, interaction: discord.Interaction):
        await interaction.response.defer()
        verse = await get_random_verse()
        if not verse:
            embed = discord.Embed(title="❌ خطأ في جلب الآية", description="حاول مرّة أخرى لاحقًا", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return
        await self._send_ayah(interaction, verse)

    @app_commands.command(name="surah-ayah", description="📖 عرض آية محددة من سورة معيّنة")
    @app_commands.describe(surah="رقم السورة (1-114)", ayah="رقم الآية")
    @app_commands.autocomplete(surah=surah_autocomplete)
    async def specific_verse(self, interaction: discord.Interaction, surah: int, ayah: int):
        await interaction.response.defer()
        if surah < 1 or surah > 114:
            embed = discord.Embed(title="❌ رقم سورة غير صحيح", description="رقم السورة يجب أن يكون بين 1 و 114", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return
        verse = await get_verse(surah, ayah)
        if not verse:
            embed = discord.Embed(title="❌ خطأ في جلب الآية", description="تأكّد من صِحّة رقم السورة والآية", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return
        await self._send_ayah(interaction, verse)

    @app_commands.command(name="surah", description="📖 عرض سورة كاملة من القرآن الكريم")
    @app_commands.describe(surah="رقم السورة (1-114)")
    @app_commands.autocomplete(surah=surah_autocomplete)
    async def surah(self, interaction: discord.Interaction, surah: int):
        await interaction.response.defer()
        if surah < 1 or surah > 114:
            embed = discord.Embed(title="❌ رقم سورة غير صحيح", description="رقم السورة يجب أن يكون بين 1 و 114", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return

        surah_data = await get_surah(surah)
        if not surah_data:
            embed = discord.Embed(title="❌ خطأ في جلب السورة", description="تأكّد من صِحّة رقم السورة", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return

        ayahs_text = "\n".join([f"**{a['number']}.** {a['text']}" for a in surah_data["ayahs"]])
        chunks = self._chunk_text(ayahs_text, 4000)

        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📖 سورة {surah_data['name']} ({surah_data['englishName']})",
                description=chunk, color=0x0984E3,
            )
            embed.set_thumbnail(url=QURAN_ICON)
            embed.add_field(
                name="📊 معلومات",
                value=f"**المعنى:** {surah_data['englishNameTranslation']}\n**نوع الوحي:** {surah_data['revelationType']}\n**عدد الآيات:** {surah_data['numberOfAyahs']}",
                inline=False,
            )
            footer_base = "﴿ وَاتْلُ مَا أُوحِيَ إِلَيْكَ مِنَ الْكِتَابِ ﴾ • MuslimBot"
            embed.set_footer(text=f"الجزء {i+1}/{len(chunks)} ─ {footer_base}" if len(chunks) > 1 else footer_base)
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="search-quran", description="🔍 البحث في القرآن الكريم")
    @app_commands.describe(keyword="الكلمة المراد البحث عنها")
    async def search_quran_cmd(self, interaction: discord.Interaction, keyword: str):
        await interaction.response.defer()
        results = await search_quran(keyword)
        if not results:
            embed = discord.Embed(title="❌ لم يتم العثور على نتائج", description="حاول بكلمة أخرى", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(title=f"🔍 نتائج البحث عن: {keyword}", description=f"تم العثور على {len(results)} نتيجة", color=0x0984E3)
        embed.set_thumbnail(url=QURAN_ICON)
        for i, result in enumerate(results[:5], 1):
            embed.add_field(
                name=f"{i}. سورة {result['surah_name']} - آية {result['ayah_number']}",
                value=result['text'][:200] + "..." if len(result['text']) > 200 else result['text'],
                inline=False,
            )
        embed.set_footer(text="﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="quran-list", description="📚 عرض جميع سور القرآن الكريم")
    async def quran_list(self, interaction: discord.Interaction):
        await interaction.response.defer()
        surahs = await get_surah_list()
        if not surahs:
            embed = discord.Embed(title="❌ خطأ في جلب قائمة السور", description="حاول مرّة أخرى لاحقًا", color=0xE74C3C)
            await interaction.followup.send(embed=embed)
            return

        chunks = []
        current_chunk = []
        for i, s in enumerate(surahs, 1):
            current_chunk.append(f"**{i}.** {s['name']} ({s['englishName']}) - {s['numberOfAyahs']} آية")
            if len(current_chunk) == 25:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            chunks.append(current_chunk)

        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="📚 سور القرآن الكريم" if i == 0 else None,
                description="\n".join(chunk), color=0x0984E3,
            )
            embed.set_thumbnail(url=QURAN_ICON)
            embed.set_footer(text=f"الجزء {i+1}/{len(chunks)} • MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="surah-select", description="📖 اختيار سورة من قائمة منسدلة")
    async def surah_select(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Create select options (Discord limit is 25)
        options = []
        for num, name in list(SURAH_NAMES.items())[:25]:
            options.append(
                discord.SelectOption(
                    label=f"{num} - {name}",
                    value=str(num)
                )
            )
        
        view = SurahSelectView(self._handle_surah_select)
        select = view.children[0]
        select.options = options
        
        embed = discord.Embed(
            title="📖 اختر سورة",
            description="اختر سورة من القائمة لعرضها\n(ملاحظة: القائمة تعرض أول 25 سورة. للسور الأخرى استخدم `/surah` مع رقم السورة)",
            color=0x0984E3,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        embed.set_footer(text="القرآن الكريم • MuslimBot")
        
        await interaction.followup.send(embed=embed, view=view)
    
    async def _handle_surah_select(self, interaction: discord.Interaction, surah_num: int):
        """Handle surah selection from dropdown."""
        await interaction.response.defer()
        
        surah_data = await get_surah(surah_num)
        if not surah_data:
            embed = discord.Embed(
                title="❌ خطأ في جلب السورة",
                description="تأكّد من صِحّة رقم السورة",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        ayahs_text = "\n".join([f"**{a['number']}.** {a['text']}" for a in surah_data["ayahs"]])
        chunks = self._chunk_text(ayahs_text, 4000)

        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📖 سورة {surah_data['name']} ({surah_data['englishName']})",
                description=chunk, color=0x0984E3,
            )
            embed.set_thumbnail(url=QURAN_ICON)
            embed.add_field(
                name="📊 معلومات",
                value=f"**المعنى:** {surah_data['englishNameTranslation']}\n**نوع الوحي:** {surah_data['revelationType']}\n**عدد الآيات:** {surah_data['numberOfAyahs']}",
                inline=False,
            )
            footer_base = "﴿ وَاتْلُ مَا أُوحِيَ إِلَيْكَ مِنَ الْكِتَابِ ﴾ • MuslimBot"
            embed.set_footer(text=f"الجزء {i+1}/{len(chunks)} ─ {footer_base}" if len(chunks) > 1 else footer_base)
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
    await bot.add_cog(QuranCog(bot))

