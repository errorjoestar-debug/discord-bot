import discord
from discord import app_commands
from discord.ext import commands

MOSQUE_ICON = "https://images.unsplash.com/photo-1564769625688-478c7a3c38b6?w=800&q=80"


class WelcomeCog(commands.Cog, name="الترحيب"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """إرسال رسالة ترحيبية عند انضمام عضو جديد"""
        if member.guild is None:
            return

        # البحث عن روم الترحيب أو استخدام روم عام
        welcome_channel = None
        for channel in member.guild.text_channels:
            if "welcome" in channel.name.lower() or "ترحيب" in channel.name.lower():
                welcome_channel = channel
                break
        
        if not welcome_channel:
            # إذا لم يوجد روم ترحيب، استخدم أول روم متاح
            for channel in member.guild.text_channels:
                if channel.permissions_for(member.guild.me).send_messages:
                    welcome_channel = channel
                    break

        if not welcome_channel:
            return

        embed = discord.Embed(
            title="🕌 مرحباً بك في مسلم بوت",
            description=f"السلام عليكم ورحمة الله وبركاته {member.mention}!\n\nأنا بوت إسلامي يساعدك في:",
            color=0x27AE60,
        )
        embed.set_thumbnail(url=MOSQUE_ICON)
        embed.add_field(
            name="📖 القرآن الكريم",
            value="آيات عشوائية، سور كاملة، بحث في القرآن، تفسير",
            inline=False,
        )
        embed.add_field(
            name="🕌 أوقات الصلاة",
            value="أوقات الصلاة الخمس، التاريخ الهجري، تنبيهات الأذان",
            inline=False,
        )
        embed.add_field(
            name="🤲 الأذكار",
            value="أذكار الصباح والمساء، أدعية، أحاديث، عداد ذكر شخصي",
            inline=False,
        )
        embed.add_field(
            name="🔧 أوامر مفيدة",
            value="اتجاه القبلة، حساب الزكاة، تحويل التاريخ، أوقات الشمس",
            inline=False,
        )
        embed.add_field(
            name="📚 كيفية الاستخدام",
            value="اكتب `/help` لعرض جميع الأوامر المتاحة",
            inline=False,
        )
        embed.set_footer(text="﴿ وَمَنْ يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا ﴾ • MuslimBot")

        try:
            await welcome_channel.send(embed=embed)
        except Exception:
            pass


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))
