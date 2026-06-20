import os
import asyncio
import aiohttp
from datetime import datetime
import pytz
import time
import gc

# ============= قراءة المتغيرات =============
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # هذا للمتابعات في القناة فقط

if not TOKEN or not CHAT_ID:
    print("❌ خطأ: تأكد من إضافة BOT_TOKEN و CHAT_ID في Secrets")
    exit()

RIYADH_TZ = pytz.timezone('Asia/Riyadh')

STOCK_NAMES = {
    "2222": "أرامكو السعودية", "1211": "معادن", "7010": "اس تي سي", "2010": "سابك",
    "2082": "أكوا", "4013": "سليمان الحبيب", "5110": "السعودية للطاقة", "2020": "سابك للمغذيات الزراعية",
    "7203": "علم", "4280": "المملكة", "7020": "إتحاد إتصالات", "1050": "بي اس اف",
    "2280": "المراعي", "2380": "بترو رابغ", "4030": "البحري", "8210": "بوبا العربية",
    "7202": "سلوشنز", "4325": "مسار", "8010": "التعاونية", "2223": "لوبريف",
    "2382": "أديس", "4190": "جرير", "4142": "كابلات الرياض", "1303": "الصناعات الكهربائية",
    "2290": "ينساب", "4250": "جبل عمر", "1030": "الإستثمار", "1111": "مجموعة تداول",
    "4263": "سال", "4002": "المواساة", "4164": "النهدي", "8313": "رسن",
    "8230": "تكافل الراجحي", "4200": "الدريس", "4015": "جمجوم فارما", "4004": "دله الصحية",
    "1212": "أسترا الصناعية", "2310": "سبكيم العالمية", "4090": "طيبة", "7030": "زين السعودية",
    "2250": "المجموعة السعودية", "2083": "مرافق", "4220": "إعمار", "2050": "مجموعة صافولا",
    "4264": "طيران ناس", "4017": "فقيه الطبية", "2350": "كيان السعودية", "2381": "الحفر العربية",
    "4321": "سينومي سنترز", "4072": "مجموعة إم بي سي", "2230": "الكيميائية", "2270": "سدافكو",
    "2320": "البابطين", "1321": "أنابيب الشرق", "2330": "المتقدمة", "2060": "التصنيع",
    "1322": "أماك", "4210": "الأبحاث والإعلام", "6004": "كاتريون", "4020": "العقارية",
    "4322": "رتال", "4031": "الخدمات الأرضية", "1810": "سيرا", "2080": "الغاز القابضة",
    "4003": "إكسترا", "4291": "الوطنية للتعليم", "7200": "ام آي اس", "4161": "بن داود",
    "4084": "دراية", "4001": "أسواق ع العثيم", "4071": "العربية", "4018": "الموسى",
    "6010": "نادك", "4005": "رعاية", "8200": "الإعادة السعودية", "4007": "الحمادي",
    "1830": "لجام للرياضة", "4150": "التعمير", "2081": "الخريف", "4019": "اس ام سي للرعاية الصحية",
    "4310": "مدينة المعرفة", "4162": "المنجم", "4260": "بدجت السعودية", "4163": "الدواء",
    "4050": "ساسكو", "4165": "الماجد للعود", "2070": "الدوائية", "7040": "قو للإتصالات",
    "2190": "سيسكو القابضة", "4009": "السعودي الألماني الصحية", "1831": "مهارة", "2283": "المطاحن الأولى",
    "4083": "تسهيل", "1320": "أنابيب السعودية", "6017": "جاهز", "2040": "الخزف السعودي",
    "4146": "جاز", "1302": "بوان", "1834": "سماسكو", "2084": "مياهنا",
    "2285": "المطاحن العربية", "4192": "السيف غاليري", "2284": "المطاحن الحديثة", "2286": "المطاحن الرابعة",
    "4292": "عطاء", "8030": "ميدغلف للتأمين", "7204": "توبي", "4016": "أفالون فارما",
    "2300": "صناعة الورق", "2240": "صناعات", "1833": "الموارد", "2170": "اللجين",
    "1304": "اليمامة للحديد", "4262": "لومي", "4261": "ذيب", "4240": "سينومي ريتيل",
    "4193": "نايس ون", "8250": "جي آي جي", "1202": "مبكو", "2200": "أنابيب",
    "1183": "سهل", "4012": "الأصيل", "4323": "سمو", "4040": "سابتكو",
    "4320": "الأندلس", "8060": "ولاء", "4143": "تالكو", "7211": "عزم",
    "2370": "مسك", "4110": "باتك", "6070": "الجوف", "1835": "تمكين",
    "2110": "الكابلات السعودية", "2281": "تنمية", "4081": "النايفات", "2150": "زجاج",
    "4080": "سناد القابضة", "4230": "البحر الأحمر", "2140": "أيان", "6001": "حلواني إخوان",
    "2282": "نقي", "6014": "الآمار", "2120": "متطورة", "1323": "يو سي آي سي",
    "8070": "الدرع العربي", "4290": "الخليج للتدريب", "4170": "شمس", "1214": "شاكر",
    "6002": "هرفي للأغذية", "1182": "أملاك", "4014": "دار المعدات", "2340": "ارتيكس",
    "4191": "أبو معطي", "4008": "ساكو", "4144": "رؤوم", "6018": "الأندية للرياضة",
    "8012": "جزيرة تكافل", "4145": "أو جي سي", "8240": "تْشب", "2287": "إنتاج",
    "2288": "نفوذ", "4180": "مجموعة فتيحي", "1210": "بي سي آي", "2030": "المصافي",
    "4148": "الوسائل الصناعية", "4011": "لازوردي", "1820": "بان", "4324": "بنان",
    "2160": "أميانتيت", "8120": "إتحاد الخليج الأهلية", "4006": "أسواق المزرعة", "3007": "الواحة",
    "4082": "مرنة", "4051": "باعظيم", "8040": "متكاملة", "8300": "الوطنية",
    "2360": "الفخارية", "8050": "سلامة", "4141": "العمران", "6040": "تبوك الزراعية",
    "1213": "نسيج", "4160": "ثمار", "8150": "أسيج", "4265": "شري",
    "4147": "سي جي إس", "6019": "المسار الشامل", "1324": "صالح الراشد", "7205": "دي بي اس",
    "4326": "الماجدية"
}

ALL_TICKERS = [f"{code}.SR" for code in STOCK_NAMES.keys()]

BANKS_EXCLUDED = ["1060.SR", "1080.SR", "1120.SR", "1140.SR", "1150.SR", "1211.SR", "1301.SR", "1320.SR", "1350.SR"]
CEMENTS = ["3001.SR", "3002.SR", "3003.SR", "3004.SR", "3005.SR", "3007.SR", "3008.SR", "3010.SR", "3011.SR", "3012.SR", "3030.SR", "3080.SR", "3090.SR", "3091.SR", "3092.SR"]
REITS = ["4330.SR", "4331.SR", "4332.SR", "4333.SR", "4334.SR", "4335.SR", "4336.SR", "4337.SR", "4338.SR", "4339.SR", "4340.SR", "4341.SR", "4342.SR", "4343.SR", "4344.SR", "4345.SR"]
EXCLUDED = set(BANKS_EXCLUDED + CEMENTS + REITS)

ACTIVE_TICKERS = [t for t in ALL_TICKERS if t not in EXCLUDED]

alert_counters = {}
tracker = {}
stock_followup = {}
daily_opportunities = []

MIN_PRICE = 1.0
MAX_PRICE = 150.0
MIN_VOLUME = 1000000
MIN_MOMENTUM = 2.5
MIN_VOLUME_RATIO = 2.0
RSI_MIN = 45
RSI_MAX = 65
PREVIOUS_HIGH_LOOKBACK = 90

TARGET_1_PCT = 0.05
TARGET_2_PCT = 0.12
TARGET_3_PCT = 0.25
TRAILING_STOP_PCT = 0.03

market_open_sent = False
market_close_sent = False
current_date = None

def get_stock_display(ticker):
    code = ticker.replace(".SR", "")
    name = STOCK_NAMES.get(code, code)
    return f"{name} ({code})"

async def send_msg(session, msg, chat_id=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id or CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                print(f"فشل الإرسال: {await resp.text()}")
    except Exception as e:
        print(f"خطأ: {e}")

async def send_inline_menu(session, chat_id):
    """إرسال قائمة الأزرار التفاعلية"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    keyboard = {
        "inline_keyboard": [
            [{"text": "📈 اختراق قمة 90 يوم", "callback_data": "breakouts"}],
            [{"text": "📊 فوق المتوسط 50", "callback_data": "ma50"}],
            [{"text": "📉 فوق المتوسط 200", "callback_data": "ma200"}],
            [{"text": "🎣 انعكاسات صاعدة (قاع)", "callback_data": "reversal_up"}],
            [{"text": "🔥 حجم استثنائي", "callback_data": "volume"}],
            [{"text": "📊 تحليل سهم (اكتب الكود)", "callback_data": "analyze"}]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": "📊 *قائمة تصنيفات الأسهم*\nاختر الفئة التي تريد عرضها:",
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    }
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status != 200:
                print(f"فشل إرسال القائمة: {await resp.text()}")
    except Exception as e:
        print(f"خطأ: {e}")

async def fetch_all_stocks_data():
    """جلب بيانات جميع الأسهم للتصنيف"""
    results = []
    for ticker in ACTIVE_TICKERS:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
            headers = {"User-Agent": "Mozilla/5.0"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("chart", {}).get("result"):
                            result = data["chart"]["result"][0]
                            meta = result.get("meta", {})
                            quote = result.get("indicators", {}).get("quote", [{}])[0]
                            
                            current_price = meta.get("regularMarketPrice", 0)
                            previous_close = meta.get("previousClose", current_price)
                            current_volume = meta.get("regularMarketVolume", 0)
                            
                            if current_price > 0 and current_volume > 0:
                                closes = quote.get("close", [])
                                highs = quote.get("high", [])
                                lows = quote.get("low", [])
                                volumes = quote.get("volume", [])
                                
                                change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                                avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else current_volume
                                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                                rsi = calculate_rsi(closes)
                                ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
                                ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else current_price
                                ma200 = sum(closes[-200:]) / 200 if len(closes) >= 200 else current_price
                                high_90d = max(highs[-90:]) if len(highs) >= 90 else current_price
                                low_30d = min(lows[-30:]) if len(lows) >= 30 else current_price
                                
                                results.append({
                                    "display": get_stock_display(ticker),
                                    "price": current_price,
                                    "change": change,
                                    "volume_ratio": volume_ratio,
                                    "rsi": rsi,
                                    "ma20": ma20,
                                    "ma50": ma50,
                                    "ma200": ma200,
                                    "high_90d": high_90d,
                                    "low_30d": low_30d,
                                    "is_breakout_90d": current_price > high_90d,
                                    "is_above_ma50": current_price > ma50,
                                    "is_above_ma200": current_price > ma200
                                })
        except:
            pass
        await asyncio.sleep(0.3)
    return results

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50
    gains, losses = [], []
    for i in range(1, period + 1):
        change = closes[-i] - closes[-i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_targets(price):
    return (price * (1 + TARGET_1_PCT), price * (1 + TARGET_2_PCT), price * (1 + TARGET_3_PCT))

def get_trailing_stop(current_price, highest_price):
    return highest_price * (1 - TRAILING_STOP_PCT)

# ============= معالجة ضغط الأزرار =============
async def handle_callback_query(session, callback_data, chat_id, message_id):
    await send_msg(session, "⏳ جاري مسح السوق وتصنيف الأسهم... يرجى الانتظار (قد يستغرق 30-60 ثانية).", chat_id)
    
    data = await fetch_all_stocks_data()
    
    if callback_data == "breakouts":
        filtered = [s for s in data if s["is_breakout_90d"] and s["change"] >= 2.0]
        filtered.sort(key=lambda x: x["change"], reverse=True)
        title = "📈 *أفضل 10 أسهم اخترقت قمة 90 يوم*"
        if not filtered:
            await send_msg(session, "⚠️ لا توجد أسهم اخترقت قمة 90 يوم اليوم.", chat_id)
            return
        
    elif callback_data == "ma50":
        filtered = [s for s in data if s["is_above_ma50"] and s["change"] >= 1.5]
        filtered.sort(key=lambda x: x["change"], reverse=True)
        title = "📈 *أفضل 10 أسهم فوق المتوسط 50*"
        if not filtered:
            await send_msg(session, "⚠️ لا توجد أسهم فوق المتوسط 50 بزخم حالياً.", chat_id)
            return
        
    elif callback_data == "ma200":
        filtered = [s for s in data if s["is_above_ma200"] and s["change"] >= 1.0]
        filtered.sort(key=lambda x: x["change"], reverse=True)
        title = "📈 *أفضل 10 أسهم فوق المتوسط 200*"
        if not filtered:
            await send_msg(session, "⚠️ لا توجد أسهم فوق المتوسط 200 بزخم حالياً.", chat_id)
            return
        
    elif callback_data == "reversal_up":
        filtered = [s for s in data if s["price"] <= (s["low_30d"] * 1.05) and s["change"] >= 2.5 and s["volume_ratio"] >= 1.8 and s["rsi"] < 50]
        filtered.sort(key=lambda x: x["change"], reverse=True)
        title = "🎣 *أفضل 5 فرص انعكاس صاعد (قاع)*"
        if not filtered:
            await send_msg(session, "⚠️ لا توجد أسهم بانعكاس صاعد واضح اليوم.", chat_id)
            return
        
    elif callback_data == "volume":
        filtered = [s for s in data if s["volume_ratio"] >= 3.0 and s["change"] >= 1.0]
        filtered.sort(key=lambda x: x["volume_ratio"], reverse=True)
        title = "🔥 *أفضل 5 أسهم بحجم استثنائي (3x المتوسط)*"
        if not filtered:
            await send_msg(session, "⚠️ لا توجد أسهم بحجم استثنائي حالياً.", chat_id)
            return
    
    elif callback_data == "analyze":
        await send_msg(session, "📊 *لتحليل سهم:*\nأرسل الأمر: `/تحليل [الكود]`\nمثال: `/تحليل 2222`", chat_id)
        return

    # بناء الرسالة
    msg = f"{title}\n📅 {datetime.now(RIYADH_TZ).strftime('%Y-%m-%d %H:%M')}\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    limit = 10 if callback_data in ["breakouts", "ma50", "ma200"] else 5
    for i, s in enumerate(filtered[:limit], 1):
        if callback_data in ["breakouts", "ma50", "ma200"]:
            msg += f"{i}. *{s['display']}*\n   💵 {s['price']:.2f} ريال | زخم +{s['change']:.2f}%\n   📊 RSI: {s['rsi']:.0f} | حجم: {s['volume_ratio']:.1f}x\n\n"
        elif callback_data == "reversal_up":
            msg += f"{i}. *{s['display']}*\n   💵 {s['price']:.2f} ريال | صعود +{s['change']:.2f}%\n   📊 حجم {s['volume_ratio']:.1f}x | RSI: {s['rsi']:.0f}\n   🛑 وقف: {s['low_30d']*0.97:.2f}\n\n"
        elif callback_data == "volume":
            msg += f"{i}. *{s['display']}*\n   💵 {s['price']:.2f} ريال | زخم +{s['change']:.2f}%\n   📊 الحجم: {s['volume_ratio']:.1f}x المتوسط\n\n"
    
    msg += "\n━━━━━━━━━━━━━━━━━━━━━\nللعودة للقائمة الرئيسية، أرسل `/start` أو اكتب `قائمة`."
    await send_msg(session, msg, chat_id)

# ============= معالجة الأوامر النصية =============
async def handle_analysis_command(session, chat_id, ticker_code):
    ticker = f"{ticker_code}.SR"
    if ticker not in ALL_TICKERS:
        await send_msg(session, f"❌ الكود {ticker_code} غير صحيح أو غير موجود.", chat_id)
        return
    
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    await send_msg(session, f"❌ تعذر جلب بيانات {ticker_code}.", chat_id)
                    return
                data = await resp.json()
                if not data.get("chart", {}).get("result"):
                    await send_msg(session, f"❌ تعذر جلب بيانات {ticker_code}.", chat_id)
                    return
                result = data["chart"]["result"][0]
                meta = result.get("meta", {})
                quote = result.get("indicators", {}).get("quote", [{}])[0]
                current_price = meta.get("regularMarketPrice", 0)
                previous_close = meta.get("previousClose", current_price)
                current_volume = meta.get("regularMarketVolume", 0)
                if current_price <= 0 or current_volume <= 0:
                    await send_msg(session, f"❌ بيانات السهم غير متاحة.", chat_id)
                    return
                closes = quote.get("close", [])
                highs = quote.get("high", [])
                lows = quote.get("low", [])
                change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                avg_volume = sum(quote.get("volume", [])[-20:]) / 20 if len(quote.get("volume", [])) >= 20 else current_volume
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                rsi = calculate_rsi(closes)
                ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
                high_90d = max(highs[-90:]) if len(highs) >= 90 else current_price
                low_30d = min(lows[-30:]) if len(lows) >= 30 else current_price
                
                display = get_stock_display(ticker)
                target1, target2, target3 = get_targets(current_price)
                trailing_stop = get_trailing_stop(current_price, current_price)
                
                is_breakout = current_price > high_90d
                is_reversal = (current_price <= low_30d * 1.05 and change >= 2.0 and volume_ratio >= 1.8 and rsi < 45)
                
                msg = f"""📊 *تحليل شامل لـ {display}*

💰 السعر: {current_price:.2f} ريال | التغيير: +{change:.2f}%
📊 الحجم: {current_volume:,} (نسبة {volume_ratio:.1f}x)
📉 RSI: {rsi:.0f} | المتوسط 20: {ma20:.2f}

━━━━━━━━━━━━━━━━━━━━━
*📈 اختراق القمة:* {"✅ متاحة" if is_breakout else "❌ غير متاحة"}
🎯 أهداف: {target1:.2f} / {target2:.2f} / {target3:.2f}
🛑 وقف: {trailing_stop:.2f}

*🎣 صيد القاع:* {"✅ فرصة" if is_reversal else "❌ غير متاحة"}
🛑 وقف صارم: {low_30d*0.97:.2f}

━━━━━━━━━━━━━━━━━━━━━
📌 القمة السابقة: {high_90d:.2f} | القاع 30 يوم: {low_30d:.2f}"""
                await send_msg(session, msg, chat_id)
    except:
        await send_msg(session, f"❌ خطأ في جلب البيانات.", chat_id)

# ============= الدالة الرئيسية =============
async def main():
    global market_open_sent, market_close_sent, current_date, daily_opportunities
    
    async with aiohttp.ClientSession() as session:
        # رسالة بدء التشغيل للقناة
        await send_msg(session, f"✅ *بوت التصنيفات والتحليل يعمل الآن*\n\n📊 {len(ACTIVE_TICKERS)} شركة تحت المراقبة\n📈 استراتيجية اختراق قمة / متوسطات\n\n🤖 للبدء، أرسل `/start` أو `قائمة` في المحادثة الخاصة.")
        
        last_update_id = 0
        
        while True:
            now_riyadh = datetime.now(RIYADH_TZ)
            market_open_time = now_riyadh.replace(hour=10, minute=0, second=0)
            market_close_time = now_riyadh.replace(hour=15, minute=0, second=0)
            
            if current_date != now_riyadh.date():
                current_date = now_riyadh.date()
                market_open_sent = False
                market_close_sent = False
                daily_opportunities = []
            
            if not market_open_sent and now_riyadh >= market_open_time and now_riyadh < market_close_time:
                market_open_sent = True
                await send_msg(session, f"🔔 *فتح السوق*\n⏰ {now_riyadh.strftime('%H:%M:%S')}")
            
            if not market_close_sent and now_riyadh >= market_close_time:
                market_close_sent = True
                await send_msg(session, f"🔔 *إغلاق السوق*\n⏰ {now_riyadh.strftime('%H:%M:%S')}\n📊 جاري الملخص...")
                if daily_opportunities:
                    daily_opportunities.sort(key=lambda x: x['strength'], reverse=True)
                    top_10 = daily_opportunities[:10]
                    msg = f"📊 *ملخص نهاية اليوم - أفضل {len(top_10)} فرصة*\n"
                    for i, opp in enumerate(top_10, 1):
                        msg += f"{i}. {opp['display_name']} | قوة: {opp['strength']}/100\n"
                    await send_msg(session, msg)
                daily_opportunities = []
            
            # ============= معالجة الرسائل والأزرار =============
            try:
                updates_url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
                async with session.get(updates_url) as resp:
                    if resp.status == 200:
                        updates_data = await resp.json()
                        if updates_data.get("ok"):
                            result = updates_data.get("result", [])
                            for update in result:
                                if update["update_id"] >= last_update_id:
                                    last_update_id = update["update_id"] + 1
                                
                                # معالجة ضغط الأزرار (Callback Query)
                                if "callback_query" in update:
                                    cq = update["callback_query"]
                                    chat_id = cq["message"]["chat"]["id"]
                                    data = cq["data"]
                                    message_id = cq["message"]["message_id"]
                                    await handle_callback_query(session, data, chat_id, message_id)
                                    continue
                                
                                # معالجة الرسائل النصية
                                if "message" in update and "text" in update["message"]:
                                    text = update["message"]["text"].strip()
                                    chat_id = update["message"]["chat"]["id"]
                                    
                                    text_lower = text.lower()
                                    
                                    # قائمة الأوامر
                                    if text_lower == "/start" or text_lower == "قائمة":
                                        await send_inline_menu(session, chat_id)
                                    
                                    elif text_lower.startswith("/تحليل") or text_lower.startswith("تحليل"):
                                        parts = text.split()
                                        if len(parts) > 1 and parts[1].isdigit():
                                            await handle_analysis_command(session, chat_id, parts[1])
                                        else:
                                            await send_msg(session, "📌 *لتحليل سهم:* أرسل `/تحليل [الكود]`\nمثال: `/تحليل 2222`", chat_id)
                                    
                                    elif text_lower.startswith("/مساعده") or text_lower == "مساعده":
                                        await send_inline_menu(session, chat_id)
                                    
                                    else:
                                        # إذا كتب المستخدم كلمة غير معروفة، يرسل له القائمة
                                        if len(text) > 1:
                                            await send_inline_menu(session, chat_id)
            except Exception as e:
                print(f"خطأ في جلب الرسائل: {e}")
            
            # ============= مراقبة السوق للتنبيهات =============
            if market_open_time <= now_riyadh <= market_close_time:
                # (تم إبقاء منطق المتابعة للقناة كما هو)
                for i, ticker in enumerate(ACTIVE_TICKERS):
                    try:
                        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                        headers = {"User-Agent": "Mozilla/5.0"}
                        async with aiohttp.ClientSession() as session_inner:
                            async with session_inner.get(url, headers=headers) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    if data.get("chart", {}).get("result"):
                                        result = data["chart"]["result"][0]
                                        meta = result.get("meta", {})
                                        quote = result.get("indicators", {}).get("quote", [{}])[0]
                                        current_price = meta.get("regularMarketPrice", 0)
                                        previous_close = meta.get("previousClose", current_price)
                                        current_volume = meta.get("regularMarketVolume", 0)
                                        if current_price > 0 and current_volume > 0:
                                            closes = quote.get("close", [])
                                            highs = quote.get("high", [])
                                            change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                                            avg_volume = sum(quote.get("volume", [])[-20:]) / 20 if len(quote.get("volume", [])) >= 20 else current_volume
                                            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                                            rsi = calculate_rsi(closes)
                                            ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
                                            high_90d = max(highs[-90:]) if len(highs) >= 90 else current_price
                                            
                                            is_breakout_90d = current_price > high_90d
                                            is_high_volume = volume_ratio >= MIN_VOLUME_RATIO
                                            is_good_momentum = change >= MIN_MOMENTUM
                                            is_good_rsi = RSI_MIN <= rsi <= RSI_MAX
                                            
                                            if is_breakout_90d and is_high_volume and is_good_momentum and is_good_rsi:
                                                display_name = get_stock_display(ticker)
                                                strength = 70
                                                daily_opportunities.append({'display_name': display_name, 'strength': strength})
                    except:
                        pass
                    if (i + 1) % 20 == 0:
                        gc.collect()
                        await asyncio.sleep(0.5)
                gc.collect()
            
            await asyncio.sleep(60)

if __name__ == "__main__":
    print(f"بدء البوت... {len(ACTIVE_TICKERS)} شركة")
    asyncio.run(main())
