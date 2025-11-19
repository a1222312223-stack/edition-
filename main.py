import time
import traceback
import os
from threading import Thread
from flask import Flask

# --- استيراد الأدوات والمنطق ---
from telegram_utils import get_updates, load_chat_sessions, save_chat_sessions
from bot_logic import process_update

# --- إعداد خادم الويب الوهمي (Keep-Alive) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Bot is running."

def run_http():
    # Render يعطيك متغير بيئة اسمه PORT، نستخدمه هنا
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_http)
    t.start()

# --- الإعدادات الرئيسية ---
SAVE_INTERVAL_SECONDS = 60

def main():
    """
    الحلقة الرئيسية للبوت.
    """
    # تشغيل الخادم الوهمي قبل البدء
    keep_alive()
    
    offset = None
    chat_sessions = load_chat_sessions()
    last_save_time = time.time()
    
    print("Professional Bot started. Awaiting commands... 🤖")

    try:
        while True:
            # 1. جلب التحديثات من تيليجرام
            updates = get_updates(offset)
            
            if updates and 'result' in updates:
                for update in updates['result']:
                    try:
                        process_update(update, chat_sessions)
                    except Exception as e:
                        print(f"CRITICAL ERROR processing update {update.get('update_id')}: {e}")
                        traceback.print_exc()
                    
                    offset = update['update_id'] + 1
            
            # 3. حفظ الجلسات بشكل دوري
            if time.time() - last_save_time > SAVE_INTERVAL_SECONDS:
                save_chat_sessions(chat_sessions)
                last_save_time = time.time()
            
            # استراحة قصيرة جداً لعدم استهلاك المعالج بشكل مفرط
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopping bot...")
    except Exception as e:
        print(f"A critical, unhandled error occurred in the main loop: {e}")
        traceback.print_exc()
    finally:
        print("Final save before shutdown.")
        save_chat_sessions(chat_sessions)
        print("Shutdown complete.")

if __name__ == '__main__':
    main()
