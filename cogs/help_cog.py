import discord
from discord import app_commands
from discord.ext import commands

HELP_ICON = "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&q=80"


class HelpCog(commands.Cog, name="المساعدة"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="❓ عرض جميع أوامر البوت")
    @app_commands.describe(category="الفئة: all, quran, prayer, azkar, settings")
    async def help_command(
        self,
        interaction: discord.Interaction,
        category: str = "all",
    ):
        categories = {
            "all": {
                "title": "📚 جميع الأوامر",
                "emoji": "📚",
                "color": 0x3498DB,
                "commands": [
                    ("📖 القرآن الكريم", [
                        "/ayah - آية قرآنية عشوائية",
                        "/surah-ayah - آية محددة",
                        "/surah - سورة كاملة",
                        "/search-quran - بحث في القرآن",
                        "/quran-list - عرض جميع السور",
                        "/quran-play - تشغيل تلاوة صوتية",
                        "/quran-stop - إيقاف التلاوة",
                        "/quran-queue - قائمة التشغيل",
                        "/quran-skip - تخطي التلاوة",
                        "/quran-loop - تكرار التلاوة",
                        "/quran-clear - مسح القائمة",
                        "/tafsir - التفسير الميسر",
                        "/allah-name - اسم من أسماء الله",
                    ]),
                    ("🕌 أوقات الصلاة", [
                        "/salah - أوقات الصلاة",
                        "/hijri - التاريخ الهجري",
                        "/athan - موعد الصلاة القادمة",
                        "/sunrise-sunset - أوقات الشمس",
                        "/date-convert - تحويل التاريخ",
                        "/qibla - اتجاه القبلة",
                        "/zakah - حساب الزكاة",
                    ]),
                    ("🤲 الأذكار", [
                        "/morning-azkar - أذكار الصباح",
                        "/evening-azkar - أذكار المساء",
                        "/sleep-azkar - أذكار النوم",
                        "/hadith - حديث عشوائي",
                        "/hadith-list - قائمة الأحاديث",
                        "/dua - دعاء عشوائي",
                        "/dua-list - قائمة الأدعية",
                        "/azkar-count - عداد الذكر",
                    ]),
                    ("🔧 الإعدادات", [
                        "/set-city - تعيين مدينة السيرفر",
                        "/settings - إعدادات السيرفر",
                        "/my-reciter - القارئ المفضل",
                        "/my-city - مدينتك المفضلة",
                        "/my-settings - إعداداتك الشخصية",
                        "/remind-on - تفعيل التنبيهات",
                        "/remind-off - إيقاف التنبيهات",
                        "/azkar-on - تفعيل الأذكار التلقائية",
                        "/azkar-off - إيقاف الأذكار التلقائية",
                        "/events - المناسبات الإسلامية",
                    ]),
                ]
            },
            "quran": {
                "title": "📖 أوامر القرآن الكريم",
                "emoji": "📖",
                "color": 0x0984E3,
                "commands": [
                    ("📖 القرآن الكريم", [
                        "/ayah - آية قرآنية عشوائية",
                        "/surah-ayah - آية محددة",
                        "/surah - سورة كاملة",
                        "/search-quran - بحث في القرآن",
                        "/quran-list - عرض جميع السور",
                        "/quran-play - تشغيل تلاوة صوتية",
                        "/quran-stop - إيقاف التلاوة",
                        "/quran-queue - قائمة التشغيل",
                        "/quran-skip - تخطي التلاوة",
                        "/quran-loop - تكرار التلاوة",
                        "/quran-clear - مسح القائمة",
                        "/tafsir - التفسير الميسر",
                        "/allah-name - اسم من أسماء الله",
                    ]),
                ]
            },
            "prayer": {
                "title": "🕌 أوامر أوقات الصلاة",
                "emoji": "🕌",
                "color": 0x27AE60,
                "commands": [
                    ("🕌 أوقات الصلاة", [
                        "/salah - أوقات الصلاة",
                        "/hijri - التاريخ الهجري",
                        "/athan - موعد الصلاة القادمة",
                        "/sunrise-sunset - أوقات الشمس",
                        "/date-convert - تحويل التاريخ",
                        "/qibla - اتجاه القبلة",
                        "/zakah - حساب الزكاة",
                    ]),
                ]
            },
            "azkar": {
                "title": "🤲 أوامر الأذكار",
                "emoji": "🤲",
                "color": 0xF39C12,
                "commands": [
                    ("🤲 الأذكار", [
                        "/morning-azkar - أذكار الصباح",
                        "/evening-azkar - أذكار المساء",
                        "/sleep-azkar - أذكار النوم",
                        "/hadith - حديث عشوائي",
                        "/hadith-list - قائمة الأحاديث",
                        "/dua - دعاء عشوائي",
                        "/dua-list - قائمة الأدعية",
                        "/azkar-count - عداد الذكر",
                    ]),
                ]
            },
            "settings": {
                "title": "⚙️ أوامر الإعدادات",
                "emoji": "⚙️",
                "color": 0x95A5A6,
                "commands": [
                    ("🔧 الإعدادات", [
                        "/set-city - تعيين مدينة السيرفر",
                        "/settings - إعدادات السيرفر",
                        "/my-reciter - القارئ المفضل",
                        "/my-city - مدينتك المفضلة",
                        "/my-settings - إعداداتك الشخصية",
                        "/remind-on - تفعيل التنبيهات",
                        "/remind-off - إيقاف التنبيهات",
                        "/azkar-on - تفعيل الأذكار التلقائية",
                        "/azkar-off - إيقاف الأذكار التلقائية",
                        "/events - المناسبات الإسلامية",
                    ]),
                ]
            }
        }

        if category not in categories:
            embed = discord.Embed(
                title="❌ فئة غير صحيحة",
                description="استخدم: all, quran, prayer, azkar, settings",
                color=0xE74C3C,
            )
            embed.set_footer(text="المساعدة • MuslimBot")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cat = categories[category]
        embed = discord.Embed(
            title=f"{cat['emoji']} {cat['title']}",
            color=cat['color'],
        )
        embed.set_thumbnail(url=HELP_ICON)

        for section_name, commands in cat['commands']:
            embed.add_field(
                name=section_name,
                value="\n".join(commands),
                inline=False,
            )

        embed.add_field(
            name="💡 نصائح",
            value="• اكتب `/` لعرض جميع الأوامر\n• استخدم autocomplete للبحث السريع\n• اضغط على الأوامر لرؤية التفاصيل",
            inline=False,
        )
        embed.set_footer(text="المساعدة • MuslimBot")

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
