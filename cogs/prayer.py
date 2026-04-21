import os
import discord
from discord import app_commands
from discord.ext import commands

from utils.prayer_times import (
    get_prayer_times,
    get_hijri_date,
    format_prayer_times,
    get_next_prayer,
    get_sun_times,
    PRAYER_NAMES_AR,
    PRAYER_EMOJIS,
    PRAYER_COLORS,
)
from utils.server_settings import get_server_city
from utils.zakah import calculate_zakah
from utils.qibla import get_qibla_direction

MOSQUE_ICON = "https://images.unsplash.com/photo-1564769625688-478c7a3c38b6?w=800&q=80"
CALENDAR_ICON = "https://images.unsplash.com/photo-1506784365847-bbad939e9335?w=800&q=80"


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
            title="🕌 أوقات الصلاة",
            description=f"📍 **{city}**، {country}\n🕐 التوقيت: {tz}\n\n{formatted}",
            color=0x00B894,
        )
        embed.set_thumbnail(url=MOSQUE_ICON)

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

        embed.set_footer(text="﴿ إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَّوْقُوتًا ﴾ • MuslimBot")

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
        embed.set_footer(text="﴿ وَتَعَاوَنُوا عَلَى الْبِرِّ وَالتَّقْوَى ﴾ • MuslimBot")

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
            embed.set_thumbnail(url=MOSQUE_ICON)
            embed.set_footer(text="حيّ على الصلاة ─ حيّ على الفلاح • MuslimBot")
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title="🌙 انتهت أوقات صلاة اليوم",
                description="بارك الله فيكم! غدًا إن شاء الله سيتم عرض الأوقات",
                color=0x2C3E50,
            )
            embed.set_thumbnail(url=MOSQUE_ICON)
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="sunrise-sunset", description="🌅 عرض أوقات شروق وغروب الشمس")
    @app_commands.describe(
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def sunrise_sunset(
        self,
        interaction: discord.Interaction,
        city: str | None = None,
        country: str | None = None,
    ):
        await interaction.response.defer()

        city, country, method = self._resolve_location(interaction, city, country, None)

        sun_times = await get_sun_times(city, country, method)
        if not sun_times:
            embed = discord.Embed(
                title="❌ خطأ في جلب أوقات الشمس",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="🌅 أوقات الشمس",
            description=f"📍 **{city}**، {country}\n🕐 التوقيت: {sun_times['timezone']}",
            color=0xF39C12,
        )
        embed.set_thumbnail(url=CALENDAR_ICON)
        embed.add_field(
            name="🌅 شروق الشمس",
            value=f"**{sun_times['sunrise']}**",
            inline=True,
        )
        embed.add_field(
            name="🌇 غروب الشمس",
            value=f"**{sun_times['sunset']}**",
            inline=True,
        )
        embed.add_field(
            name="☀️ منتصف النهار",
            value=f"**{sun_times['midday']}**",
            inline=True,
        )
        embed.set_footer(text="﴿ وَسَخَّرَ لَكُمُ الشَّمْسَ وَالْقَمَرَ دَائِبَيْنِ ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="date-convert", description="📅 تحويل التاريخ (ميلادي ↔ هجري)")
    @app_commands.describe(
        date="التاريخ (مثال: 2024-01-15) أو اتركه فارغاً لليوم",
        city="اسم المدينة (مثال: Cairo)",
        country="كود الدولة (مثال: EG)",
    )
    async def date_convert(
        self,
        interaction: discord.Interaction,
        date: str | None = None,
        city: str | None = None,
        country: str | None = None,
    ):
        await interaction.response.defer()

        city, country, method = self._resolve_location(interaction, city, country, None)

        hijri = await get_hijri_date(city, country, method)
        if not hijri:
            embed = discord.Embed(
                title="❌ خطأ في جلب التاريخ الهجري",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        hijri_date = hijri.get("date", "")
        hijri_month = hijri.get("month", {})
        hijri_day = hijri.get("day", 1)

        embed = discord.Embed(
            title="📅 تحويل التاريخ",
            description=f"📍 **{city}**، {country}",
            color=0x9B59B6,
        )
        embed.set_thumbnail(url=CALENDAR_ICON)
        embed.add_field(
            name="🌙 التاريخ الهجري",
            value=f"**{hijri_date}**\n{hijri_month.get('en', '')} - {hijri_month.get('ar', '')}",
            inline=True,
        )
        embed.add_field(
            name="📅 اليوم",
            value=f"**اليوم {hijri_day}** من شهر {hijri_month.get('ar', '')}",
            inline=True,
        )
        embed.add_field(
            name="📋 المعلومات",
            value=f"الأيام في الشهر: {hijri_month.get('number', '')}",
            inline=False,
        )
        embed.set_footer(text="﴿ إِنَّ عِدَّةَ الشُّهُورِ عِندَ اللَّهِ اثْنَا عَشَرَ شَهْرًا ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="zakah", description="💰 حساب الزكاة")
    @app_commands.describe(
        amount="المبلغ (بالدولار)",
        type="النوع: gold, silver, cash",
    )
    async def zakah(
        self,
        interaction: discord.Interaction,
        amount: float,
        type: str = "cash",
    ):
        result = calculate_zakah(amount, type)
        
        if "error" in result:
            embed = discord.Embed(
                title="❌ خطأ في حساب الزكاة",
                description=result["error"],
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if result["eligible"]:
            embed = discord.Embed(
                title="💰 حساب الزكاة",
                description=f"المبلغ: **${amount:,.2f}**\nالنوع: **{type}**",
                color=0x27AE60,
            )
            embed.add_field(
                name="📊 النصاب",
                value=f"**${result['nisab_value']:,.2f}**",
                inline=True,
            )
            embed.add_field(
                name="💵 الزكاة المستحقة",
                value=f"**${result['zakah_amount']:,.2f}** ({result['zakah_rate']})",
                inline=True,
            )
            embed.add_field(
                name="✅ الحالة",
                value="مستحق للزكاة",
                inline=False,
            )
            embed.set_footer(text="﴿ خُذْ مِنْ أَمْوَالِهِمْ صَدَقَةً تُطَهِّرُهُمْ وَتُزَكِّيهِم بِهَا ﴾ • MuslimBot")
        else:
            embed = discord.Embed(
                title="💰 حساب الزكاة",
                description=f"المبلغ: **${amount:,.2f}**\nالنوع: **{type}**",
                color=0xF39C12,
            )
            embed.add_field(
                name="📊 النصاب",
                value=f"**${result['nisab_value']:,.2f}**",
                inline=True,
            )
            embed.add_field(
                name="💵 الزكاة المستحقة",
                value="**$0.00**",
                inline=True,
            )
            embed.add_field(
                name="⚠️ الحالة",
                value="لم يبلغ النصاب بعد",
                inline=False,
            )
            embed.set_footer(text="﴿ خُذْ مِنْ أَمْوَالِهِمْ صَدَقَةً تُطَهِّرُهُمْ وَتُزَكِّيهِم بِهَا ﴾ • MuslimBot")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="qibla", description="🕋 عرض اتجاه القبلة")
    @app_commands.describe(city="اسم المدينة (مثال: Cairo, Riyadh, Dubai)")
    async def qibla(
        self,
        interaction: discord.Interaction,
        city: str = "Cairo",
    ):
        await interaction.response.defer()

        qibla = await get_qibla_direction(city)
        if not qibla:
            embed = discord.Embed(
                title="❌ خطأ في جلب اتجاه القبلة",
                description="حاول مرّة أخرى لاحقًا أو استخدم مدينة أخرى",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        direction = qibla["direction"]
        direction_text = f"**{direction}°** من الشمال (باتجاه عقارب الساعة)"

        embed = discord.Embed(
            title="🕋 اتجاه القبلة",
            description=f"📍 **{qibla['city']}**",
            color=0x8E44AD,
        )
        embed.set_thumbnail(url=MOSQUE_ICON)
        embed.add_field(
            name="🧭 الاتجاه",
            value=direction_text,
            inline=True,
        )
        embed.add_field(
            name="📍 الإحداثيات",
            value=f"Lat: {qibla['latitude']}\nLng: {qibla['longitude']}",
            inline=True,
        )
        embed.add_field(
            name="📖 تذكير",
            value="﴿ فَوَلِّ وَجْهَكَ شَطْرَ الْمَسْجِدِ الْحَرَامِ ﴾",
            inline=False,
        )
        embed.set_footer(text="﴿ وَمِنْ حَيْثُ خَرَجْتَ فَوَلِّ وَجْهَكَ شَطْرَ الْمَسْجِدِ الْحَرَامِ ﴾ • MuslimBot")
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
