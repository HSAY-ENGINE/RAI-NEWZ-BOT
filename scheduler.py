import schedule
import time
from bot import run_bot

# ─── SCHEDULE TIMES ───
schedule.every().day.at("08:00").do(run_bot)
schedule.every().day.at("20:00").do(run_bot)

print("✅ RAI NEWZ BOT scheduler is running...")
print("📅 Scheduled for 8:00 AM and 8:00 PM daily")
print("⏳ Waiting for next scheduled time...")

# ─── KEEP RUNNING FOREVER ───
while True:
    schedule.run_pending()
    time.sleep(60)