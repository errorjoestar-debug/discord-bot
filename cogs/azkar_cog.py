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


class AzkarCog(commands.Cog, name="الأذكار"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="أذكار-الصباح", description="عرض أذكار الصباح")
    async def morning_azkar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        azkar = get_morning_azkar()
        text = format_azkar(azkar, "أذكار الصباح ☀️")

        for chunk in self._chunk_text(text, 4096):
            embed = discord.Embed(description=chunk, color=discord.Color.orange())
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="أذكار-المساء", description="عرض أذكار المساء")
    async def evening_azkar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        azkar = get_evening_azkar()
        text = format_azkar(azkar, "أذكار المساء 🌇")

        for chunk in self._chunk_text(text, 4096):
            embed = discord.Embed(description=chunk, color=discord.Color.purple())
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="أذكار-النوم", description="عرض أذكار النوم")
    async def sleep_azkar(self, interaction: discord.Interaction):
        await interaction.response.defer()
        azkar = get_sleep_azkar()
        text = format_azkar(azkar, "أذكار النوم 🌙")

        for chunk in self._chunk_text(text, 4096):
            embed = discord.Embed(description=chunk, color=discord.Color.dark_blue())
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="حديث", description="حديث شريف عشوائي")
    async def hadith(self, interaction: discord.Interaction):
        h = get_random_hadith()
        embed = discord.Embed(
            title="📖 حديث شريف",
            description=h["text"],
            color=discord.Color.green(),
        )
        embed.set_footer(text=f"الراوي: {h['narrator']} | المصدر: {h['source']}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="دعاء", description="دعاء عشوائي من القرآن")
    async def dua(self, interaction: discord.Interaction):
        d = get_random_dua()
        embed = discord.Embed(
            title="🤲 دعاء",
            description=d["text"],
            color=discord.Color.teal(),
        )
        embed.set_footer(text=f"المصدر: {d['source']}")
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
