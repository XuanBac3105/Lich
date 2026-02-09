import requests
import json

url = "https://sinhvien.huce.edu.vn/"

with open("cookies.json") as f:
    cookies = json.load(f)

r = requests.get(url, cookies=cookies)

print(r.status_code)

if r.status_code == 200:
    print("Đăng nhập thành công bằng cookie")
else:
    print("Cookie hết hạn")
