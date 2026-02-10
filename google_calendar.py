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
    
    # Nếu event có meeting link, thêm vào conferenceData
    if "_meetingLink" in event:
        meeting_link = event["_meetingLink"]
        
        # Xác định loại meeting (Teams hoặc Zoom)
        if "teams.microsoft.com" in meeting_link:
            conference_solution = "Microsoft Teams"
        elif "zoom.us" in meeting_link:
            conference_solution = "Zoom"
        else:
            conference_solution = "Video Conference"
        
        event["conferenceData"] = {
            "conferenceSolution": {
                "name": conference_solution,
                "iconUri": "https://fonts.gstatic.com/s/i/productlogos/meet_2020q4/v6/web-512dp/logo_meet_2020q4_color_2x_web_512dp.png"
            },
            "entryPoints": [
                {
                    "entryPointType": "video",
                    "uri": meeting_link,
                    "label": meeting_link
                }
            ]
        }
        
        # Xóa _meetingLink vì không phải field của Google Calendar API
        del event["_meetingLink"]

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        conferenceDataVersion=1  # Bắt buộc để dùng conferenceData
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
