import requests
import os
import time
import pytz

from datetime import datetime, timedelta

from parser import parse_schedule
from google_calendar import create_event, delete_all_events


URL = "https://sinhvien.huce.edu.vn/SinhVien/GetDanhSachLichTheoTuan"


def load_cookies():

    cookie_string = os.getenv("COOKIE")

    cookies = {}

    for part in cookie_string.split(";"):
        if "=" in part:
            name, value = part.strip().split("=", 1)
            cookies[name] = value

    return cookies


def get_schedule(week=0):
    """
    Lấy lịch học theo tuần
    week: 0 = tuần hiện tại, 1 = tuần sau, -1 = tuần trước, etc.
    """
    cookies = load_cookies()

    headers = {

        "User-Agent": "Mozilla/5.0",

        "X-Requested-With": "XMLHttpRequest",

        "Content-Type": "application/x-www-form-urlencoded",

        "Origin": "https://sinhvien.huce.edu.vn",

        "Referer": "https://sinhvien.huce.edu.vn/lich-theo-tuan.html"

    }

    data = {

        "tuan": str(week)

    }

    response = requests.post(
        URL,
        headers=headers,
        cookies=cookies,
        data=data
    )

    return response.text


def seconds_until_6am():

    timezone = pytz.timezone("Asia/Ho_Chi_Minh")

    now = datetime.now(timezone)

    next_run = now.replace(
        hour=6,
        minute=0,
        second=0,
        microsecond=0
    )

    if now >= next_run:
        next_run += timedelta(days=1)

    return (next_run - now).total_seconds()


def run():

    print("🚀 Syncing schedule")

    html = get_schedule()

    events = parse_schedule(html)
    
    # Lấy link Teams/Zoom cho các event có IDLichHoc
    from meeting_links import get_meeting_link
    
    for event in events:
        if "_idLichHoc" in event:
            id_lich_hoc = event["_idLichHoc"]
            print(f"🔗 Getting meeting link for {event['summary']}...")
            
            meeting_link = get_meeting_link(id_lich_hoc)
            
            if meeting_link:
                # Lưu link vào _meetingLink để google_calendar.py xử lý
                event["_meetingLink"] = meeting_link
                print(f"   ✅ Found link")
            else:
                print(f"   ⚠️  No link found")
            
            # Xóa _idLichHoc vì Google Calendar API không cần field này
            del event["_idLichHoc"]

    delete_all_events()

    for event in events:
        create_event(event)

    print("✅ Done sync")


def main():

    print("🚀 Bot started")

    # Chạy sync ngay lập tức khi khởi động
    run()

    while True:

        wait = seconds_until_6am()

        print(f"⏰ Wait {wait/3600:.2f} hours until 6AM")

        time.sleep(wait)

        run()


if __name__ == "__main__":
    main()
