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
    "2280": "المراعي", "2380": "بترو رابغ", "4030": "البحري", "8210": "بوبا العربية",
    "4190": "جرير", "4003": "إكسترا", "4263": "سال", "4002": "المواساة",
    "1212": "أسترا الصناعية", "2310": "سبكيم العالمية", "4090": "طيبة", "7030": "زين السعودية",
    "2250": "المجموعة السعودية", "2083": "مرافق", "4220": "إعمار", "2050": "مجموعة صافولا",
    "4264": "طيران ناس", "4017": "فقيه الطبية", "2350": "كيان السعودية", "2381": "الحفر العربية"
}

ALL_TICKERS = [f"{code}.SR" for code in STOCK_NAMES.keys()]

BANKS_EXCLUDED = ["1060.SR", "1080.SR", "1120.SR", "1140.SR", "1150.SR"]
EXCLUDED = set(BANKS_EXCLUDED)
ACTIVE_TICKERS = [t for t in ALL_TICKERS if t not in EXCLUDED]

market_open_sent = False
market_close_sent = False
current_date = None

def get_stock_display(ticker):
    code = ticker.replace(".SR", "")
    return f"{STOCK_NAMES.get(code, code)} ({code})"

async def send_msg(session, msg, chat_id=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id or CHAT_ID, "text": msg, "parse_mode": "Markdown"}
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

async def fetch_full_data(ticker):
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

async def handle_analysis_command(session, chat_id, code):
    ticker = f"{code}.SR"
    if ticker not in ALL_TICKERS:
        await send_msg(session, f"❌ الكود {code} غير موجود في القائمة.", chat_id)
        return
    
    data = await fetch_full_data(ticker)
    if not data:
        await send_msg(session, f"❌ تعذر جلب بيانات {code}.", chat_id)
        return
    
    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    price = data["price"]
    
    rsi = calculate_rsi(closes)
    ma50 = sum(closes[-50:]) / 50 if len(closes) >= 50 else price
    low_30d = min(lows[-30:]) if len(lows) >= 30 else price
    previous_high = max(highs[-90:]) if len(highs) >= 90 else price
    
    trend = "صاعد" if price > ma50 else "هابط"
    is_breakout = price > previous_high
    evaluation = "إيجابي 🟢" if (price > ma50 and rsi > 50) else "سلبي 🔴" if (price < ma50 and rsi < 50) else "محايد 🟡"
    
    t1, t2, t3 = get_targets(price)
    stop_loss = low_30d * 0.97
    
    msg = f"""📊 *تحليل فني لـ {get_stock_display(ticker)}*

💰 السعر: {price:.2f} ريال
📉 RSI: {rsi:.0f}
📊 MA50: {ma50:.2f}
📌 الترند: {trend}
📈 القمة السابقة: {previous_high:.2f}

🎯 *الأهداف المتوقعة:*
1️⃣ {t1:.2f} (+3%)
2️⃣ {t2:.2f} (+6%)
3️⃣ {t3:.2f} (+10%)

🛑 *وقف الخسارة:* {stop_loss:.2f}

📌 *التقييم:* {evaluation}"""
    await send_msg(session, msg, chat_id)

async def main():
    global market_open_sent, market_close_sent, current_date
    
    async with aiohttp.ClientSession() as session:
        await send_msg(session, f"✅ *بوت التحليل يعمل*\n📊 اكتب الرمز (مثلاً 2222) للتحليل الفني.")
        
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
                                    if str(chat_id) == str(CHAT_ID): continue
                                    
                                    if text.isdigit() and len(text) == 4:
                                        await handle_analysis_command(session, chat_id, text)
                                    elif text in ["/start", "start", "قائمة"]:
                                        await send_msg(session, "📊 *مرحباً*\n\nاكتب الرمز (مثلاً 2222) للتحليل الفني الكامل.", chat_id)
            except Exception as e:
                print(f"خطأ: {e}")
            
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
