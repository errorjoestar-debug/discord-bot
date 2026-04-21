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
    PRAYER_COLORS,
)
from utils.server_settings import get_server_city

MOSQUE_ICON = "https://cdn-icons-png.flaticon.com/512/2382/2382006.png"
CALENDAR_ICON = "https://cdn-icons-png.flaticon.com/512/3658/3658802.png"


class PrayerCog(commands.Cog, name="أوقات الصلاة"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="salah", description="🕌 عرض أوقات الصلاة الخمس لمدينة معينة")
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

        city, country, method = self._resolve_location(interaction, city, country, method)

        timings = await get_prayer_times(city, country, method)
        if not timings:
            embed = discord.Embed(
                title="❌ تعذّر جلب أوقات الصلاة",
                description="تأكّد من صِحّة اسم المدينة وكود الدولة وحاول مرّة أخرى",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        formatted = format_prayer_times(timings)
        next_prayer = get_next_prayer(timings)
        tz = timings.get("_timezone", "UTC")

        embed = discord.Embed(
            title="�️ أوقات الصلاة",
            description=f"📍 **{city}**، {country}\n🕐 التوقيت: {tz}\n\n{formatted}",
            color=0x1ABC9C,
        )
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2382/2382006.png")

        if next_prayer:
            name, remaining, actual_time = next_prayer
            ar_name = PRAYER_NAMES_AR.get(name, name)
            emoji = PRAYER_EMOJIS.get(name, "⏰")
            color = PRAYER_COLORS.get(name, 0xF1C40F)
            embed.color = color
            embed.add_field(
                name=f"{emoji} الصلاة القادمة",
                value=f"**{ar_name}** ─ {actual_time} ─ بعد **{remaining}**",
                inline=False,
            )

        embed.set_footer(text="﴿ إِنَّ ٱلصَّلَوٰةَ كَانَتْ عَلَى ٱلْمُؤْمِنِينَ كِتَـٰبًا مَّوْقُوتًا ﴾")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="hijri", description="📅 عرض التاريخ الهجري مع تفاصيل اليوم والشهر")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def hijri(
        self,
        interaction: discord.Interaction,
        city: str | None = None,
        country: str | None = None,
        method: int | None = None,
    ):
        await interaction.response.defer()

        city, country, method = self._resolve_location(interaction, city, country, method)

        hijri = await get_hijri_date(city, country, method)
        if not hijri:
            embed = discord.Embed(
                title="❌ تعذّر جلب التاريخ الهجري",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        date_str = hijri.get("date", "غير متوفر")
        day = hijri.get("day", "")
        month = hijri.get("month", {})
        month_ar = month.get("ar", "")
        month_en = month.get("en", "")
        year = hijri.get("year", "")
        designation = hijri.get("designation", {}).get("abbrev", "")
        weekday = hijri.get("weekday", {}).get("ar", "")

        embed = discord.Embed(
            title="📅 التاريخ الهجري",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=CALENDAR_ICON)
        embed.add_field(
            name="📆 التاريخ",
            value=f"**{day} {month_ar} {year} {designation}**",
            inline=False,
        )
        embed.add_field(
            name="📝 بالإنجليزي",
            value=f"{day} {month_en} {year}",
            inline=True,
        )
        embed.add_field(
            name="🗓️ اليوم",
            value=weekday or "—",
            inline=True,
        )
        embed.add_field(
            name="📋 كامل",
            value=f"`{date_str}`",
            inline=False,
        )
        embed.set_footer(text="﴿ وَتَعَـٰوَنُوا عَلَى ٱلْبِرِّ وَٱلتَّقْوَىٰ ﴾")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="athan", description="⏰ عرض الصلاة القادمة مع الوقت المتبقّي")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def next_prayer(
        self,
        interaction: discord.Interaction,
        city: str | None = None,
        country: str | None = None,
        method: int | None = None,
    ):
        await interaction.response.defer()

        city, country, method = self._resolve_location(interaction, city, country, method)

        timings = await get_prayer_times(city, country, method)
        if not timings:
            embed = discord.Embed(
                title="❌ تعذّر جلب أوقات الصلاة",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        next_p = get_next_prayer(timings)
        if next_p:
            name, remaining, actual_time = next_p
            ar_name = PRAYER_NAMES_AR.get(name, name)
            emoji = PRAYER_EMOJIS.get(name, "⏰")
            color = PRAYER_COLORS.get(name, 0xF1C40F)
            embed = discord.Embed(
                title=f"{emoji} الصلاة القادمة: {ar_name}",
                description=f"🕐 وقت الأذان: **{actual_time}**\n⏳ متبقّي **{remaining}** على صلاة **{ar_name}**\n📍 **{city}**، {country}",
                color=color,
            )
            embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/2382/2382006.png")
            embed.set_footer(text="حيّ على الصلاة ─ حيّ على الفلاح")
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🌙 انتهت أوقات صلاة اليوم",
                description="بارك الله فيكم! غدًا إن شاء الله سيتم عرض الأوقات",
                color=0x2C3E50,
            )
            embed.set_thumbnail(url=MOSQUE_ICON)
            await interaction.followup.send(embed=embed)

    def _resolve_location(self, interaction, city, country, method):
        if not city and interaction.guild_id:
            saved = get_server_city(interaction.guild_id)
            if saved:
                city = city or saved[0]
                country = country or saved[1]
                if method is None:
                    method = saved[2]
        city = city or os.getenv("PRAYER_CITY", "Cairo")
        country = country or os.getenv("PRAYER_COUNTRY", "EG")
        if method is None:
            method = int(os.getenv("PRAYER_METHOD", "5"))
        return city, country, method


async def setup(bot: commands.Bot):
    await bot.add_cog(PrayerCog(bot))
