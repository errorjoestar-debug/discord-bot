import os
import logging
from datetime import datetime, time, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.azkar import get_morning_azkar, get_evening_azkar, format_azkar
from utils.prayer_times import get_prayer_times, get_hijri_date
from utils.events import get_today_events

log = logging.getLogger(__name__)

MORNING_TIME = time(5, 30)
EVENING_TIME = time(16, 0)

MOSQUE_ICON = "https://cdn-icons-png.flaticon.com/512/331/331008.png"
BOOK_ICON = "https://cdn-icons-png.flaticon.com/512/201/201614.png"
CALENDAR_ICON = "https://cdn-icons-png.flaticon.com/512/2898/2898849.png"

AZKAR_CONFIG = {
    "morning": {
        "title": "☀️ أذكار الصباح",
        "color": 0xFF8C00,
        "footer": "لا تنسَ ذكر الله ☀️ ﴿ وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ طُلُوعِ الشَّمْسِ ﴾",
    },
    "evening": {
        "title": "🌇 أذكار المساء",
        "color": 0x7B68EE,
        "footer": "لا تنسَ ذكر الله 🌇 ﴿ وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ غُرُوبِ الشَّمْسِ ﴾",
    },
}


class AutoAzkarCog(commands.Cog, name="الأذكار التلقائية"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.azkar_channel_id: int | None = None
        self._load_channel()
        self.morning_sent = False
        self.evening_sent = False

    def _load_channel(self):
        channel_id = os.getenv("AZKAR_CHANNEL_ID", "")
        if channel_id:
            try:
                self.azkar_channel_id = int(channel_id)
            except ValueError:
                log.warning("Invalid AZKAR_CHANNEL_ID")

    @app_commands.command(name="azkar-on", description="🔔 تفعيل إرسال الأذكار تلقائياً في هذه القناة")
    async def enable_azkar(self, interaction: discord.Interaction):
        self.azkar_channel_id = interaction.channel_id
        if not self.auto_azkar_loop.is_running():
            self.auto_azkar_loop.start()

        embed = discord.Embed(
            title="✅ تم تفعيل الأذكار التلقائية",
            description=(
                "سيتم إرسال:\n"
                "☀️ أذكار الصباح ─ بعد الفجر\n"
                "🌇 أذكار المساء ─ بعد العصر\n"
                "📅 المناسبات الإسلامية ─ تلقائياً"
            ),
            color=0x27AE60,
        )
        embed.set_thumbnail(url=MOSQUE_ICON)
        embed.set_footer(text="﴿ وَاذْكُر رَّبَّكَ كَثِيرًا ﴾")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="azkar-off", description="🔕 إيقاف إرسال الأذكار التلقائية")
    async def disable_azkar(self, interaction: discord.Interaction):
        self.azkar_channel_id = None
        if self.auto_azkar_loop.is_running():
            self.auto_azkar_loop.cancel()

        embed = discord.Embed(
            title="⛔ تم إيقاف الأذكار التلقائية",
            description="لن يتم إرسال أذكار تلقائية",
            color=0xE74C3C,
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="events", description="📅 عرض المناسبات الإسلامية القادمة")
    async def events(self, interaction: discord.Interaction):
        await interaction.response.defer()

        hijri = await get_hijri_date()
        if not hijri:
            embed = discord.Embed(
                title="❌ خطأ في جلب التاريخ الهجري",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        hijri_month = int(hijri.get("month", {}).get("number", 1))
        hijri_day = int(hijri.get("day", 1))

        from utils.events import get_upcoming_events
        upcoming = get_upcoming_events(hijri_month, hijri_day, days_ahead=90)

        if not upcoming:
            embed = discord.Embed(
                title="📅 المناسبات الإسلامية",
                description="لا توجد مناسبات إسلامية قريبة",
                color=0x3498DB,
            )
            await interaction.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="📅 المناسبات الإسلامية القادمة",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=CALENDAR_ICON)

        for ev in upcoming[:5]:
            days = ev["days_until"]
            when = "🎉 اليوم!" if days == 0 else f"⏳ بعد {days} يوم"
            embed.add_field(
                name=f"🕌 {ev['name_ar']}",
                value=f"{when}\n{ev['description']}",
                inline=False,
            )

        embed.set_footer(text="﴿ وَتَعَاوَنُوا عَلَى الْبِرِّ وَالتَّقْوَى ﴾")
        await interaction.followup.send(embed=embed)

    @tasks.loop(minutes=5)
    async def auto_azkar_loop(self):
        if not self.azkar_channel_id:
            return

        channel = self.bot.get_channel(self.azkar_channel_id)
        if not channel:
            return

        timings = await get_prayer_times()
        tz_name = timings.get("_timezone", "UTC") if timings else "UTC"
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(tz_name))
        except Exception:
            now = datetime.now(timezone.utc)
        current_time = now.time()

        if current_time.hour == 0:
            self.morning_sent = False
            self.evening_sent = False

        if not self.morning_sent and current_time >= MORNING_TIME:
            self.morning_sent = True
            config = AZKAR_CONFIG["morning"]
            azkar = get_morning_azkar()
            text = format_azkar(azkar, config["title"])
            chunks = self._chunk_text(text, 4096)
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(
                    title=config["title"] if i == 0 else None,
                    description=chunk,
                    color=config["color"],
                )
                if i == 0:
                    embed.set_thumbnail(url=BOOK_ICON)
                embed.set_footer(text=config["footer"])
                await channel.send(embed=embed)

        if not self.evening_sent and current_time >= EVENING_TIME:
            self.evening_sent = True
            config = AZKAR_CONFIG["evening"]
            azkar = get_evening_azkar()
            text = format_azkar(azkar, config["title"])
            chunks = self._chunk_text(text, 4096)
            for i, chunk in enumerate(chunks):
                embed = discord.Embed(
                    title=config["title"] if i == 0 else None,
                    description=chunk,
                    color=config["color"],
                )
                if i == 0:
                    embed.set_thumbnail(url=BOOK_ICON)
                embed.set_footer(text=config["footer"])
                await channel.send(embed=embed)

        if current_time.hour == 8 and current_time.minute < 5:
            hijri = await get_hijri_date()
            if hijri:
                hijri_month = int(hijri.get("month", {}).get("number", 1))
                hijri_day = int(hijri.get("day", 1))
                today_events = get_today_events(hijri_month, hijri_day)

                for ev in today_events:
                    embed = discord.Embed(
                        title=f"🕌 {ev['name_ar']}",
                        description=ev["description"],
                        color=0xF1C40F,
                    )
                    embed.set_thumbnail(url=CALENDAR_ICON)
                    embed.set_footer(text="﴿ وَتَعَاوَنُوا عَلَى الْبِرِّ وَالتَّقْوَى ﴾")
                    await channel.send(embed=embed)

    @auto_azkar_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        if self.azkar_channel_id and not self.auto_azkar_loop.is_running():
            self.auto_azkar_loop.start()

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
    await bot.add_cog(AutoAzkarCog(bot))
