import discord
from discord import app_commands
from discord.ext import commands

from utils.quran import get_random_verse, get_verse
from utils.quran_audio import get_reciters, get_reciter_by_id, get_ayah_audio_url

QURAN_ICON = "https://cdn-icons-png.flaticon.com/512/331/331008.png"
SPEAKER_ICON = "https://cdn-icons-png.flaticon.com/512/732/732078.png"

RECITER_CHOICES = [
    app_commands.Choice(name="مشاري العفاسي", value="ar.alafasy"),
    app_commands.Choice(name="عبد الباسط عبد الصمد (مرتل)", value="ar.abdulbasitmurattal"),
    app_commands.Choice(name="محمود خليل الحصري", value="ar.husary"),
    app_commands.Choice(name="محمد صديق المنشاوي", value="ar.minshawi"),
    app_commands.Choice(name="عبد الرحمن السديس", value="ar.abdurrahmaansudais"),
    app_commands.Choice(name="سعود الشريم", value="ar.saaborimuneer"),
    app_commands.Choice(name="ماهر المعيقلي", value="ar.maaborali"),
]


class QuranVoiceCog(commands.Cog, name="القرآن صوتي"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_clients: dict[int, discord.VoiceClient] = {}
        self.current_reciter: dict[int, str] = {}

    @app_commands.command(name="quran-play", description="🔊 تشغيل آية قرآنية في الفويس")
    @app_commands.describe(
        surah="رقم السورة (1-114)",
        ayah="رقم الآية",
        reciter="اختر القارئ",
    )
    @app_commands.choices(reciter=RECITER_CHOICES)
    async def quran_play(
        self,
        interaction: discord.Interaction,
        surah: int | None = None,
        ayah: int | None = None,
        reciter: str | None = None,
    ):
        if not interaction.user.voice:
            embed = discord.Embed(
                title="❌ لازم تكون في روم صوتي",
                description="ادخل روم صوتي الأول وبعدين شغّل القرآن",
                color=0xE74C3C,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        reciter_id = reciter or "ar.alafasy"
        reciter_info = get_reciter_by_id(reciter_id)

        if surah and ayah:
            verse = await get_verse(surah, ayah)
        else:
            verse = await get_random_verse()

        if not verse:
            embed = discord.Embed(
                title="❌ خطأ في جلب الآية",
                color=0xE74C3C,
            )
            await interaction.followup.send(embed=embed)
            return

        audio_url = get_ayah_audio_url(verse["surah_number"] * 1000 + verse["ayah_number"], reciter_id)

        voice_channel = interaction.user.voice.channel
        guild_id = interaction.guild_id

        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
            vc = self.voice_clients[guild_id]
        else:
            try:
                vc = await voice_channel.connect()
                self.voice_clients[guild_id] = vc
            except Exception as e:
                embed = discord.Embed(
                    title="❌ مش قادر أدخل الفويس",
                    description=str(e),
                    color=0xE74C3C,
                )
                await interaction.followup.send(embed=embed)
                return

        source = discord.FFmpegPCMAudio(audio_url)
        if vc.is_playing():
            vc.stop()
        vc.play(source)

        reciter_name = reciter_info["name"] if reciter_info else reciter_id

        embed = discord.Embed(
            title="🔊 يتم تشغيل آية قرآنية",
            description=f"\n{verse['text']}\n",
            color=0x196F3D,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.add_field(
            name="📍 السورة",
            value=f"**{verse['surah_name']}** ({verse['surah_english']})",
            inline=True,
        )
        embed.add_field(
            name="🔢 رقم الآية",
            value=str(verse["ayah_number"]),
            inline=True,
        )
        embed.add_field(
            name="🎤 القارئ",
            value=reciter_name,
            inline=False,
        )
        embed.set_footer(text="﴿ وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا ﴾")

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
            embed = discord.Embed(
                title="⏹️ تم إيقاف القرآن",
                description="تم الخروج من الروم الصوتي",
                color=0x95A5A6,
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ مش في فويس",
                description="البوت مش موجود في أي روم صوتي",
                color=0xE74C3C,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reciters", description="🎤 عرض القُرّاء المتاحين")
    async def list_reciters(self, interaction: discord.Interaction):
        reciters = get_reciters()
        lines = []
        for r in reciters:
            lines.append(f"🎤 **{r['name']}**")

        embed = discord.Embed(
            title="🎤 القُرّاء المتاحون",
            description="\n".join(lines),
            color=0x196F3D,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text="اختر القارئ من القائمة في أمر /quran-play")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="allah-name", description="✨ اسم من أسماء الله الحسنى مع المعنى")
    @app_commands.describe(number="رقم الاسم (1-99) ─ اتركه فارغ لعشوائي")
    async def allah_name(self, interaction: discord.Interaction, number: int | None = None):
        from utils.quran_audio import get_random_allah_name
        import json
        from pathlib import Path

        if number is not None:
            if number < 1 or number > 99:
                embed = discord.Embed(
                    title="❌ رقم غير صحيح",
                    description="الرقم يجب أن يكون بين 1 و 99",
                    color=0xE74C3C,
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            data_dir = Path(__file__).parent.parent / "data"
            with open(data_dir / "allah_names.json", encoding="utf-8") as f:
                names = json.load(f)
            name = next((n for n in names if n["number"] == number), None)
            if not name:
                name = get_random_allah_name()
        else:
            name = get_random_allah_name()

        embed = discord.Embed(
            title=f"✨ {name['ar']} ─ {name['en']}",
            description=f"**{name['meaning']}**",
            color=0xF1C40F,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        embed.set_footer(text=f"الاسم رقم {name['number']} من ٩٩ اسم من أسماء الله الحسنى ﴿ وَلِلَّهِ الْأَسْمَاءُ الْحُسْنَىٰ ﴾")
        await interaction.response.send_message(embed=embed)

    async def cog_unload(self):
        for vc in self.voice_clients.values():
            if vc.is_connected():
                await vc.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranVoiceCog(bot))
