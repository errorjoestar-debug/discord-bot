import os
import logging
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.prayer_times import get_prayer_times, PRAYER_NAMES_AR, PRAYER_EMOJIS, PRAYER_COLORS

log = logging.getLogger(__name__)

MOSQUE_ICON = "https://cdn-icons-png.flaticon.com/512/331/331008.png"
BELL_ICON = "https://cdn-icons-png.flaticon.com/512/1827/1827347.png"


class RemindersCog(commands.Cog, name="التنبيهات"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.notified_prayers: set[str] = set()
        self.reminder_channel_id: int | None = None
        self._load_channel_id()

    def _load_channel_id(self):
        channel_id = os.getenv("REMINDER_CHANNEL_ID", "")
        if channel_id:
            try:
                self.reminder_channel_id = int(channel_id)
            except ValueError:
                log.warning("Invalid REMINDER_CHANNEL_ID in .env")

    @app_commands.command(name="remind-on", description="🔔 تفعيل تنبيهات الصلاة في هذه القناة")
    async def enable_reminders(self, interaction: discord.Interaction):
        self.reminder_channel_id = interaction.channel_id
        if not self.check_prayers.is_running():
            self.check_prayers.start()

        embed = discord.Embed(
            title="✅ تم تفعيل التنبيهات",
            description="سيتم إرسال تنبيه عند حلول كل صلاة في هذه القناة",
            color=0x27AE60,
        )
        embed.set_thumbnail(url=BELL_ICON)
        embed.set_footer(text="﴿ حَافِظُوا عَلَى الصَّلَوَاتِ ﴾")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind-off", description="🔕 إيقاف تنبيهات الصلاة")
    async def disable_reminders(self, interaction: discord.Interaction):
        self.reminder_channel_id = None
        self.notified_prayers.clear()
        if self.check_prayers.is_running():
            self.check_prayers.cancel()

        embed = discord.Embed(
            title="⛔ تم إيقاف التنبيهات",
            description="لن يتم إرسال تنبيهات الصلاة",
            color=0xE74C3C,
        )
        embed.set_thumbnail(url=BELL_ICON)
        await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=1)
    async def check_prayers(self):
        if not self.reminder_channel_id:
            return

        channel = self.bot.get_channel(self.reminder_channel_id)
        if not channel:
            return

        timings = await get_prayer_times()
        if not timings:
            return

        tz_name = timings.get("_timezone", "UTC")
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo(tz_name))
        except Exception:
            now = datetime.now(timezone.utc)

        current_time = f"{now.hour:02d}:{now.minute:02d}"

        for key in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
            prayer_time = timings.get(key, "").split()[0]
            if prayer_time == current_time and key not in self.notified_prayers:
                self.notified_prayers.add(key)
                ar_name = PRAYER_NAMES_AR.get(key, key)
                emoji = PRAYER_EMOJIS.get(key, "🕌")
                color = PRAYER_COLORS.get(key, 0xF1C40F)

                embed = discord.Embed(
                    title=f"{emoji} حان وقت صلاة {ar_name}",
                    description=f"حيّ على الصلاة! حان وقت صلاة **{ar_name}**\nأقيموا الصلاة بارك الله فيكم 🤲",
                    color=color,
                )
                embed.set_thumbnail(url=MOSQUE_ICON)
                embed.set_footer(text="﴿ إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَّوْقُوتًا ﴾")
                await channel.send(embed=embed)

        if now.hour == 0 and now.minute < 5:
            self.notified_prayers.clear()

    @check_prayers.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        if self.reminder_channel_id and not self.check_prayers.is_running():
            self.check_prayers.start()


async def setup(bot: commands.Bot):
    await bot.add_cog(RemindersCog(bot))
