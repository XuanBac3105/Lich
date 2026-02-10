import requests
import json
import time

CHECK_INTERVAL = 86400  # 24h

def load_cookies():

    with open("cookies.json", "r", encoding="utf-8") as f:
        cookies_list = json.load(f)

    cookies = {}

    for c in cookies_list:
        cookies[c["name"]] = c["value"]

    return cookies


def get_schedule():

    cookies = load_cookies()

    url = "https://sinhvien.huce.edu.vn/SinhVien/GetDanhSachLichTheoTuan"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://sinhvien.huce.edu.vn",
        "Referer": "https://sinhvien.huce.edu.vn/lich-theo-tuan.html",
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
        "tuan": "0",
        "nam": "0"
    }

    try:

        r = requests.post(
            url,
            headers=headers,
            cookies=cookies,
            data=data
        )

        print("Status:", r.status_code)

        if r.status_code == 200:

            if len(r.text) > 100:
                print("Lấy lịch thành công")
                return r.text

            else:
                print("Có thể cookie hết hạn")
                return None

        else:
            print("Lỗi:", r.status_code)
            return None

    except Exception as e:
        print("Error:", e)
        return None


def main():

    last = None

    while True:

        print("Đang kiểm tra thời khoá biểu...")

        current = get_schedule()

        if current:

            if last is None:
                last = current
                print("Đã lưu lịch")

            elif current != last:
                print("LỊCH ĐÃ THAY ĐỔI!")
                last = current

            else:
                print("Không có thay đổi")

        print("Kiểm tra lại sau 24 giờ...\n")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
