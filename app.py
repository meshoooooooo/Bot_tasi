import os
import asyncio
import aiohttp
from datetime import datetime
import pytz
import time

# --- الإعدادات ---
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ تأكد من إضافة BOT_TOKEN و CHAT_ID في الإعدادات")
    exit()

RIYADH_TZ = pytz.timezone('Asia/Riyadh')

# --- بيانات الأسهم ---
STOCK_NAMES = {"2222": "أرامكو السعودية", "1211": "معادن", "7010": "اس تي سي"} # (أضف بقية أسهمك هنا)
ALL_TICKERS = [f"{code}.SR" for code in STOCK_NAMES.keys()]
ACTIVE_TICKERS = [t for t in ALL_TICKERS] # عدلها حسب احتياجك

alert_tracker = {}
RSI_PERIOD = 14
SCALP_COOLDOWN = 1800

# --- الدوال الأساسية (التحليل والإرسال) ---
def get_stock_display(ticker):
    code = ticker.replace(".SR", "")
    return f"{STOCK_NAMES.get(code, code)} ({code})"

async def send_msg(session, msg, chat_id):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    async with session.post(url, json=payload) as resp:
        return await resp.status

def calculate_rsi(closes, period=14):
    if len(closes) < period + 1: return 50
    # (تم اختصار الكود هنا، تأكد من وضع دالة حساب RSI الأصلية التي كانت لديك)
    return 50 

async def fetch_data(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            data = await resp.json()
            # (تأكد من وضع منطق معالجة البيانات الأصلي الخاص بك هنا)
            return {"price": 100, "closes": [100]*20, "highs": [105]*20, "lows": [95]*20}

async def handle_analysis_command(session, chat_id, code):
    ticker = f"{code}.SR"
    data = await fetch_data(ticker)
    # هنا ضع منطق بناء رسالة التحليل (المتغير msg)
    msg = f"📊 *تحليل {code}* \nالسعر الحالي: {data['price']} \n(ضع باقي بياناتك هنا)"
    await send_msg(session, msg, chat_id)

# --- الدالة الرئيسية ---
async def main():
    async with aiohttp.ClientSession() as session:
        last_update_id = 0
        while True:
            # 1. قسم التنبيهات التلقائية (يعمل في الخلفية)
            # (هنا يمكنك إضافة كود فحص السوق الدوري)

            # 2. قسم الاستجابة للأوامر (يقرأ الرسائل في القناة)
            try:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
                async with session.get(url) as resp:
                    updates = await resp.json()
                    if updates.get("ok"):
                        for update in updates.get("result", []):
                            last_update_id = update["update_id"] + 1
                            if "message" in update and "text" in update["message"]:
                                text = update["message"]["text"].strip()
                                chat_id = update["message"]["chat"]["id"]
                                
                                # التعديل الحاسم: استجابة لأي رمز مكون من 4 أرقام في أي محادثة (بما فيها القناة)
                                if text.isdigit() and len(text) == 4:
                                    await handle_analysis_command(session, chat_id, text)
            except Exception as e:
                print(f"خطأ: {e}")
            
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())
