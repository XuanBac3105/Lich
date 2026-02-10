import os
import json
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


# đọc credentials từ Railway Variables
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


# tạo service
def get_service():

    credentials = get_credentials()

    service = build(
        "calendar",
        "v3",
        credentials=credentials
    )

    return service


# tạo event mẫu (bạn sẽ sửa sau để parse từ HUCE)
def create_sample_event(service):

    now = datetime.now()

    start = now + timedelta(minutes=1)
    end = start + timedelta(hours=2)

    event = {
        "summary": "Test lịch học HUCE",
        "location": "HUCE",
        "description": "Tự động sync từ Railway",
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "Asia/Ho_Chi_Minh",
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "Asia/Ho_Chi_Minh",
        },
    }

    event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("📅 Event created:", event.get("htmlLink"))


# hàm chính được gọi từ main.py
def sync_to_google_calendar():

    try:

        print("📅 Sync Google Calendar...")

        service = get_service()

        create_sample_event(service)

        print("✅ Sync thành công")

    except Exception as e:

        print("❌ Lỗi sync Google Calendar:", e)
