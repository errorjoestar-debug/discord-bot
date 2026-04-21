import os
import discord
from discord import app_commands
from discord.ext import commands

from utils.server_settings import set_server_city, get_server_city

GEAR_ICON = "https://cdn-icons-png.flaticon.com/512/1269/1269202.png"

METHODS = {
    1: "University of Islamic Sciences, Karachi",
    2: "Islamic Society of North America",
    3: "Muslim World League",
    4: "Umm Al-Qura University, Makkah",
    5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran",
    8: "Gulf Region",
    9: "Kuwait",
    10: "Qatar",
    11: "Majlis Ugama Islam Singapura",
    12: "UOIF (France)",
    13: "Diyanet İşleri Başkanlığı (Turkey)",
    14: "Spiritual Administration of Muslims of Russia",
}


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
            embed = discord.Embed(
                title="❌ ده مخصص للسيرفرات بس",
                color=0xE74C3C,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        set_server_city(interaction.guild_id, city, country, method)
        method_name = METHODS.get(method, "غير معروف")

        embed = discord.Embed(
            title="✅ تم حفظ إعدادات المدينة",
            color=0x27AE60,
        )
        embed.set_thumbnail(url=GEAR_ICON)
        embed.add_field(name="🏙️ المدينة", value=f"**{city}**", inline=True)
        embed.add_field(name="🌍 الدولة", value=f"**{country}**", inline=True)
        embed.add_field(name="📐 طريقة الحساب", value=f"**{method}** ─ {method_name}", inline=False)
        embed.set_footer(text="دلوقتي أوامر الصلاة هتستخدم المدينة دي تلقائياً")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="settings", description="⚙️ عرض إعدادات السيرفر")
    async def show_settings(self, interaction: discord.Interaction):
        if not interaction.guild_id:
            embed = discord.Embed(
                title="❌ ده مخصص للسيرفرات بس",
                color=0xE74C3C,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        result = get_server_city(interaction.guild_id)
        if result:
            city, country, method = result
            method_name = METHODS.get(method, "غير معروف")
            embed = discord.Embed(
                title="⚙️ إعدادات السيرفر",
                color=0x3498DB,
            )
            embed.set_thumbnail(url=GEAR_ICON)
            embed.add_field(name="🏙️ المدينة", value=f"**{city}**", inline=True)
            embed.add_field(name="🌍 الدولة", value=f"**{country}**", inline=True)
            embed.add_field(name="📐 طريقة الحساب", value=f"**{method}** ─ {method_name}", inline=False)
        else:
            default_city = os.getenv("PRAYER_CITY", "Cairo")
            default_country = os.getenv("PRAYER_COUNTRY", "EG")
            embed = discord.Embed(
                title="⚙️ إعدادات السيرفر",
                description="لم يتم حفظ إعدادات بعد.\nاستخدم `/set-city` لحفظ مدينتك.",
                color=0xE67E22,
            )
            embed.set_thumbnail(url=GEAR_ICON)
            embed.add_field(
                name="📍 الافتراضي",
                value=f"**{default_city}**, {default_country}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(SettingsCog(bot))
