import json
import urllib.request
import time
from datetime import datetime, timedelta

# إعدادات التليجرام
TELEGRAM_TOKEN = "8782648491:AAF0PHHHBMFzh5yG6RwHOjXbBDdZMoOshzw"
CHAT_ID = "-1003766547355"
API_KEY = "4HN7WBRH6GSU18NZ" 

TADAWUL_STOCKS = ["2222", "2010", "1301", "2060", "2080", "2300", "2310", "2350", "7010", "7020", "2030", "2280", "1210", "1303", "2020", "2090"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try: urllib.request.urlopen(req, timeout=10)
    except: pass

print("[*] Sniper Engine: Scanning for Trend Breakouts...")

while True:
    now = datetime.utcnow() + timedelta(hours=3)
    
    if 10 <= now.hour < 15:
        for symbol in TADAWUL_STOCKS:
            # طلب البيانات اليومية
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}.SR&apikey={API_KEY}"
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
                    if "Time Series (Daily)" in data:
                        ts = data["Time Series (Daily)"]
                        dates = sorted(ts.keys())[-30:]
                        highs = [float(ts[d]["2. high"]) for d in dates]
                        current_price = float(ts[dates[-1]]["4. close"])
                        resistance = max(highs[:-1]) # أعلى سعر في الـ 29 يوم السابقة
                        
                        # منطق كسر الترند (الاختراق)
                        if current_price >= resistance:
                            send_telegram(f"🎯 *إشارة قنص (اختراق):* {symbol}\n📈 السعر الآن: {current_price:.2f}\n🚀 كسر مقاومة {resistance:.2f}")
            except:
                pass
            time.sleep(20) 
        time.sleep(300)
    else:
        time.sleep(1800)
