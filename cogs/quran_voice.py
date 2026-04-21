import json
import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path

from utils.quran import get_random_verse, get_verse
from utils.quran_audio import get_reciters, get_reciter_by_id, get_ayah_audio_url, get_random_allah_name

QURAN_ICON = "https://images.unsplash.com/photo-1576413329366-5b2c6e0463e4?w=800&q=80"
SPEAKER_ICON = "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=800&q=80"

DATA_DIR = Path(__file__).parent.parent / "data"

RECITER_CHOICES = [
    app_commands.Choice(name="مشاري العفاسي", value="ar.alafasy"),
    app_commands.Choice(name="عبد الباسط عبد الصمد (مرتل)", value="ar.abdulbasitmurattal"),
    app_commands.Choice(name="محمود خليل الحصري", value="ar.husary"),
    app_commands.Choice(name="محمد صديق المنشاوي", value="ar.minshawi"),
    app_commands.Choice(name="عبد الرحمن السديس", value="ar.abdurrahmaansudais"),
    app_commands.Choice(name="سعود الشريم", value="ar.saaborimuneer"),
    app_commands.Choice(name="ماهر المعيقلي", value="ar.maaborali"),
    app_commands.Choice(name="ياسر الدوسري", value="ar.yaserdussry"),
    app_commands.Choice(name="صلاح البدير", value="ar.salahbudair"),
    app_commands.Choice(name="خالد الجليل", value="ar.khalidaljaleel"),
    app_commands.Choice(name="عبد الله الجهني", value="ar.abdullahjahny"),
    app_commands.Choice(name="علي الحذيفي", value="ar.alihudhaify"),
    app_commands.Choice(name="محمد أيوب", value="ar.muhammadayyoub"),
    app_commands.Choice(name="سعد الغامدي", value="ar.saadalghamdi"),
    app_commands.Choice(name="فارس عباد", value="ar.faresabbad"),
]


async def allah_name_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
    with open(DATA_DIR / "allah_names.json", encoding="utf-8") as f:
        names = json.load(f)
    choices = []
    for n in names:
        label = f"{n['ar']} - {n['en']}"
        if current.lower() in n["ar"] or current.lower() in n["en"].lower() or current in str(n["number"]):
            choices.append(app_commands.Choice(name=label[:100], value=n["ar"]))
    return choices[:25]


class QuranVoiceCog(commands.Cog, name="القرآن صوتي"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_clients: dict[int, discord.VoiceClient] = {}
        self.current_reciter: dict[int, str] = {}
        self.queues: dict[int, list[dict]] = {}
        self.current_track: dict[int, dict] = {}
        self.looping: dict[int, bool] = {}

    @app_commands.command(name="quran-play", description="🔊 تشغيل تلاوة آية قرآنية في الروم الصوتي")
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
                title="❌ أنت لست في روم صوتي",
                description="يجب أن تكون في روم صوتي لاستخدام هذا الأمر",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        reciter_id = reciter or "ar.alafasy"

        if surah and ayah:
            verse = await get_verse(surah, ayah)
        else:
            verse = await get_random_verse()

        if not verse:
            embed = discord.Embed(
                title="❌ تعذّر جلب الآية",
                description="حاول مرّة أخرى لاحقًا",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        audio_url = get_ayah_audio_url(verse["absolute_number"], reciter_id)
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
                embed = discord.Embed(
                    title="❌ تعذّر الدخول للروم الصوتي",
                    description=str(e),
                    color=0xE74C3C,
                )
                embed.set_footer(text="MuslimBot")
                await interaction.followup.send(embed=embed)
                return

        source = discord.FFmpegPCMAudio(audio_url)
        if vc.is_playing():
            vc.stop()
        vc.play(source)

        reciter_name = reciter_info["name"] if reciter_info else reciter_id

        embed = discord.Embed(
            title="🔊 يتم تشغيل تلاوة قرآنية",
            description=f"**{verse['text']}**\n\n📖 سورة {verse['surah_name']} - آية {verse['ayah_number']}\n🎙️ القارئ: {reciter_name}",
            color=0x9B59B6,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text="﴿ فَاقْرَءُوا مَا تَيَسَّرَ مِنَ الْقُرْآنِ ﴾ • MuslimBot")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="quran-stop", description="⏹️ إيقاف التلاوة والخروج من الروم الصوتي")
    async def quran_stop(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            if vc.is_playing():
                vc.stop()
            await vc.disconnect()
            del self.voice_clients[guild_id]
            embed = discord.Embed(
                title="⏹️ تم إيقاف التلاوة",
                description="تم الخروج من الروم الصوتي",
                color=0x95A5A6,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ لا يوجد تلاوة قيد التشغيل",
                description="لا يوجد تلاوة قرآنية قيد التشغيل حالياً",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reciters", description="🎤 عرض القُرّاء المتاحين للتلاوة")
    async def list_reciters(self, interaction: discord.Interaction):
        reciters = get_reciters()
        lines = []
        for r in reciters:
            lines.append(f"🎤 **{r['name']}** ─ `{r['id']}`")

        embed = discord.Embed(
            title="🎙️ قائمة القُرّاء",
            description="اختر القارئ الذي تفضّله لتشغيل التلاوات",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text="القارئ الافتراضي: مشاري العفاسي • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="allah-name", description="✨ اسم من أسماء الله الحسنى مع معناه")
    @app_commands.describe(name="اختر اسم أو اتركه فارغ لعشوائي")
    @app_commands.autocomplete(name=allah_name_autocomplete)
    async def allah_name(self, interaction: discord.Interaction, name: str | None = None):
        if name:
            with open(DATA_DIR / "allah_names.json", encoding="utf-8") as f:
                names = json.load(f)
            selected = next((n for n in names if n["ar"] == name), None)
            if not selected:
                selected = get_random_allah_name()
        else:
            selected = get_random_allah_name()

        embed = discord.Embed(
            title="🌟 اسم من أسماء الله الحسنى",
            description=f"**{selected['ar']}**\n\n{selected['meaning']}",
            color=0xF39C12,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        embed.set_footer(text="﴿ وَلِلَّهِ الْأَسْمَاءُ الْحُسْنَى فَادْعُوهُ بِهَا ﴾ • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quran-queue", description="📋 عرض قائمة التشغيل")
    async def show_queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not guild_id:
            await interaction.response.send_message("هذا الأمر للسيرفرات فقط", ephemeral=True)
            return

        queue = self.queues.get(guild_id, [])
        current = self.current_track.get(guild_id)
        
        if not queue and not current:
            embed = discord.Embed(
                title="📋 قائمة التشغيل فارغة",
                description="أضف آيات باستخدام `/quran-play`",
                color=0x95A5A6,
            )
            embed.set_thumbnail(url=SPEAKER_ICON)
            embed.set_footer(text="قائمة التشغيل • MuslimBot")
            await interaction.response.send_message(embed=embed)
            return

        lines = []
        if current:
            lines.append(f"🔊 **الآن:** {current['surah_name']} - آية {current['ayah_number']}")
        
        if queue:
            lines.append("\n**التالي:**")
            for i, track in enumerate(queue[:10], 1):
                lines.append(f"{i}. {track['surah_name']} - آية {track['ayah_number']}")
            if len(queue) > 10:
                lines.append(f"\n... و {len(queue) - 10} آية أخرى")

        embed = discord.Embed(
            title="📋 قائمة التشغيل",
            description="\n".join(lines) if lines else "فارغة",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text=f"إجمالي: {len(queue)} آية • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quran-skip", description="⏭️ تخطي التلاوة الحالية")
    async def skip_track(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not guild_id:
            await interaction.response.send_message("هذا الأمر للسيرفرات فقط", ephemeral=True)
            return

        if guild_id in self.voice_clients and self.voice_clients[guild_id].is_playing():
            self.voice_clients[guild_id].stop()
            embed = discord.Embed(
                title="⏭️ تم التخطي",
                description="جاري تشغيل الآية التالية...",
                color=0xF39C12,
            )
            embed.set_footer(text="قائمة التشغيل • MuslimBot")
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ لا يوجد تلاوة قيد التشغيل",
                color=0xE74C3C,
            )
            embed.set_footer(text="قائمة التشغيل • MuslimBot")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="quran-loop", description="🔁 تفعيل/تعطيل التكرار")
    async def toggle_loop(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not guild_id:
            await interaction.response.send_message("هذا الأمر للسيرفرات فقط", ephemeral=True)
            return

        self.looping[guild_id] = not self.looping.get(guild_id, False)
        is_looping = self.looping[guild_id]
        
        embed = discord.Embed(
            title="🔁 التكرار",
            description=f"تم {'تفعيل' if is_looping else 'تعطيل'} التكرار",
            color=0x27AE60 if is_looping else 0xE74C3C,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text="قائمة التشغيل • MuslimBot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="quran-clear", description="🗑️ مسح قائمة التشغيل")
    async def clear_queue(self, interaction: discord.Interaction):
        guild_id = interaction.guild_id
        if not guild_id:
            await interaction.response.send_message("هذا الأمر للسيرفرات فقط", ephemeral=True)
            return

        self.queues[guild_id] = []
        self.looping[guild_id] = False
        
        embed = discord.Embed(
            title="🗑️ تم مسح قائمة التشغيل",
            description="تم إفراغ قائمة التشغيل",
            color=0xE74C3C,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text="قائمة التشغيل • MuslimBot")
        await interaction.response.send_message(embed=embed)

    async def cog_unload(self):
        for vc in self.voice_clients.values():
            if vc.is_connected():
                await vc.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranVoiceCog(bot))
