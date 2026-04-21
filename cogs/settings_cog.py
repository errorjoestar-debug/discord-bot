import os
import discord
from discord import app_commands
from discord.ext import commands

from utils.server_settings import set_server_city, get_server_city


class SettingsCog(commands.Cog, name="إعدادات السيرفر"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set-city", description="⚙️ حفظ مدينتك لأوقات الصلاة")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo, Dubai, Riyadh)",
        country="كود الدولة (مثال: EG, AE, SA)",
        method="رقم طريقة الحساب (افتراضي 5)",
    )
    async def set_city(
        self,
        interaction: discord.Interaction,
        city: str,
        country: str,
        method: int = 5,
    ):
        if not interaction.guild_id:
            await interaction.response.send_message("❌ ده مخصص للسيرفرات بس.", ephemeral=True)
            return

        set_server_city(interaction.guild_id, city, country, method)

        embed = discord.Embed(
            title="✅ تم حفظ إعدادات المدينة",
            description=f"المدينة: **{city}**\nالدولة: **{country}**\nطريقة الحساب: **{method}**",
            color=discord.Color.green(),
        )
        embed.set_footer(text="دلوقتي أوامر الصلاة هتستخدم المدينة دي تلقائياً")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="settings", description="⚙️ عرض إعدادات السيرفر")
    async def show_settings(self, interaction: discord.Interaction):
        if not interaction.guild_id:
            await interaction.response.send_message("❌ ده مخصص للسيرفرات بس.", ephemeral=True)
            return

        result = get_server_city(interaction.guild_id)
        if result:
            city, country, method = result
            embed = discord.Embed(
                title="⚙️ إعدادات السيرفر",
                description=f"المدينة: **{city}**\nالدولة: **{country}**\nطريقة الحساب: **{method}**",
                color=discord.Color.blue(),
            )
        else:
            embed = discord.Embed(
                title="⚙️ إعدادات السيرفر",
                description="لم يتم حفظ إعدادات بعد.\nاستخدم `/set-city` لحفظ مدينتك.",
                color=discord.Color.orange(),
            )
            embed.set_footer(text=f"الافتراضي: {os.getenv('PRAYER_CITY', 'Cairo')}, {os.getenv('PRAYER_COUNTRY', 'EG')}")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SettingsCog(bot))
