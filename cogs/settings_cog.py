import os
import discord
from discord import app_commands
from discord.ext import commands

from utils.server_settings import set_server_city, get_server_city
from utils.user_settings import set_user_reciter, get_user_reciter, set_user_city, get_user_city

GEAR_ICON = "https://images.unsplash.com/photo-1526694456423-8e8db921553c?w=800&q=80"

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

    @app_commands.command(name="set-city", description="⚙️ حفظ مدينتك لحساب أوقات الصلاة تلقائيًا")
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
            title="⚙️ تم حفظ الإعدادات",
            description=f"تم تعيين مدينة الصلاة إلى **{city}**، {country}\nطريقة الحساب: {method_name}",
            color=0x2ECC71,
        )
        embed.set_thumbnail(url=GEAR_ICON)
        embed.add_field(name="🏙️ المدينة", value=f"**{city}**", inline=True)
        embed.add_field(name="🌍 الدولة", value=f"**{country}**", inline=True)
        embed.add_field(name="📐 طريقة الحساب", value=f"**{method}** ─ {method_name}", inline=False)
        embed.set_footer(text="الآن أوامر الصلاة ستستخدم المدينة تلقائياً • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="settings", description="⚙️ عرض إعدادات السيرفر الحالية")
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
            settings_text = f"مدينة الصلاة: **{city}**، {country}\nطريقة الحساب: {method_name}"
            embed = discord.Embed(
                title="⚙️ إعدادات السيرفر",
                description=settings_text,
                color=0x3498DB,
            )
            embed.set_thumbnail(url=GEAR_ICON)
            embed.add_field(name="🏙️ المدينة", value=f"**{city}**", inline=True)
            embed.add_field(name="🌍 الدولة", value=f"**{country}**", inline=True)
            embed.add_field(name="📐 طريقة الحساب", value=f"**{method}** ─ {method_name}", inline=False)
            embed.set_footer(text="إعدادات السيرفر • MuslimBot")
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

    @app_commands.command(name="my-reciter", description="🎙️ تعيين القارئ المفضل الخاص بك")
    @app_commands.describe(reciter="معرف القارئ (مثال: ar.alafasy)")
    async def set_my_reciter(
        self,
        interaction: discord.Interaction,
        reciter: str,
    ):
        set_user_reciter(interaction.user.id, reciter)
        embed = discord.Embed(
            title="✅ تم حفظ القارئ المفضل",
            description=f"القارئ: **{reciter}**",
            color=0x2ECC71,
        )
        embed.set_thumbnail(url=GEAR_ICON)
        embed.set_footer(text="الإعدادات الشخصية • MuslimBot")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="my-city", description="🏙️ تعيين مدينتك الشخصية")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def set_my_city(
        self,
        interaction: discord.Interaction,
        city: str,
        country: str,
    ):
        set_user_city(interaction.user.id, city, country)
        embed = discord.Embed(
            title="✅ تم حفظ المدينة المفضلة",
            description=f"المدينة: **{city}**، {country}",
            color=0x2ECC71,
        )
        embed.set_thumbnail(url=GEAR_ICON)
        embed.set_footer(text="الإعدادات الشخصية • MuslimBot")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="my-settings", description="⚙️ عرض إعداداتك الشخصية")
    async def show_my_settings(self, interaction: discord.Interaction):
        reciter = get_user_reciter(interaction.user.id)
        city_country = get_user_city(interaction.user.id)
        
        embed = discord.Embed(
            title="⚙️ إعداداتك الشخصية",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=GEAR_ICON)
        
        if reciter:
            embed.add_field(name="🎙️ القارئ المفضل", value=f"`{reciter}`", inline=False)
        else:
            embed.add_field(name="🎙️ القارئ المفضل", value="لم يتم تعيين", inline=False)
        
        if city_country:
            embed.add_field(name="🏙️ المدينة المفضلة", value=f"**{city_country[0]}**، {city_country[1]}", inline=False)
        else:
            embed.add_field(name="🏙️ المدينة المفضلة", value="لم يتم تعيين", inline=False)
        
        embed.set_footer(text="الإعدادات الشخصية • MuslimBot")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SettingsCog(bot))
