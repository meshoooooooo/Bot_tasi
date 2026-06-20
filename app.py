import os
import asyncio
import aiohttp
from datetime import datetime
import pytz
import time

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ تأكد من إضافة BOT_TOKEN و CHAT_ID في Secrets")
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

market_open_sent = False
market_close_sent = False
current_date = None
alert_tracker = {}
daily_opportunities = []

RSI_PERIOD = 14
PREVIOUS_HIGH_LOOKBACK = 90
SCALP_MIN_VOLUME_RATIO = 2.0
SCALP_MIN_RSI = 30
SCALP_COOLDOWN = 1800

def get_stock_display(ticker):
    code = ticker.replace(".SR", "")
    return f"{STOCK_NAMES.get(code, code)} ({code})"

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

def get_targets(price):
    return (price * 1.03, price * 1.06, price * 1.10)

async def fetch_data(ticker):
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
                price = meta.get("regularMarketPrice", 0)
                if price <= 0:
                    return None
                closes = quote.get("close", [])
                highs = quote.get("high", [])
                lows = quote.get("low", [])
                if not closes or not highs or not lows:
                    return None
                return {
                    "price": price,
                    "closes": closes,
                    "highs": highs,
                    "lows": lows
                }
    except:
        return None

async def analyze_stock(ticker, code, data):
    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    price = data["price"]
    
    rsi = calculate_rsi(closes, RSI_PERIOD)
    ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else price
    ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else price
    high_90d = max(highs[-90:]) if len(highs) >= 90 else price
    low_30d = min(lows[-30:]) if len(lows) >= 30 else price
    prev_high = max(highs[-PREVIOUS_HIGH_LOOKBACK:]) if len(highs) >= PREVIOUS_HIGH_LOOKBACK else price
    
    trend = "صاعد" if price > ma50 else "هابط"
    
    # الكشف عن النموذج الفني
    pattern = "لا يوجد نموذج واضح حالياً"
    if price > prev_high:
        pattern = "اختراق قمة سابقة (إيجابي)"
    elif len(lows) >= 60:
        low1 = min(lows[-60:-30])
        low2 = min(lows[-30:])
        if abs(low1 - low2) / low1 < 0.02 and low2 >= low1 and price > max(lows[-60:]):
            pattern = "نموذج قاع مزدوج (Double Bottom) - إيجابي"
    
    is_breakout = price > prev_high
    evaluation = "إيجابي 🟢" if (price > ma50 and rsi > 50 and is_breakout) else "سلبي 🔴" if (price < ma50 and rsi < 50) else "محايد 🟡"
    
    t1, t2, t3 = get_targets(price)
    stop = low_30d * 0.97 if low_30d > 0 else price * 0.95
    
    return {
        "price": price,
        "rsi": rsi,
        "ma20": ma20,
        "ma50": ma50,
        "trend": trend,
        "pattern": pattern,
        "evaluation": evaluation,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "stop": stop
    }

async def handle_analysis_command(session, chat_id, code):
    ticker = f"{code}.SR"
    if ticker not in ALL_TICKERS:
        await send_msg(session, f"❌ الكود {code} غير موجود.", chat_id)
        return
    
    data = await fetch_data(ticker)
    if not data:
        await send_msg(session, f"❌ تعذر جلب بيانات {code}.", chat_id)
        return
    
    analysis = await analyze_stock(ticker, code, data)
    display = get_stock_display(ticker)
    
    msg = f"""📊 *تحليل فني كامل لـ {display}*

💰 السعر: {analysis['price']:.2f} ريال
📉 RSI: {analysis['rsi']:.0f}
📊 MA20: {analysis['ma20']:.2f} | MA50: {analysis['ma50']:.2f}
📌 الترند: {analysis['trend']}

🔍 *النموذج الفني المكتشف:*
{analysis['pattern']}

🎯 *الأهداف المتوقعة:*
1️⃣ {analysis['t1']:.2f} (+3%)
2️⃣ {analysis['t2']:.2f} (+6%)
3️⃣ {analysis['t3']:.2f} (+10%)

🛑 *وقف الخسارة:* {analysis['stop']:.2f}

📈 *التقييم العام:* {analysis['evaluation']}"""
    await send_msg(session, msg, chat_id)

async def scalping_check(ticker, data, now):
    global alert_tracker
    if not data:
        return None
    
    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    price = data["price"]
    
    if len(closes) < 20:
        return None
    
    rsi = calculate_rsi(closes, RSI_PERIOD)
    recent_highs = highs[-5:]
    if len(recent_highs) < 5:
        return None
    
    is_downtrend = all(recent_highs[i] < recent_highs[i-1] for i in range(1, 5))
    
    breakout = (
        is_downtrend and
        price > recent_highs[-1] and
        rsi > SCALP_MIN_RSI
    )
    
    if breakout:
        display = get_stock_display(ticker)
        last_alert = alert_tracker.get(display, 0)
        if time.time() - last_alert > SCALP_COOLDOWN:
            alert_tracker[display] = time.time()
            t1, t2, t3 = get_targets(price)
            stop = price * 0.97
            return {
                "display": display,
                "price": price,
                "rsi": rsi,
                "t1": t1,
                "t2": t2,
                "t3": t3,
                "stop": stop
            }
    return None

async def scan_market_for_scalps(session, now):
    for ticker in ACTIVE_TICKERS:
        data = await fetch_data(ticker)
        signal = await scalping_check(ticker, data, now)
        if signal:
            msg = f"""⚡ *تنبيه مضاربة فورية*

📌 *{signal['display']}*
💰 السعر: {signal['price']:.2f} ريال
📊 RSI: {signal['rsi']:.0f}

🎯 *أهداف سريعة:*
1️⃣ {signal['t1']:.2f} (+3%)
2️⃣ {signal['t2']:.2f} (+6%)
3️⃣ {signal['t3']:.2f} (+10%)

🛑 *وقف:* {signal['stop']:.2f}"""
            await send_msg(session, msg)
        await asyncio.sleep(0.5)

async def main():
    global market_open_sent, market_close_sent, current_date, daily_opportunities
    
    async with aiohttp.ClientSession() as session:
        await send_msg(session, f"✅ *بوت التحليل والمضاربة يعمل*\n\n📌 اكتب الرمز (مثلاً 2222) للتحليل.\n📡 القناة للتنبيهات.")
        last_update_id = 0
        while True:
            now_riyadh = datetime.now(RIYADH_TZ)
            market_open_time = now_riyadh.replace(hour=10, minute=0, second=0)
            market_close_time = now_riyadh.replace(hour=15, minute=0, second=0)
            
            if current_date != now_riyadh.date():
                current_date = now_riyadh.date()
                market_open_sent = False
                market_close_sent = False
            
            if not market_open_sent and now_riyadh >= market_open_time and now_riyadh < market_close_time:
                market_open_sent = True
                await send_msg(session, f"🔔 *فتح السوق*\n⏰ {now_riyadh.strftime('%H:%M:%S')}")
            
            if not market_close_sent and now_riyadh >= market_close_time:
                market_close_sent = True
                await send_msg(session, f"🔔 *إغلاق السوق*\n⏰ {now_riyadh.strftime('%H:%M:%S')}")
            
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        updates = await resp.json()
                        if updates.get("ok"):
                            for update in updates.get("result", []):
                                if update["update_id"] >= last_update_id:
                                    last_update_id = update["update_id"] + 1
                                if "message" in update and "text" in update["message"]:
                                    text = update["message"]["text"].strip()
                                    chat_id = update["message"]["chat"]["id"]
                                    if str(chat_id) == str(CHAT_ID):
                                        continue
                                    if text.isdigit() and len(text) == 4:
                                        await handle_analysis_command(session, chat_id, text)
                                    elif text.lower() in ["/start", "start", "قائمة"]:
                                        await send_msg(session, "📊 *مرحباً*\n\nاكتب الرمز (مثلاً 2222) للتحليل.", chat_id)
            except Exception as e:
                print(f"خطأ: {e}")
            
            if market_open_time <= now_riyadh <= market_close_time:
                if now_riyadh.minute % 5 == 0 and now_riyadh.second < 5:
                    await scan_market_for_scalps(session, now_riyadh)
            
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
