import os
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/calendar']


# lấy credentials từ Railway Variables
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
        'calendar',
        'v3',
        credentials=credentials
    )

    return service


# tạo service global
service = get_service()


# QUAN TRỌNG: dùng email calendar của bạn
CALENDAR_ID = "xuanbac0531@gmail.com"


# tạo event
def create_event(event):

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()

    print("📅 Created:", created_event.get("summary"))


# xoá toàn bộ event cũ
def delete_all_events():

    print("🗑 Deleting old events...")

    events = service.events().list(
        calendarId=CALENDAR_ID
    ).execute()

    for event in events.get("items", []):
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event["id"]
        ).execute()

    print("✅ Deleted old events")
