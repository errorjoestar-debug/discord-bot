import os
import logging
from datetime import datetime, time

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.azkar import get_morning_azkar, get_evening_azkar, format_azkar
from utils.prayer_times import get_hijri_date
from utils.events import get_today_events

log = logging.getLogger(__name__)

MORNING_TIME = time(5, 30)   # 5:30 AM - after Fajr
EVENING_TIME = time(16, 0)   # 4:00 PM - after Asr


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
                "☀️ أذكار الصباح - بعد الفجر\n"
                "🌇 أذكار المساء - بعد العصر\n"
                "📅 المناسبات الإسلامية - تلقائياً"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="azkar-off", description="🔕 إيقاف إرسال الأذكار التلقائية")
    async def disable_azkar(self, interaction: discord.Interaction):
        self.azkar_channel_id = None
        if self.auto_azkar_loop.is_running():
            self.auto_azkar_loop.cancel()

        embed = discord.Embed(
            title="⛔ تم إيقاف الأذكار التلقائية",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="events", description="📅 عرض المناسبات الإسلامية القادمة")
    async def events(self, interaction: discord.Interaction):
        await interaction.response.defer()

        hijri = await get_hijri_date()
        if not hijri:
            await interaction.followup.send("❌ حدث خطأ في جلب التاريخ الهجري.")
            return

        hijri_month = int(hijri.get("month", {}).get("number", 1))
        hijri_day = int(hijri.get("day", 1))

        from utils.events import get_upcoming_events
        upcoming = get_upcoming_events(hijri_month, hijri_day, days_ahead=90)

        if not upcoming:
            await interaction.followup.send("لا توجد مناسبات إسلامية قريبة.")
            return

        embed = discord.Embed(
            title="📅 المناسبات الإسلامية القادمة",
            color=discord.Color.blue(),
        )

        for ev in upcoming[:5]:
            days = ev["days_until"]
            when = "اليوم! 🎉" if days == 0 else f"بعد {days} يوم"
            embed.add_field(
                name=f"{ev['name_ar']}",
                value=f"{when}\n{ev['description']}",
                inline=False,
            )

        await interaction.followup.send(embed=embed)

    @tasks.loop(minutes=5)
    async def auto_azkar_loop(self):
        if not self.azkar_channel_id:
            return

        channel = self.bot.get_channel(self.azkar_channel_id)
        if not channel:
            return

        now = datetime.now()
        current_time = now.time()

        # Reset flags at midnight
        if current_time.hour == 0:
            self.morning_sent = False
            self.evening_sent = False

        # Morning azkar
        if not self.morning_sent and current_time >= MORNING_TIME:
            self.morning_sent = True
            azkar = get_morning_azkar()
            text = format_azkar(azkar, "أذكار الصباح ☀️")
            for chunk in self._chunk_text(text, 4096):
                embed = discord.Embed(description=chunk, color=discord.Color.orange())
                embed.set_footer(text="لا تنسَ ذكر الله ☀️")
                await channel.send(embed=embed)

        # Evening azkar
        if not self.evening_sent and current_time >= EVENING_TIME:
            self.evening_sent = True
            azkar = get_evening_azkar()
            text = format_azkar(azkar, "أذكار المساء 🌇")
            for chunk in self._chunk_text(text, 4096):
                embed = discord.Embed(description=chunk, color=discord.Color.purple())
                embed.set_footer(text="لا تنسَ ذكر الله 🌇")
                await channel.send(embed=embed)

        # Islamic events check
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
                        color=discord.Color.gold(),
                    )
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
