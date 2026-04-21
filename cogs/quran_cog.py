import discord
from discord import app_commands
from discord.ext import commands

from utils.quran import get_random_verse, get_verse


class QuranCog(commands.Cog, name="القرآن"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ayah", description="📖 آية قرآنية عشوائية")
    async def random_verse(self, interaction: discord.Interaction):
        await interaction.response.defer()

        verse = await get_random_verse()
        if not verse:
            await interaction.followup.send("❌ حدث خطأ في جلب الآية.")
            return

        embed = discord.Embed(
            title="📖 آية قرآنية",
            description=f"```\n{verse['text']}\n```",
            color=discord.Color.dark_green(),
        )
        embed.set_footer(
            text=f"سورة {verse['surah_name']} ({verse['surah_english']}) - الآية {verse['ayah_number']}"
        )
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
            await interaction.followup.send("❌ رقم السورة يجب أن يكون بين 1 و 114.")
            return

        verse = await get_verse(surah, ayah)
        if not verse:
            await interaction.followup.send("❌ حدث خطأ. تأكد من رقم السورة والآية.")
            return

        embed = discord.Embed(
            title="📖 آية قرآنية",
            description=f"```\n{verse['text']}\n```",
            color=discord.Color.dark_green(),
        )
        embed.set_footer(
            text=f"سورة {verse['surah_name']} ({verse['surah_english']}) - الآية {verse['ayah_number']}"
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranCog(bot))
