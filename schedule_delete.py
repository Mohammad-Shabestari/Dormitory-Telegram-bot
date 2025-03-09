import asyncio
from database import db

async def cleanup_task():
    while True:
        # محاسبه تعداد روزها از تاریخ ایجاد آگهی
        print("Running cleanup job...")
        db.delete_old_items()
        print("Cleanup completed.")

        # صبر کردن به مدت 24 ساعت
        await asyncio.sleep(86400)  # 86400 ثانیه برابر با 24 ساعت