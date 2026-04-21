import json
import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path

from utils.quran import get_random_verse, get_verse
from utils.quran_audio import get_reciters, get_reciter_by_id, get_ayah_audio_url, get_random_allah_name

QURAN_ICON = "https://cdn-icons-png.flaticon.com/512/3564/3564299.png"
SPEAKER_ICON = "https://cdn-icons-png.flaticon.com/512/4248/4248710.png"

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
                title="❌ لازم تكون في روم صوتي",
                description="ادخل روم صوتي الأوّل وبعدين شغّل القرآن",
                color=0xE74C3C,
            )
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
                await interaction.followup.send(embed=embed)
                return

        source = discord.FFmpegPCMAudio(audio_url)
        if vc.is_playing():
            vc.stop()
        vc.play(source)

        reciter_name = reciter_info["name"] if reciter_info else reciter_id

        embed = discord.Embed(
            title="🔊 يتم تشغيل تلاوة قرآنية",
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
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ لا توجد تلاوة قيد التشغيل",
                description="البوت ليس موجودًا في أي روم صوتي",
                color=0xE74C3C,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reciters", description="🎤 عرض القُرّاء المتاحين للتلاوة")
    async def list_reciters(self, interaction: discord.Interaction):
        reciters = get_reciters()
        lines = []
        for r in reciters:
            lines.append(f"🎤 **{r['name']}** ─ `{r['id']}`")

        embed = discord.Embed(
            title="🎤 القُرّاء المتاحون",
            description="\n".join(lines),
            color=0x196F3D,
        )
        embed.set_thumbnail(url=SPEAKER_ICON)
        embed.set_footer(text="اختر القارئ من القائمة في أمر /quran-play ─ ﴿ وَرَتِّلِ ٱلْقُرْءَانَ تَرْتِيلًا ﴾")
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
            title=f"✨ {selected['ar']} ─ {selected['en']}",
            description=f"**{selected['meaning']}**",
            color=0xF1C40F,
        )
        embed.set_thumbnail(url=QURAN_ICON)
        embed.set_footer(text=f"الاسم رقم {selected['number']} من ٩٩ اسم من أسماء الله الحسنى ﴿ وَلِلَّهِ الْأَسْمَاءُ الْحُسْنَىٰ ﴾")
        await interaction.response.send_message(embed=embed)

    async def cog_unload(self):
        for vc in self.voice_clients.values():
            if vc.is_connected():
                await vc.disconnect()


async def setup(bot: commands.Bot):
    await bot.add_cog(QuranVoiceCog(bot))
