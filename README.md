# 🕌 Muslim Discord Bot

بوت ديسكورد إسلامي يقدم أوقات الصلاة، الأذكار، آيات قرآنية، أحاديث نبوية، أدعية، والمزيد.

## ✨ المميزات

- 🕌 **أوقات الصلاة** - عرض مواقيت الصلاة لأي مدينة في العالم
- ⏰ **الصلاة القادمة** - معرفة الوقت المتبقي على الصلاة التالية
- 📅 **التاريخ الهجري** - عرض التاريخ الهجري الحالي
- ☀️ **أذكار الصباح** - أذكار الصباح من الكتاب والسنة
- 🌇 **أذكار المساء** - أذكار المساء من الكتاب والسنة
- 🌙 **أذكار النوم** - أذكار قبل النوم
- 📖 **آية قرآنية** - آية عشوائية أو آية محددة
- 📖 **حديث شريف** - حديث عشوائي من الأحاديث الصحيحة
- 🤲 **دعاء** - دعاء عشوائي من القرآن الكريم
- 🔔 **تنبيهات الصلاة** - تنبيه تلقائي عند حلول وقت كل صلاة

## 🚀 التشغيل

### 1. المتطلبات
- Python 3.11+
- Discord Bot Token

### 2. التثبيت

```bash
pip install -r requirements.txt
```

### 3. الإعداد

انسخ ملف `.env.example` إلى `.env` وعدّل القيم:

```env
DISCORD_TOKEN=your_bot_token_here
PRAYER_CITY=Cairo
PRAYER_COUNTRY=EG
PRAYER_METHOD=5
REMINDER_CHANNEL_ID=your_channel_id_here
```

**طرق حساب أوقات الصلاة (PRAYER_METHOD):**
| الرقم | الطريقة |
|-------|---------|
| 1 | University of Islamic Sciences, Karachi |
| 2 | Islamic Society of North America (ISNA) |
| 3 | Muslim World League |
| 4 | Umm Al-Qura University, Makkah |
| 5 | Egyptian General Authority of Survey (افتراضي) |
| 7 | Institute of Geophysics, University of Tehran |
| 8 | Gulf Region |
| 9 | Kuwait |
| 10 | Qatar |
| 11 | Majlis Ugama Islam Singapura |
| 12 | UOIF (France) |
| 13 | Diyanet İşleri Başkanlığı (Turkey) |
| 14 | Spiritual Administration of Muslims of Russia |

### 4. تشغيل البوت

```bash
python bot.py
```

## 📋 الأوامر

| الأمر | الوصف |
|-------|-------|
| `/salah` | 🕌 عرض أوقات الصلاة |
| `/salah city:Dubai country:AE` | أوقات الصلاة لمدينة محددة |
| `/athan` | ⏰ الصلاة القادمة والوقت المتبقي |
| `/hijri` | 📅 التاريخ الهجري |
| `/morning-azkar` | ☀️ أذكار الصباح |
| `/evening-azkar` | 🌇 أذكار المساء |
| `/sleep-azkar` | 🌙 أذكار النوم |
| `/ayah` | 📖 آية قرآنية عشوائية |
| `/surah-ayah surah:1 ayah:1` | 📖 آية محددة |
| `/hadith` | 📖 حديث شريف عشوائي |
| `/dua` | 🤲 دعاء عشوائي |
| `/remind-on` | 🔔 تفعيل تنبيهات الصلاة في القناة |
| `/remind-off` | 🔕 إيقاف التنبيهات |
| `/azkar-on` | 🔔 تفعيل إرسال الأذكار تلقائياً |
| `/azkar-off` | 🔕 إيقاف الأذكار التلقائية |
| `/events` | 📅 عرض المناسبات الإسلامية القادمة |
| `/quran-play` | 🔊 تشغيل آية قرآنية في الفويس |
| `/quran-stop` | ⏹️ إيقاف القرآن والخروج من الفويس |
| `/reciters` | 🎤 عرض القُرّاء المتاحين |
| `/tafsir surah:1 ayah:1` | 📖 تفسير ميسر لآية |
| `/allah-name` | ✨ اسم من أسماء الله الحسنى |
| `/set-city city:Cairo country:EG` | ⚙️ حفظ مدينتك للسيرفر |
| `/settings` | ⚙️ عرض إعدادات السيرفر |

## 📁 هيكل المشروع

```
discord-bot/
├── bot.py                  # الملف الرئيسي
├── requirements.txt        # المكتبات
├── .env.example           # نموذج الإعدادات
├── cogs/
│   ├── prayer.py          # أوامر الصلاة والتاريخ الهجري
│   ├── azkar_cog.py       # أوامر الأذكار والأحاديث والأدعية
│   ├── quran_cog.py       # أوامر القرآن نصي
│   ├── quran_voice.py     # القرآن صوتي في الفويس
│   ├── tafsir_cog.py      # تفسير الآيات
│   ├── settings_cog.py    # إعدادات السيرفر
│   ├── reminders.py       # تنبيهات الصلاة التلقائية
│   └── auto_azkar.py      # أذكار تلقائية + مناسبات
├── utils/
│   ├── prayer_times.py    # API أوقات الصلاة (Aladhan)
│   ├── azkar.py           # تحميل وتنسيق الأذكار
│   ├── quran.py           # API القرآن (alquran.cloud)
│   ├── quran_audio.py     # روابط القرآن الصوتي
│   ├── tafsir.py          # API التفسير
│   ├── events.py          # المناسبات الإسلامية
│   └── server_settings.py # إعدادات السيرفر
└── data/
    ├── azkar_morning.json  # أذكار الصباح
    ├── azkar_evening.json  # أذكار المساء
    ├── azkar_sleep.json    # أذكار النوم
    ├── hadith.json         # الأحاديث
    ├── dua.json            # الأدعية
    ├── islamic_events.json # المناسبات الإسلامية
    ├── reciters.json       # القُرّاء
    └── allah_names.json    # أسماء الله الحسنى
```

## 🔗 APIs المستخدمة

- [Aladhan Prayer Times API](https://aladhan.com/prayer-times-api) - أوقات الصلاة والتاريخ الهجري
- [Al Quran Cloud API](https://alquran.cloud/api) - آيات القرآن الكريم

لا تحتاج أي API keys - كل الـ APIs مجانية!
