import os
import discord
from discord import app_commands
from discord.ext import commands

from utils.prayer_times import (
    get_prayer_times,
    get_hijri_date,
    format_prayer_times,
    get_next_prayer,
    PRAYER_NAMES_AR,
    PRAYER_EMOJIS,
)


class PrayerCog(commands.Cog, name="أوقات الصلاة"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="salah", description="🕌 عرض أوقات الصلاة لمدينة معينة")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
        method="رقم طريقة الحساب (افتراضي 5)",
    )
    async def prayer(
        self,
        interaction: discord.Interaction,
        city: str | None = None,
        country: str | None = None,
        method: int | None = None,
    ):
        await interaction.response.defer()

        city = city or os.getenv("PRAYER_CITY", "Cairo")
        country = country or os.getenv("PRAYER_COUNTRY", "EG")

        timings = await get_prayer_times(city, country, method)
        if not timings:
            await interaction.followup.send("❌ حدث خطأ في جلب أوقات الصلاة. تأكد من اسم المدينة.")
            return

        formatted = format_prayer_times(timings)
        next_prayer = get_next_prayer(timings)

        embed = discord.Embed(
            title=f"🕌 أوقات الصلاة - {city}",
            description=formatted,
            color=discord.Color.green(),
        )

        if next_prayer:
            name, remaining = next_prayer
            ar_name = PRAYER_NAMES_AR.get(name, name)
            emoji = PRAYER_EMOJIS.get(name, "⏰")
            embed.set_footer(text=f"{emoji} الصلاة القادمة: {ar_name} - بعد {remaining}")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hijri", description="📅 عرض التاريخ الهجري")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def hijri(
        self,
        interaction: discord.Interaction,
        city: str | None = None,
        country: str | None = None,
    ):
        await interaction.response.defer()

        city = city or os.getenv("PRAYER_CITY", "Cairo")
        country = country or os.getenv("PRAYER_COUNTRY", "EG")

        hijri = await get_hijri_date(city, country)
        if not hijri:
            await interaction.followup.send("❌ حدث خطأ في جلب التاريخ الهجري.")
            return

        date_str = hijri.get("date", "غير متوفر")
        day = hijri.get("day", "")
        month = hijri.get("month", {})
        month_ar = month.get("ar", "")
        year = hijri.get("year", "")
        designation = hijri.get("designation", {}).get("abbrev", "")

        embed = discord.Embed(
            title="📅 التاريخ الهجري",
            color=discord.Color.blue(),
        )
        embed.add_field(name="التاريخ", value=f"{day} {month_ar} {year} {designation}", inline=False)
        embed.add_field(name="كامل", value=date_str, inline=False)

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="athan", description="⏰ تنبيه بالصلاة القادمة")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def next_prayer(
        self,
        interaction: discord.Interaction,
        city: str | None = None,
        country: str | None = None,
    ):
        await interaction.response.defer()

        city = city or os.getenv("PRAYER_CITY", "Cairo")
        country = country or os.getenv("PRAYER_COUNTRY", "EG")

        timings = await get_prayer_times(city, country)
        if not timings:
            await interaction.followup.send("❌ حدث خطأ في جلب أوقات الصلاة.")
            return

        next_p = get_next_prayer(timings)
        if next_p:
            name, remaining = next_p
            ar_name = PRAYER_NAMES_AR.get(name, name)
            emoji = PRAYER_EMOJIS.get(name, "⏰")
            embed = discord.Embed(
                title=f"{emoji} الصلاة القادمة: {ar_name}",
                description=f"متبقي **{remaining}** على صلاة {ar_name}",
                color=discord.Color.gold(),
            )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("🌙 انتهت أوقات صلاة اليوم. بارك الله فيكم!")


async def setup(bot: commands.Bot):
    await bot.add_cog(PrayerCog(bot))
