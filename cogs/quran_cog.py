import discord
from discord import app_commands
from discord.ext import commands

from utils.quran import get_random_verse, get_verse, get_surah, search_quran, get_surah_list

QURAN_ICON = "https://images.unsplash.com/photo-1576413329366-5b2c6e0463e4?w=800&q=80"


class QuranCog(commands.Cog, name="القرآن"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ayah", description="📖 آية قرآنية عشوائية من القرآن الكريم")
    async def random_verse(self, interaction: discord.Interaction):
        await interaction.response.defer()

        verse = await get_random_verse()
        if not verse:
            embed = discord.Embed(
                title="❌ خطأ في جلب الآية",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="📖 آية قرآنية",
            description=f"\n{verse['text']}\n",
            color=0x0984E3,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        embed.add_field(
            name="📍 السورة",
            value=f"**{verse['surah_name']}** ({verse['surah_english']})",
            inline=True,
        )
        embed.add_field(
            name="🔢 رقم الآية",
            value=str(verse["ayah_number"]),
            inline=True,
        )
        embed.set_footer(text="﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="surah-ayah", description="📖 عرض آية محددة من سورة معيّنة")
    @app_commands.describe(surah="رقم السورة (1-114)", ayah="رقم الآية")
    async def specific_verse(
        self,
        interaction: discord.Interaction,
        surah: int,
        ayah: int,
    ):
        await interaction.response.defer()

        if surah < 1 or surah > 114:
            embed = discord.Embed(
                title="❌ رقم سورة غير صحيح",
                description="رقم السورة يجب أن يكون بين 1 و 114",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        verse = await get_verse(surah, ayah)
        if not verse:
            embed = discord.Embed(
                title="❌ خطأ في جلب الآية",
                description="تأكّد من صِحّة رقم السورة والآية",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="📖 آية قرآنية",
            description=f"\n{verse['text']}\n",
            color=0x0984E3,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        embed.add_field(
            name="📍 السورة",
            value=f"**{verse['surah_name']}** ({verse['surah_english']})",
            inline=True,
        )
        embed.add_field(
            name="🔢 رقم الآية",
            value=str(verse["ayah_number"]),
            inline=True,
        )
        embed.set_footer(text="﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِرٍ ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="surah", description="📖 عرض سورة كاملة من القرآن الكريم")
    @app_commands.describe(surah="رقم السورة (1-114)")
    async def surah(
        self,
        interaction: discord.Interaction,
        surah: int,
    ):
        await interaction.response.defer()

        if surah < 1 or surah > 114:
            embed = discord.Embed(
                title="❌ رقم سورة غير صحيح",
                description="رقم السورة يجب أن يكون بين 1 و 114",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        surah_data = await get_surah(surah)
        if not surah_data:
            embed = discord.Embed(
                title="❌ خطأ في جلب السورة",
                description="تأكّد من صِحّة رقم السورة",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        # Format ayahs text
        ayahs_text = "\n".join([f"**{a['number']}.** {a['text']}" for a in surah_data["ayahs"]])
        
        # Chunk if too long
        chunks = []
        current_chunk = ""
        for line in ayahs_text.split("\n"):
            if len(current_chunk) + len(line) + 1 > 4000:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk = f"{current_chunk}\n{line}" if current_chunk else line
        if current_chunk:
            chunks.append(current_chunk)

        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"📖 سورة {surah_data['name']} ({surah_data['englishName']})",
                description=chunk,
                color=0x0984E3,
            )
            embed.set_thumbnail(url=QURAN_ICON)
            embed.add_field(
                name="📊 معلومات",
                value=f"**المعنى بالإنجليزية:** {surah_data['englishNameTranslation']}\n**نوع الوحي:** {surah_data['revelationType']}\n**عدد الآيات:** {surah_data['numberOfAyahs']}",
                inline=False,
            )
            if len(chunks) > 1:
                embed.set_footer(text=f"الجزء {i+1} من {len(chunks)} ─ ﴿ وَاتْلُ مَا أُوحِيَ إِلَيْكَ مِنَ الْكِتَابِ ﴾ • MuslimBot")
            else:
                embed.set_footer(text="﴿ وَاتْلُ مَا أُوحِيَ إِلَيْكَ مِنَ الْكِتَابِ ﴾ • MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="search-quran", description="🔍 البحث في القرآن الكريم")
    @app_commands.describe(keyword="الكلمة المراد البحث عنها")
    async def search_quran_cmd(
        self,
        interaction: discord.Interaction,
        keyword: str,
    ):
        await interaction.response.defer()

        results = await search_quran(keyword)
        if not results:
            embed = discord.Embed(
                title="❌ لم يتم العثور على نتائج",
                description="حاول بكلمة أخرى",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"🔍 نتائج البحث عن: {keyword}",
            description=f"تم العثور على {len(results)} نتيجة",
            color=0x0984E3,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        
        for i, result in enumerate(results[:5], 1):  # Show first 5 results
            embed.add_field(
                name=f"{i}. سورة {result['surah_name']} - آية {result['ayah_number']}",
                value=result['text'][:200] + "..." if len(result['text']) > 200 else result['text'],
                inline=False,
            )
        
        if len(results) > 5:
            embed.set_footer(text=f"عرض أول 5 نتائج من {len(results)} ─ ﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ ﴾ • MuslimBot")
        else:
            embed.set_footer(text="﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ ﴾ • MuslimBot")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="quran-list", description="📚 عرض جميع سور القرآن الكريم")
    async def quran_list(self, interaction: discord.Interaction):
        await interaction.response.defer()

        surahs = await get_surah_list()
        if not surahs:
            embed = discord.Embed(
                title="❌ خطأ في جلب قائمة السور",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        # Group surahs in chunks of 25 (Discord limit)
        chunks = []
        current_chunk = []
        for i, surah in enumerate(surahs, 1):
            current_chunk.append(f"**{i}.** {surah['name']} ({surah['englishName']}) - {surah['numberOfAyahs']} آية")
            if len(current_chunk) == 25:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            chunks.append(current_chunk)

        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title="📚 سور القرآن الكريم" if i == 0 else None,
                description="\n".join(chunk),
                color=0x0984E3,
            )
            embed.set_thumbnail(url=QURAN_ICON)
            embed.set_footer(text=f"الجزء {i+1} من {len(chunks)} • MuslimBot")
            await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranCog(bot))
