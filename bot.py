import os
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("muslim_bot")

COGS = [
    "cogs.prayer",
    "cogs.azkar_cog",
    "cogs.quran_cog",
    "cogs.reminders",
    "cogs.auto_azkar",
]


class MuslimBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                log.info(f"Loaded cog: {cog}")
            except Exception as e:
                log.error(f"Failed to load cog {cog}: {e}")

        synced = await self.tree.sync()
        log.info(f"Synced {len(synced)} commands")

    async def on_ready(self):
        log.info(f"Bot ready: {self.user} (ID: {self.user.id})")


def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        log.error("DISCORD_TOKEN not found in .env file!")
        return

    bot = MuslimBot()
    bot.run(token)


if __name__ == "__main__":
    main()
