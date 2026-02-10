import requests
import os
import re


def load_cookies():
    cookie_string = os.getenv("COOKIE")
    cookies = {}
    for part in cookie_string.split(";"):
        if "=" in part:
            name, value = part.strip().split("=", 1)
            cookies[name] = value
    return cookies


def get_meeting_link(id_lich_hoc):
    """
    Lấy link Teams/Zoom từ API JoinZoomClass
    
    Args:
        id_lich_hoc: ID của lịch học
        
    Returns:
        Link Teams/Zoom nếu có, None nếu không có
    """
    url = "https://sinhvien.huce.edu.vn/SinhVien/JoinZoomClass"
    
    cookies = load_cookies()
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://sinhvien.huce.edu.vn",
        "Referer": "https://sinhvien.huce.edu.vn/lich-theo-tuan.html"
    }
    
    data = {
        "param[IDLichHoc]": str(id_lich_hoc),
        "param[IsLichHoc]": "True"
    }
    
    try:
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            # Thử lấy từ joinUrl trước
            if "joinUrl" in result:
                return result["joinUrl"]
            
            # Nếu không có, extract từ Data (HTML iframe)
            if "Data" in result:
                data_html = result["Data"]
                # Extract link từ iframe src
                match = re.search(r'src="([^"]+)"', data_html)
                if match:
                    return match.group(1)
        
        return None
        
    except Exception as e:
        print(f"⚠️  Error getting meeting link for ID {id_lich_hoc}: {e}")
        return None
