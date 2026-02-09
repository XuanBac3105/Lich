import requests
import json
import time
import hashlib
import os

URL = "https://sinhvien.huce.edu.vn/TraCuu/GetDanhSachLichTheoTuan"

# load cookies từ Railway Environment Variable
def load_cookies():
    cookies_json = os.environ.get("COOKIES_JSON")

    if not cookies_json:
        raise Exception("Thiếu COOKIES_JSON trong Railway Variables")

    cookies_list = json.loads(cookies_json)

    cookies = {}
    for c in cookies_list:
        cookies[c['name']] = c['value']

    return cookies


def get_schedule():
    cookies = load_cookies()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://sinhvien.huce.edu.vn/",
        "Origin": "https://sinhvien.huce.edu.vn"
    }

    params = {
        "tuan": 0,
        "namHoc": 2025,
        "hocKy": 2
    }

    try:
        r = requests.get(URL, headers=headers, cookies=cookies, params=params)

        print("Status:", r.status_code)

        if r.status_code == 200:
            return r.text
        else:
            print("Cookie hết hạn hoặc lỗi đăng nhập")
            return None

    except Exception as e:
        print("Lỗi request:", e)
        return None


def hash_data(data):
    return hashlib.md5(data.encode()).hexdigest()


def load_old_hash():
    try:
        with open("hash.txt", "r") as f:
            return f.read()
    except:
        return ""


def save_hash(h):
    with open("hash.txt", "w") as f:
        f.write(h)


def save_schedule(data):
    with open("schedule.json", "w", encoding="utf-8") as f:
        f.write(data)


# vòng lặp chính
while True:

    print("Đang kiểm tra thời khoá biểu...")

    data = get_schedule()

    if data:

        new_hash = hash_data(data)
        old_hash = load_old_hash()

        if new_hash != old_hash:

            print("Thời khoá biểu đã thay đổi!")

            save_hash(new_hash)
            save_schedule(data)

        else:
            print("Không có thay đổi")

    print("Kiểm tra lại sau 24 giờ...\n")

    time.sleep(86400)
