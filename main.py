import requests
import json
import time
import hashlib

URL = "https://sinhvien.huce.edu.vn/TraCuu/GetDanhSachLichTheoTuan"

def load_cookies():
    with open("cookies.json", "r") as f:
        cookies_list = json.load(f)
    cookies = {}
    for c in cookies_list:
        cookies[c['name']] = c['value']
    return cookies

def get_schedule():
    cookies = load_cookies()
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "tuan": 0,
        "namHoc": 2025,
        "hocKy": 2
    }

    r = requests.get(URL, headers=headers, cookies=cookies, params=params)

    if r.status_code == 200:
        return r.text
    else:
        print("Lỗi:", r.status_code)
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

while True:
    print("Checking schedule...")

    data = get_schedule()

    if data:
        new_hash = hash_data(data)
        old_hash = load_old_hash()

        if new_hash != old_hash:
            print("Schedule changed!")
            save_hash(new_hash)

            with open("schedule.json", "w") as f:
                f.write(data)

        else:
            print("No change")

    print("Next check after 24 hours...")
    time.sleep(21600)
