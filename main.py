import requests
import os
import time
from datetime import datetime
from google_calendar import sync_to_google_calendar

URL = "https://sinhvien.huce.edu.vn/SinhVien/GetDanhSachLichTheoTuan"

CHECK_INTERVAL = 86400  # 24 giờ


# đọc COOKIE từ Railway Variables
def load_cookies():
    cookie_string = os.getenv("COOKIE")

    if not cookie_string:
        print("❌ COOKIE chưa được thiết lập")
        return {}

    cookies = {}

    parts = cookie_string.split(";")
    for part in parts:
        if "=" in part:
            name, value = part.strip().split("=", 1)
            cookies[name] = value

    return cookies


# lấy thời khoá biểu
def get_schedule():

    cookies = load_cookies()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://sinhvien.huce.edu.vn",
        "Referer": "https://sinhvien.huce.edu.vn/lich-theo-tuan.html"
    }

    data = {
        "tuan": "0"
    }

    try:

        response = requests.post(
            URL,
            headers=headers,
            cookies=cookies,
            data=data,
            timeout=30
        )

        if response.status_code == 200:
            return response.text

        print("❌ HTTP Error:", response.status_code)
        return None

    except Exception as e:
        print("❌ Request Error:", e)
        return None


# đọc cache
def load_cache():

    if not os.path.exists("schedule_cache.txt"):
        return ""

    with open("schedule_cache.txt", "r", encoding="utf-8") as f:
        return f.read()


# lưu cache
def save_cache(data):

    with open("schedule_cache.txt", "w", encoding="utf-8") as f:
        f.write(data)


# thông báo thay đổi
def notify_change():

    print("📢 Thời khoá biểu thay đổi lúc:", datetime.now())

    # sync lên Google Calendar
    sync_to_google_calendar(current)


# chương trình chính
def main():

    print("🚀 Bot started")

    while True:

        try:

            print("🔍 Đang kiểm tra thời khoá biểu...")

            current = get_schedule()

            if current:

                old = load_cache()

                if current != old:

                    print("✅ Có thay đổi!")

                    notify_change()

                    save_cache(current)

                else:

                    print("⏱ Không có thay đổi")

            else:

                print("⚠ Không lấy được dữ liệu")

        except Exception as e:

            print("❌ Lỗi:", e)

        print("💤 Sleep 24h...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
