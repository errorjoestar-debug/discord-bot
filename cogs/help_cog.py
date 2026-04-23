import discord
from discord import app_commands
from discord.ext import commands
import platform
import psutil
import os

HELP_ICON = "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&q=80"
BOT_ICON = "https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=800&q=80"


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
                        "/surah-ayah - آية محددة من سورة",
                        "/surah - سورة كاملة",
                        "/surah-select - اختيار سورة من قائمة",
                        "/search-quran - بحث في القرآن",
                        "/quran-list - عرض جميع السور",
                        "/tafsir - التفسير الميسر",
                    ]),
                    ("🕌 أوقات الصلاة", [
                        "/salah - أوقات الصلاة",
                        "/hijri - التاريخ الهجري",
                        "/athan - الصلاة القادمة",
                        "/sunrise-sunset - أوقات الشمس",
                        "/date-convert - تحويل التاريخ",
                        "/qibla - اتجاه القبلة",
                        "/zakah - حساب الزكاة",
                    ]),
                    ("🤲 الأذكار والأدعية", [
                        "/morning-azkar - أذكار الصباح",
                        "/evening-azkar - أذكار المساء",
                        "/sleep-azkar - أذكار النوم",
                        "/hadith - حديث شريف عشوائي",
                        "/hadith-list - قائمة الأحاديث",
                        "/dua - دعاء عشوائي",
                        "/dua-list - قائمة الأدعية",
                        "/azkar-count - عداد الذكر التفاعلي",
                        "/favorites - عرض المفضلة المحفوظة",
                        "/search-favorites - البحث في المفضلة",
                        "/clear-favorites - مسح المفضلة",
                    ]),
                    ("⚙️ الإعدادات والتنبيهات", [
                        "/set-city - تعيين مدينة السيرفر",
                        "/settings - إعدادات السيرفر",
                        "/my-city - مدينتك المفضلة",
                        "/my-settings - إعداداتك الشخصية",
                        "/remind-on - تفعيل تنبيهات الأذان",
                        "/remind-off - إيقاف التنبيهات",
                        "/azkar-on - تفعيل الأذكار التلقائية",
                        "/azkar-off - إيقاف الأذكار التلقائية",
                        "/events - المناسبات الإسلامية",
                    ]),
                    ("ℹ️ معلومات", [
                        "/bot-info - معلومات البوت والإحصائيات",
                        "/ping - اختبار سرعة البوت",
                        "/my-stats - إحصائياتك الشخصية",
                        "/report - الإبلاغ عن مشكلة",
                        "/help - عرض جميع الأوامر",
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
                        "/surah-ayah - آية محددة من سورة",
                        "/surah - سورة كاملة",
                        "/surah-select - اختيار سورة من قائمة",
                        "/search-quran - بحث في القرآن",
                        "/quran-list - عرض جميع السور",
                        "/tafsir - التفسير الميسر",
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
                        "/athan - الصلاة القادمة",
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
                    ("🤲 الأذكار والأدعية", [
                        "/morning-azkar - أذكار الصباح",
                        "/evening-azkar - أذكار المساء",
                        "/sleep-azkar - أذكار النوم",
                        "/hadith - حديث شريف عشوائي",
                        "/hadith-list - قائمة الأحاديث",
                        "/dua - دعاء عشوائي",
                        "/dua-list - قائمة الأدعية",
                        "/azkar-count - عداد الذكر التفاعلي",
                        "/favorites - عرض المفضلة المحفوظة",
                        "/search-favorites - البحث في المفضلة",
                        "/clear-favorites - مسح المفضلة",
                    ]),
                ]
            },
            "settings": {
                "title": "⚙️ أوامر الإعدادات",
                "emoji": "⚙️",
                "color": 0x95A5A6,
                "commands": [
                    ("⚙️ الإعدادات والتنبيهات", [
                        "/set-city - تعيين مدينة السيرفر",
                        "/settings - إعدادات السيرفر",
                        "/my-city - مدينتك المفضلة",
                        "/my-settings - إعداداتك الشخصية",
                        "/remind-on - تفعيل تنبيهات الأذان",
                        "/remind-off - إيقاف التنبيهات",
                        "/azkar-on - تفعيل الأذكار التلقائية",
                        "/azkar-off - إيقاف الأذكار التلقائية",
                        "/events - المناسبات الإسلامية",
                    ]),
                    ("ℹ️ معلومات", [
                        "/bot-info - معلومات البوت والإحصائيات",
                        "/ping - اختبار سرعة البوت",
                        "/my-stats - إحصائياتك الشخصية",
                        "/report - الإبلاغ عن مشكلة",
                        "/help - عرض جميع الأوامر",
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

        for section_name, cmds in cat['commands']:
            embed.add_field(
                name=section_name,
                value="\n".join(cmds),
                inline=False,
            )

        embed.add_field(
            name="💡 نصائح",
            value="• اكتب `/` لعرض جميع الأوامر\n• استخدم autocomplete للبحث السريع\n• اضغط على الأوامر لرؤية التفاصيل",
            inline=False,
        )
        embed.set_footer(text="المساعدة • MuslimBot")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="report", description="📝 الإبلاغ عن مشكلة أو اقتراح")
    @app_commands.describe(message="رسالتك أو المشكلة")
    async def report(self, interaction: discord.Interaction, message: str):
        embed = discord.Embed(
            title="📝 تم استلام بلاغك",
            description=f"شكراً لك على إبلاغك!\n\n**رسالتك:**\n{message}\n\nسنقوم بمراجعة بلاغك في أقرب وقت.",
            color=0x27AE60,
        )
        embed.set_thumbnail(url=BOT_ICON)
        embed.add_field(
            name="👤 المبلّغ",
            value=f"{interaction.user.mention}",
            inline=True,
        )
        embed.add_field(
            name="📅 التاريخ",
            value=f"{discord.utils.format_dt(discord.utils.utcnow())}",
            inline=True,
        )
        embed.set_footer(text="مسلم بوت • MuslimBot")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="my-stats", description="📊 إحصائيات استخدامك الشخصية")
    async def my_stats(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        from utils.favorites import get_favorites
        from utils.azkar_counter import get_counter
        
        favorites_count = len(get_favorites(interaction.user.id))
        counter = get_counter(interaction.user.id)
        
        embed = discord.Embed(
            title="📊 إحصائياتك الشخصية",
            description=f"إحصائيات استخدامك لمسلم بوت",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=BOT_ICON)
        embed.add_field(
            name="⭐ المفضلة",
            value=f"**{favorites_count}** عنصر محفوظ",
            inline=True,
        )
        embed.add_field(
            name="🔢 عداد الذكر",
            value=f"**{counter}** ذكر",
            inline=True,
        )
        embed.add_field(
            name="👤 المستخدم",
            value=f"**{interaction.user.name}**\n{interaction.user.mention}",
            inline=False,
        )
        embed.set_footer(text="مسلم بوت • MuslimBot")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="🏓 اختبار سرعة استجابة البوت")
    async def ping(self, interaction: discord.Interaction):
        ping_ms = round(self.bot.latency * 1000)
        color = 0x27AE60 if ping_ms < 100 else 0xF39C12 if ping_ms < 300 else 0xE74C3C
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"سرعة الاستجابة: **{ping_ms}ms**",
            color=color,
        )
        embed.set_footer(text="مسلم بوت • MuslimBot")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bot-info", description="ℹ️ عرض معلومات البوت والإحصائيات")
    async def bot_info(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_used = ram.used / (1024**3)
        ram_total = ram.total / (1024**3)
        
        # Get bot info
        guild_count = len(self.bot.guilds)
        user_count = sum(g.member_count for g in self.bot.guilds)
        ping = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="ℹ️ معلومات البوت",
            description="مسلم بوت - بوت إسلامي شامل",
            color=0x3498DB,
        )
        embed.set_thumbnail(url=BOT_ICON)
        
        embed.add_field(
            name="📊 الإحصائيات",
            value=f"**السيرفرات:** {guild_count}\n**المستخدمين:** {user_count:,}\n**البنج:** {ping}ms",
            inline=True,
        )
        embed.add_field(
            name="💻 النظام",
            value=f"**النظام:** {platform.system()}\n**بايثون:** {platform.python_version()}\n**CPU:** {cpu_percent}%\n**الرام:** {ram_used:.1f}GB / {ram_total:.1f}GB",
            inline=True,
        )
        embed.add_field(
            name="🔧 المعلومات",
            value=f"**الإصدار:** 2.0\n**المطور:** MuslimBot Team\n**اللغة:** Python + discord.py",
            inline=False,
        )
        embed.set_footer(text="مسلم بوت • MuslimBot")
        
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))
