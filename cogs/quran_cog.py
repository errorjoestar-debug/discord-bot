import discord
from discord import app_commands
from discord.ext import commands

from utils.quran import get_random_verse, get_verse

QURAN_ICON = "https://cdn-icons-png.flaticon.com/512/331/331008.png"


class QuranCog(commands.Cog, name="القرآن"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ayah", description="📖 آية قرآنية عشوائية")
    async def random_verse(self, interaction: discord.Interaction):
        await interaction.response.defer()

        verse = await get_random_verse()
        if not verse:
            embed = discord.Embed(
                title="❌ خطأ في جلب الآية",
                description="حاول مرة أخرى لاحقاً",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="📖 آية قرآنية",
            description=f"\n{verse['text']}\n",
            color=0x196F3D,
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
        embed.set_footer(text="﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="surah-ayah", description="📖 عرض آية محددة من سورة معينة")
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
                description="تأكد من رقم السورة والآية",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="📖 آية قرآنية",
            description=f"\n{verse['text']}\n",
            color=0x196F3D,
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
        embed.set_footer(text="﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ فَهَلْ مِن مُّدَّكِرٍ ﴾")
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranCog(bot))
