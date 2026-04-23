import os
import sys
import traceback
import logging
from pathlib import Path

BOT_DIR = Path(__file__).parent.resolve()
os.chdir(BOT_DIR)
sys.path.insert(0, str(BOT_DIR))

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("muslim_bot")

GUILD_ID = os.getenv("GUILD_ID", "")

COGS = [
    "cogs.prayer",
    "cogs.azkar_cog",
    "cogs.quran_cog",
    "cogs.tafsir_cog",
    "cogs.settings_cog",
    "cogs.reminders",
    "cogs.auto_azkar",
    "cogs.welcome_cog",
    "cogs.help_cog",
]


class MuslimBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Required for some features
        intents.members = True  # Required for welcome messages
        super().__init__(
            command_prefix="!",
            intents=intents,
        )

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                log.info(f"Loaded cog: {cog}")
            except Exception:
                log.error(f"Failed to load cog {cog}:\n{traceback.format_exc()}")

        # Guild sync = instant, Global sync = up to 1 hour
        if GUILD_ID:
            try:
                guild = discord.Object(id=int(GUILD_ID))
                self.tree.copy_global_to(guild=guild)
                synced = await self.tree.sync(guild=guild)
                log.info(f"Synced {len(synced)} commands to guild {GUILD_ID} (instant)")
            except discord.errors.Forbidden:
                log.warning(f"Failed to sync to guild {GUILD_ID}, using global sync instead")
                log.warning("Make sure the bot has 'applications.commands' permission")
                synced = await self.tree.sync()
                log.info(f"Synced {len(synced)} commands globally (may take up to 1 hour)")
            except Exception as e:
                log.error(f"Error syncing to guild: {e}, using global sync instead")
                synced = await self.tree.sync()
                log.info(f"Synced {len(synced)} commands globally (may take up to 1 hour)")
        else:
            synced = await self.tree.sync()
            log.info(f"Synced {len(synced)} commands globally (may take up to 1 hour)")

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

