import json
import urllib.request
import time
from datetime import datetime

# --- إعدادات البوت ---
TELEGRAM_TOKEN = "8782648491:AAF0PHHHBMFzh5yG6RwHOjXbBDdZMoOshzw"
CHAT_ID = "-1003766547355"

# الكلمات المفتاحية للاستثناء
EXCLUDED_KEYWORDS = ["الريت", "صندوق", "الإنماء", "الراجحي ريت", "الإسمنت", "أسمنت", "سمنت", "REIT"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}).encode('utf-8')
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try: urllib.request.urlopen(req, timeout=5)
    except: pass

def check_stock_validity(ticker_name):
    """فلتر استبعاد الصناديق والريتات والإسمنتات"""
    for keyword in EXCLUDED_KEYWORDS:
        if keyword in ticker_name:
            return False
    return True

def run_scanner():
    print("[*] System Online: Monitoring TASI...")
    
    # رسالة ترحيب عند تشغيل البوت
    send_telegram("🚀 *نظام TRB v2.0 يعمل الآن بكامل طاقته.*")
    
    while True:
        now = datetime.now()
        
        # 1. وضع المضاربة اللحظية (خلال جلسة تاسي)
        if 10 <= now.hour < 15:
            # هنا يتم وضع منطق مراقبة السيولة اللحظية للأسهم المسموحة
            pass 
        
        # 2. وضع المسح اليومي (بعد الإغلاق الساعة 4 م)
        elif now.hour == 16 and now.minute == 0:
            send_telegram("📊 *بدء المسح الشامل لأسهم تاسي (استراتيجية TRB v2.0)...*")
            # هنا يتم إجراء المسح وحساب الاختراقات (Breakouts)
            time.sleep(65) # لتجنب التكرار في نفس الدقيقة
            
        time.sleep(60)

if __name__ == "__main__":
    run_scanner()
