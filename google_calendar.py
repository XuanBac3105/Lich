import os
import json
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


# =========================
# lấy credentials từ Railway Variables
# =========================
def get_credentials():

    creds_json = os.getenv("GOOGLE_CREDENTIALS")

    if not creds_json:
        raise Exception("GOOGLE_CREDENTIALS chưa được thiết lập")

    creds_dict = json.loads(creds_json)

    credentials = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=SCOPES
    )

    return credentials


# =========================
# tạo Google Calendar service
# =========================
def get_service():

    credentials = get_credentials()

    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )

    return service


# =========================
# tạo event
# =========================
def create_event(service, summary, description, location, start_time, end_time):

    event = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Ho_Chi_Minh",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Ho_Chi_Minh",
        },
    }

    event = service.events().insert(
        calendarId="primary",  # giữ nguyên nếu đã share calendar
        body=event
    ).execute()

    print("📅 Event created:", event.get("htmlLink"))


# =========================
# hàm sync chính (được gọi từ main.py)
# =========================
def sync_to_google_calendar():

    try:

        print("📅 Sync Google Calendar...")

        service = get_service()

        # test event (sau sẽ thay bằng parse HUCE)
        now = datetime.now()

        start = now + timedelta(minutes=1)
        end = start + timedelta(hours=2)

        create_event(
            service=service,
            summary="HUCE Schedule Updated",
            description="Tự động sync từ Railway",
            location="HUCE",
            start_time=start,
            end_time=end
        )

        print("✅ Sync thành công")

    except Exception as e:

        print("❌ Lỗi sync Google Calendar:", e)
