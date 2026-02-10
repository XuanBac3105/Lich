import os
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/calendar']


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


def get_service():

    credentials = get_credentials()

    service = build(
        'calendar',
        'v3',
        credentials=credentials
    )

    return service


service = get_service()

CALENDAR_ID = "primary"


def create_event(event):

    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()

    print("📅 Created:", created_event.get("summary"))


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
