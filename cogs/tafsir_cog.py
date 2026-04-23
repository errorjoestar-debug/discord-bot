import io
import discord
from discord import app_commands
from discord.ext import commands

from utils.tafsir import get_tafsir
from utils.quran_image import create_text_image

QURAN_ICON = "https://images.unsplash.com/photo-1576413329366-5b2c6e0463e4?w=800&q=80"


class TafsirCog(commands.Cog, name="التفسير"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="tafsir", description="📖 عرض التفسير الميسر لآية من القرآن الكريم")
    @app_commands.describe(surah="رقم السورة (1-114)", ayah="رقم الآية")
    async def tafsir(
        self,
        interaction: discord.Interaction,
        surah: int,
        ayah: int,
    ):
        await interaction.response.defer()

        if surah < 1 or surah > 114:
            embed = discord.Embed(
                title="❌ رقم سورة غير صحيح",
                description="رقم السورة يجب أن يكون بين 1 و 114",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        result = await get_tafsir(surah, ayah)
        if not result:
            embed = discord.Embed(
                title="❌ خطأ في جلب التفسير",
                description="تأكّد من صِحّة رقم السورة والآية",
                color=0xE74C3C,
            )
            embed.set_footer(text="MuslimBot")
            await interaction.followup.send(embed=embed)
            return

        text = result["tafsir"] or result["text"]

        # Try image first
        try:
            title = f"التفسير الميسر - سورة {result['surah_name']} آية {result['ayah_number']}"
            img_bytes = await create_text_image(title, text, "﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ ﴾ • MuslimBot", "#8E44AD")
            if img_bytes:
                file = discord.File(io.BytesIO(img_bytes), filename="tafsir.png")
                embed = discord.Embed(color=0x8E44AD)
                embed.set_image(url="attachment://tafsir.png")
                embed.set_footer(text="﴿ وَأَنزَلْنَا إِلَيْكَ الذِّكْرَ لِتُبَيِّنَ لِلنَّاسِ مَا نُزِّلَ إِلَيْهِمْ ﴾ • MuslimBot")
                await interaction.followup.send(embed=embed, file=file)
                return
        except Exception:
            pass

        # Fallback to text
        chunks = self._chunk_text(text, 4096)
        for i, chunk in enumerate(chunks):
            if i == 0:
                embed = discord.Embed(
                    title=f"📖 التفسير الميسر - سورة {result['surah_name']} آية {result['ayah_number']}",
                    description=chunk,
                    color=0x8E44AD,
                )
                embed.set_thumbnail(url=QURAN_ICON)
                embed.set_footer(text="﴿ وَأَنزَلْنَا إِلَيْكَ الذِّكْرَ لِتُبَيِّنَ لِلنَّاسِ مَا نُزِّلَ إِلَيْهِمْ ﴾ • MuslimBot")
            else:
                embed = discord.Embed(
                    description=chunk,
                    color=0x196F3D,
                )
            if len(chunks) > 1:
                embed.set_footer(text=f"الجزء {i+1}/{len(chunks)} • MuslimBot")
            else:
                embed.set_footer(text="التفسير الميسر ─ ﴿ وَلَقَدْ يَسَّرْنَا الْقُرْآنَ لِلذِّكْرِ ﴾")
            await interaction.followup.send(embed=embed)

    @staticmethod
    def _chunk_text(text: str, max_len: int) -> list[str]:
        if len(text) <= max_len:
            return [text]
        chunks = []
        while text:
            if len(text) <= max_len:
                chunks.append(text)
                break
            split_at = text.rfind(" ", 0, max_len)
            if split_at == -1:
                split_at = max_len
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip()
        return chunks


async def setup(bot: commands.Bot):
    await bot.add_cog(TafsirCog(bot))

