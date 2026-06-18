import os
import asyncio
import aiohttp
from datetime import datetime
import pytz
import time
import gc

# ============= قراءة المتغيرات من Secrets =============
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

# ============= إعدادات الاستراتيجية =============
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

# ============= الدوال المساعدة =============
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

def calculate_strength_score(change, volume_ratio, rsi, is_breakout_20d, is_breakout_60d, is_above_ma20):
    score = 0
    score += min(change * 12, 30)
    score += min(volume_ratio * 15, 30)
    score += min((rsi - 45) * 2, 20) if rsi > 45 else 0
    if is_breakout_20d:
        score += 10
    if is_breakout_60d:
        score += 15
    if is_above_ma20:
        score += 5
    return min(score, 100)

def get_targets(price):
    return (price * (1 + TARGET_1_PCT), price * (1 + TARGET_2_PCT), price * (1 + TARGET_3_PCT))

def get_trailing_stop(current_price, highest_price):
    return highest_price * (1 - TRAILING_STOP_PCT)

# ============= دوال التحليل والاستراتيجيات =============
async def handle_analysis_command(session, chat_id, ticker_code=None):
    """تحليل سهم معين أو عرض نظرة عامة"""
    if ticker_code:
        ticker = f"{ticker_code}.SR"
        if ticker not in ALL_TICKERS:
            await send_msg(session, f"❌ الكود {ticker_code} غير صحيح أو غير موجود.", chat_id)
            return
        
        data = await fetch_ticker_data(ticker)
        if not data:
            await send_msg(session, f"❌ تعذر جلب بيانات {ticker_code}. حاول لاحقاً.", chat_id)
            return
        
        display = get_stock_display(ticker)
        price = data["price"]
        change = data["change"]
        volume = data["volume"]
        volume_ratio = data["volume_ratio"]
        rsi = data["rsi"]
        strength = data["strength"]
        previous_high = data["previous_high"]
        
        target1, target2, target3 = get_targets(price)
        trailing_stop = get_trailing_stop(price, price)
        
        s_text = "💥 قوي جداً" if strength >= 75 else "🚀 قوي" if strength >= 60 else "📈 متوسط"
        
        msg = f"""📊 *تحليل {display}*

💰 السعر: {price:.2f} ريال
📈 التغيير: +{change:.2f}%
📊 الحجم: {volume:,} | نسبة: {volume_ratio:.1f}x
📉 RSI: {rsi:.0f}
💪 القوة: {s_text} ({strength:.0f})
📌 القمة السابقة: {previous_high:.2f}

🎯 الأهداف:
1️⃣ {target1:.2f} (+{TARGET_1_PCT*100:.0f}%)
2️⃣ {target2:.2f} (+{TARGET_2_PCT*100:.0f}%)
3️⃣ {target3:.2f} (+{TARGET_3_PCT*100:.0f}%)

🛑 وقف متحرك: {trailing_stop:.2f}"""
        await send_msg(session, msg, chat_id)
    else:
        msg = f"""📊 *نظرة عامة على السوق*

📌 إجمالي الأسهم المراقبة: {len(ACTIVE_TICKERS)}
📈 استراتيجية: اختراق آخر قمة (90 يوم)
🎯 أهداف: {TARGET_1_PCT*100:.0f}% / {TARGET_2_PCT*100:.0f}% / {TARGET_3_PCT*100:.0f}%
🛡️ وقف متحرك: {TRAILING_STOP_PCT*100:.0f}%

🔍 *لتحليل سهم محدد:* أرسل `/تحليل [الكود]`
مثال: `/تحليل 2222`"""
        await send_msg(session, msg, chat_id)

async def handle_strategy_command(session, chat_id):
    msg = f"""📈 *استراتيجية اختراق آخر قمة*

🔍 *كيف تعمل؟*
نبحث عن الأسهم التي:
1️⃣ تخترق أعلى سعر لها خلال 90 يوماً
2️⃣ حجم تداول أعلى من المتوسط بـ {MIN_VOLUME_RATIO}x
3️⃣ زخم سعري +{MIN_MOMENTUM}% أو أكثر
4️⃣ مؤشر RSI بين {RSI_MIN} و {RSI_MAX}
5️⃣ سيولة عالية (حجم > {MIN_VOLUME:,})
6️⃣ السعر بين {MIN_PRICE} - {MAX_PRICE} ريال

🎯 *الأهداف:*
• الهدف 1: +{TARGET_1_PCT*100:.0f}%
• الهدف 2: +{TARGET_2_PCT*100:.0f}%
• الهدف 3: +{TARGET_3_PCT*100:.0f}%

🛡️ *إدارة المخاطر:*
• وقف خسارة متحرك بـ {TRAILING_STOP_PCT*100:.0f}%
• يتم رفع الوقف مع ارتفاع السعر

📌 *ملاحظة:* هذا تحليل فني، ليس نصيحة استثمارية."""
    await send_msg(session, msg, chat_id)

async def handle_help_command(session, chat_id):
    msg = f"""🤖 *أوامر البوت المتاحة:*

/تحليل [كود السهم] - تحليل سهم محدد
مثال: `/تحليل 2222` (لأرامكو)

/تحليل - عرض نظرة عامة على السوق

/استراتيجيات - شرح استراتيجية البوت

/الفرص - عرض أفضل الفرص الحالية

/مساعده - عرض هذه القائمة

📌 *ملاحظة:* يمكنك كتابة الأوامر بدون "/" أيضاً."""
    await send_msg(session, msg, chat_id)

async def handle_opportunities_command(session, chat_id):
    if not daily_opportunities:
        await send_msg(session, "⚠️ لا توجد فرص حالياً. انتظر ظهور فرص جديدة.", chat_id)
        return
    
    daily_opportunities.sort(key=lambda x: x['strength'], reverse=True)
    top_5 = daily_opportunities[:5]
    
    msg = f"🚀 *أفضل 5 فرص حالياً*\n📅 {datetime.now(RIYADH_TZ).strftime('%Y-%m-%d %H:%M')}\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, opp in enumerate(top_5, 1):
        icon = "💥" if opp['strength'] >= 75 else "🚀" if opp['strength'] >= 60 else "📈"
        msg += f"{i}. {icon} *{opp['display_name']}*\n   💵 {opp['price']:.2f} | قوة: {opp['strength']}/100\n   📊 حجم {opp['volume_ratio']:.1f}x | زخم +{opp['change']:.2f}%\n\n"
    await send_msg(session, msg, chat_id)

# ============= دالة جلب البيانات =============
async def fetch_ticker_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                if not data.get("chart", {}).get("result"):
                    return None
                result = data["chart"]["result"][0]
                meta = result.get("meta", {})
                quote = result.get("indicators", {}).get("quote", [{}])[0]
                current_price = meta.get("regularMarketPrice", 0)
                previous_close = meta.get("previousClose", current_price)
                current_volume = meta.get("regularMarketVolume", 0)
                if current_price <= 0 or current_volume <= 0:
                    return None
                volumes = quote.get("volume", [])
                closes = quote.get("close", [])
                highs = quote.get("high", [])
                prev_volume = volumes[-2] if len(volumes) >= 2 and volumes[-2] else current_volume
                change = ((current_price - previous_close) / previous_close) * 100 if previous_close > 0 else 0
                avg_volume = sum(volumes[-20:]) / 20 if len(volumes) >= 20 else current_volume
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                rsi = calculate_rsi(closes)
                ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else current_price
                high_20d = max(highs[-20:]) if len(highs) >= 20 else current_price
                high_60d = max(highs[-60:]) if len(highs) >= 60 else current_price
                previous_high = max(highs[-PREVIOUS_HIGH_LOOKBACK:]) if len(highs) >= PREVIOUS_HIGH_LOOKBACK else current_price
                is_above_ma20 = current_price > ma20
                is_breakout_20d = current_price > high_20d
                is_breakout_60d = current_price > high_60d
                is_breakout_previous_high = current_price > previous_high
                is_high_volume = volume_ratio >= MIN_VOLUME_RATIO
                is_good_momentum = change >= MIN_MOMENTUM
                is_good_rsi = RSI_MIN <= rsi <= RSI_MAX
                is_high_liquidity = current_volume >= MIN_VOLUME
                if (is_good_momentum and is_high_volume and is_breakout_previous_high and 
                    is_good_rsi and is_high_liquidity and is_above_ma20 and
                    MIN_PRICE <= current_price <= MAX_PRICE):
                    strength = calculate_strength_score(change, volume_ratio, rsi, is_breakout_20d, is_breakout_60d, is_above_ma20)
                    return {"ticker": ticker, "price": current_price, "change": change, "volume": current_volume, "volume_ratio": volume_ratio, "rsi": rsi, "strength": strength, "previous_high": previous_high}
                return None
    except:
        return None

# ============= دوال المتابعة والملخص =============
async def check_and_update_followups(session, now_riyadh):
    global stock_followup
    to_remove = []
    for ticker, follow in stock_followup.items():
        data = await fetch_ticker_data(ticker)
        if not data:
            continue
        current_price = data["price"]
        highest_reached = max(follow["highest_price"], current_price)
        display_name = get_stock_display(ticker)
        stock_followup[ticker]["highest_price"] = highest_reached
        new_stop = get_trailing_stop(current_price, highest_reached)
        old_stop = follow["stop_loss"]
        target1, target2, target3 = get_targets(follow["entry_price"])
        msg_updates = []
        if not follow["target1_hit"] and current_price >= target1:
            follow["target1_hit"] = True
            msg_updates.append(f"✅ *تحقق الهدف الأول* عند {target1:.2f}")
        if not follow["target2_hit"] and current_price >= target2:
            follow["target2_hit"] = True
            msg_updates.append(f"✅ *تحقق الهدف الثاني* عند {target2:.2f}")
        if not follow["target3_hit"] and current_price >= target3:
            follow["target3_hit"] = True
            msg_updates.append(f"🏆 *تحقق الهدف الثالث* عند {target3:.2f}")
            to_remove.append(ticker)
        if new_stop > old_stop:
            stock_followup[ticker]["stop_loss"] = new_stop
            msg_updates.append(f"🛡️ *رفع وقف الخسارة* إلى {new_stop:.2f}")
        if current_price <= follow["stop_loss"]:
            msg_updates.append(f"❌ *تم ضرب وقف الخسارة* عند {follow['stop_loss']:.2f}")
            to_remove.append(ticker)
        if msg_updates:
            update_msg = f"📊 *متابعة {display_name}*\n💰 السعر: {current_price:.2f}\n📈 الأعلى: {highest_reached:.2f}\n🛑 الوقف: {new_stop:.2f}\n━━━━━━━━━━━━━━━━━━━━━\n" + "\n".join(msg_updates)
            await send_msg(session, update_msg)
    for ticker in to_remove:
        del stock_followup[ticker]

async def send_daily_summary(session):
    global daily_opportunities
    if not daily_opportunities:
        await send_msg(session, "📊 *ملخص نهاية اليوم*\n\n⚠️ لم يتم رصد أي فرص اليوم.")
        return
    daily_opportunities.sort(key=lambda x: x['strength'], reverse=True)
    top_10 = daily_opportunities[:10]
    msg = f"📊 *ملخص نهاية اليوم - أفضل {len(top_10)} فرصة*\n📅 {datetime.now(RIYADH_TZ).strftime('%Y-%m-%d')}\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, opp in enumerate(top_10, 1):
        icon = "💥" if opp['strength'] >= 75 else "🚀" if opp['strength'] >= 60 else "📈"
        msg += f"{i}. {icon} *{opp['display_name']}* | قوة: {opp['strength']}/100\n   💵 {opp['price']:.2f} | زخم +{opp['change']:.2f}%\n   📊 حجم {opp['volume_ratio']:.1f}x | RSI: {opp['rsi']:.0f}\n   🎯 أهداف: {opp['target1']:.2f} / {opp['target2']:.2f} / {opp['target3']:.2f}\n   🛑 وقف: {opp['stop_loss']:.2f}\n\n"
    await send_msg(session, msg)
    daily_opportunities = []

# ============= الدالة الرئيسية =============
async def main():
    global market_open_sent, market_close_sent, current_date, daily_opportunities
    
    async with aiohttp.ClientSession() as session:
        await send_msg(session, f"✅ *البوت يعمل الان جاري المتابعة*\n\n📊 {len(ACTIVE_TICKERS)} شركة تحت المراقبة\n📈 استراتيجية اختراق آخر قمة\n🎯 أهداف: {TARGET_1_PCT*100:.0f}% / {TARGET_2_PCT*100:.0f}% / {TARGET_3_PCT*100:.0f}%\n🛡️ وقف متحرك: {TRAILING_STOP_PCT*100:.0f}%\n\n🤖 أرسل `/مساعده` لمعرفة الأوامر المتاحة.")
        
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
                await send_daily_summary(session)
            
            # ============= معالجة الأوامر =============
            try:
                updates_url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
                async with session.get(updates_url) as resp:
                    if resp.status == 200:
                        updates_data = await resp.json()
                        if updates_data.get("ok"):
                            for update in updates_data.get("result", []):
                                last_update_id = update["update_id"]
                                if "message" in update and "text" in update["message"]:
                                    text = update["message"]["text"].strip()
                                    chat_id = update["message"]["chat"]["id"]
                                    
                                    if str(chat_id) == str(CHAT_ID):
                                        continue
                                    
                                    text_lower = text.lower()
                                    
                                    if text_lower.startswith("/تحليل") or text_lower.startswith("تحليل"):
                                        parts = text.split()
                                        if len(parts) > 1 and parts[1].isdigit():
                                            await handle_analysis_command(session, chat_id, parts[1])
                                        else:
                                            await handle_analysis_command(session, chat_id)
                                    
                                    elif text_lower.startswith("/استراتيجيات") or text_lower == "استراتيجيات":
                                        await handle_strategy_command(session, chat_id)
                                    
                                    elif text_lower.startswith("/الفرص") or text_lower == "الفرص":
                                        await handle_opportunities_command(session, chat_id)
                                    
                                    elif text_lower.startswith("/مساعده") or text_lower == "مساعده":
                                        await handle_help_command(session, chat_id)
            except Exception as e:
                print(f"خطأ في جلب الرسائل: {e}")
            
            # ============= مراقبة السوق =============
            if market_open_time <= now_riyadh <= market_close_time:
                await check_and_update_followups(session, now_riyadh)
                for i, ticker in enumerate(ACTIVE_TICKERS):
                    data = await fetch_ticker_data(ticker)
                    if data:
                        display_name = get_stock_display(ticker)
                        price = data["price"]
                        change = data["change"]
                        volume = data["volume"]
                        volume_ratio = data["volume_ratio"]
                        rsi = data["rsi"]
                        strength = data["strength"]
                        previous_high = data["previous_high"]
                        alert_counters[display_name] = alert_counters.get(display_name, 0) + 1
                        target1, target2, target3 = get_targets(price)
                        trailing_stop = get_trailing_stop(price, price)
                        daily_opportunities.append({'display_name': display_name, 'price': price, 'change': change, 'volume_ratio': volume_ratio, 'strength': strength, 'target1': target1, 'target2': target2, 'target3': target3, 'stop_loss': trailing_stop, 'rsi': rsi})
                        last_alert = tracker.get(display_name, 0)
                        if time.time() - last_alert > 21600:
                            tracker[display_name] = time.time()
                            if display_name not in stock_followup:
                                stock_followup[display_name] = {"entry_price": price, "highest_price": price, "target1_hit": False, "target2_hit": False, "target3_hit": False, "stop_loss": trailing_stop}
                            s_text = "💥 قوي جداً" if strength >= 75 else "🚀 قوي" if strength >= 60 else "📈 متوسط"
                            msg = (f"🚀 *اختراق آخر قمة*\n\n📌 *{display_name}* | #{alert_counters[display_name]}\n💰 {price:.2f} ريال | زخم +{change:.2f}%\n📊 حجم {volume_ratio:.1f}x | سيولة {volume:,}\n📈 RSI: {rsi:.0f} | قوة: {s_text} ({strength:.0f})\n📊 القمة السابقة: {previous_high:.2f}\n\n🎯 الأهداف:\n1️⃣ {target1:.2f} (+{TARGET_1_PCT*100:.0f}%)\n2️⃣ {target2:.2f} (+{TARGET_2_PCT*100:.0f}%)\n3️⃣ {target3:.2f} (+{TARGET_3_PCT*100:.0f}%)\n🛑 وقف متحرك: {trailing_stop:.2f} (-{TRAILING_STOP_PCT*100:.0f}%)")
                            await send_msg(session, msg)
                    if (i + 1) % 20 == 0:
                        gc.collect()
                        await asyncio.sleep(0.5)
                gc.collect()
            
            await asyncio.sleep(60)

if __name__ == "__main__":
    print(f"بدء البوت... {len(ACTIVE_TICKERS)} شركة")
    asyncio.run(main())
