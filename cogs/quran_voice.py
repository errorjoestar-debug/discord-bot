import discord
from discord import app_commands
from discord.ext import commands

from utils.quran import get_random_verse, get_verse
from utils.quran_audio import get_reciters, get_reciter_by_id, get_ayah_audio_url


class QuranVoiceCog(commands.Cog, name="القرآن صوتي"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_clients: dict[int, discord.VoiceClient] = {}
        self.current_reciter: dict[int, str] = {}

    @app_commands.command(name="quran-play", description="🔊 تشغيل آية قرآنية في الفويس")
    @app_commands.describe(
        surah="رقم السورة (1-114)",
        ayah="رقم الآية",
        reciter="اسم القارئ (اختياري)",
    )
    async def quran_play(
        self,
        interaction: discord.Interaction,
        surah: int | None = None,
        ayah: int | None = None,
        reciter: str | None = None,
    ):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ لازم تكون في روم صوتي الأول!", ephemeral=True)
            return

        await interaction.response.defer()

        reciter_id = "ar.alafasy"
        if reciter:
            r = get_reciter_by_id(reciter)
            if r:
                reciter_id = r["id"]
            else:
                await interaction.followup.send(f"❌ القارئ غير موجود. استخدم `/reciters` لعرض القُرّاء المتاحين.")
                return

        if surah and ayah:
            verse = await get_verse(surah, ayah)
        else:
            verse = await get_random_verse()

        if not verse:
            await interaction.followup.send("❌ حدث خطأ في جلب الآية.")
            return

        audio_url = get_ayah_audio_url(verse["surah_number"] * 1000 + verse["ayah_number"], reciter_id)
        reciter_info = get_reciter_by_id(reciter_id)

        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild_id

        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
            vc = self.voice_clients[guild_id]
        else:
            try:
                vc = await voice_channel.connect()
                self.voice_clients[guild_id] = vc
            except Exception as e:
                await interaction.followup.send(f"❌ مش قادر أدخل الفويس: {e}")
                return

        source = discord.FFmpegPCMAudio(audio_url)
        if vc.is_playing():
            vc.stop()
        vc.play(source)

        embed = discord.Embed(
            title="📖 يتم تشغيل آية قرآنية",
            description=f"```\n{verse['text']}\n```",
            color=discord.Color.dark_green(),
        )
        reciter_name = reciter_info["name"] if reciter_info else reciter_id
        embed.set_footer(
            text=f"سورة {verse['surah_name']} - الآية {verse['ayah_number']} | القارئ: {reciter_name}"
        )

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="quran-stop", description="⏹️ إيقاف القرآن والخروج من الفويس")
    async def quran_stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()
            del self.voice_clients[guild_id]
            await interaction.response.send_message("⏹️ تم إيقاف القرآن والخروج من الفويس.")
        else:
            await interaction.response.send_message("❌ مش في فويس أصلاً.", ephemeral=True)

    @app_commands.command(name="reciters", description="🎤 عرض القُرّاء المتاحين")
    async def list_reciters(self, interaction: discord.Interaction):
        reciters = get_reciters()
        lines = []
        for r in reciters:
            lines.append(f"• **{r['name']}** (`{r['id']}`)")

        embed = discord.Embed(
            title="🎤 القُرّاء المتاحون",
            description="\n".join(lines),
            color=discord.Color.dark_green(),
        )
        embed.set_footer(text="استخدم الـ id في أمر /quran-play")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="allah-name", description="✨ اسم من أسماء الله الحسنى مع المعنى")
    async def allah_name(self, interaction: discord.Interaction):
        from utils.quran_audio import get_random_allah_name
        name = get_random_allah_name()
        embed = discord.Embed(
            title=f"✨ {name['ar']} - {name['en']}",
            description=name['meaning'],
            color=discord.Color.gold(),
        )
        embed.set_footer(text=f"الاسم رقم {name['number']} من أسماء الله الحسنى")
        await interaction.response.send_message(embed=embed)

    async def cog_unload(self):
        for vc in self.voice_clients.values():
            if vc.is_connected():
                await vc.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranVoiceCog(bot))
