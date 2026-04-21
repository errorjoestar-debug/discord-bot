import os
import logging
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands, tasks

from utils.prayer_times import get_prayer_times, PRAYER_NAMES_AR, PRAYER_EMOJIS, PRAYER_COLORS
from utils.server_settings import get_server_city

log = logging.getLogger(__name__)

MOSQUE_ICON = "https://images.unsplash.com/photo-1564769625688-478c7a3c38b6?w=800&q=80"
BELL_ICON = "https://images.unsplash.com/photo-1542384385-8c8a8495a948?w=800&q=80"


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

    @app_commands.command(name="remind-on", description="🔔 تفعيل تنبيهات الأذان تلقائيًا في هذه القناة")
    async def enable_reminders(self, interaction: discord.Interaction):
        self.reminder_channel_id = interaction.channel_id
        if not self.check_prayers.is_running():
            self.check_prayers.start()

        embed = discord.Embed(
            title="🔔 تم تفعيل التنبيهات",
            description=f"سيتم إرسال التنبيهات في هذا الروم قبل كل صلاة",
            color=0x2ECC71,
        )
        embed.set_thumbnail(url=BELL_ICON)
        embed.set_footer(text="تنبيهات صلاة • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remind-off", description="🔕 إيقاف تنبيهات الأذان التلقائية")
    async def disable_reminders(self, interaction: discord.Interaction):
        self.reminder_channel_id = None
        self.notified_prayers.clear()
        if self.check_prayers.is_running():
            self.check_prayers.cancel()

        embed = discord.Embed(
            title="🔕 تم تعطيل التنبيهات",
            description="تم إيقاف التنبيهات",
            color=0xE74C3C,
        )
        embed.set_thumbnail(url=BELL_ICON)
        embed.set_footer(text="تنبيهات صلاة • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @tasks.loop(minutes=1)
    async def check_prayers(self):
        if not self.reminder_channel_id:
            return

        channel = self.bot.get_channel(self.reminder_channel_id)
        if not channel:
            return

        city, country, method = None, None, None
        if hasattr(channel, "guild") and channel.guild:
            saved = get_server_city(channel.guild.id)
            if saved:
                city, country, method = saved
        timings = await get_prayer_times(city, country, method)
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
                emoji = PRAYER_EMOJIS.get(key, "✨")
                color = PRAYER_COLORS.get(key, 0xF1C40F)

                embed = discord.Embed(
                    title=f"{emoji} حان وقت صلاة {ar_name}",
                    description=f"حيّ على الصلاة! حان وقت صلاة **{ar_name}**\nأقيموا الصلاة بارك الله فيكم 🤲",
                    color=color,
                )
                embed.set_thumbnail(url=MOSQUE_ICON)
                embed.set_footer(text="﴿ إِنَّ الصَّلَاةَ كَانَتْ عَلَى الْمُؤْمِنِينَ كِتَابًا مَّوْقُوتًا ﴾ • MuslimBot")
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
