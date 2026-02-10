import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]


# đọc credentials từ Railway
def get_credentials():

    creds_json = os.getenv("GOOGLE_CREDENTIALS")

    if not creds_json:
        raise Exception("GOOGLE_CREDENTIALS chưa thiết lập")

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


# parse HTML HUCE schedule
def parse_schedule(html):

    soup = BeautifulSoup(html, "html.parser")

    events = []

    table = soup.find("table")

    if not table:
        return events

    headers = table.find_all("th")

    dates = []

    for th in headers[1:]:
        text = th.get_text(separator="\n").strip().split("\n")

        if len(text) >= 2:
            dates.append(text[1].strip())
        else:
            dates.append(None)

    rows = table.find_all("tr")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) < 2:
            continue

        for i in range(1, len(cols)):

            cell = cols[i]

            content = cell.find_all("div", class_="content")

            for c in content:

                try:

                    subject = c.find("a").text.strip()

                    time_text = c.find(string=lambda t: "Giờ" in t)

                    time_parent = c.find("span", string=lambda t: "Giờ" in t)

                    if not time_parent:
                        continue

                    time_line = time_parent.parent.get_text()

                    time_str = time_line.split(":")[1].strip()

                    start_time, end_time = time_str.split(" - ")

                    room = c.find("font").text.strip()

                    date_str = dates[i-1]

                    date_obj = datetime.strptime(date_str, "%d/%m/%Y")

                    start_dt = datetime.strptime(
                        date_str + " " + start_time,
                        "%d/%m/%Y %H:%M"
                    )

                    end_dt = datetime.strptime(
                        date_str + " " + end_time,
                        "%d/%m/%Y %H:%M"
                    )

                    events.append({
                        "summary": subject,
                        "location": room,
                        "start": start_dt,
                        "end": end_dt
                    })

                except Exception as e:
                    print("Parse error:", e)

    return events


# tạo event Google Calendar
def create_events(service, events):

    for ev in events:

        body = {
            "summary": ev["summary"],
            "location": ev["location"],
            "description": "Tự động sync từ HUCE",
            "start": {
                "dateTime": ev["start"].isoformat(),
                "timeZone": "Asia/Ho_Chi_Minh"
            },
            "end": {
                "dateTime": ev["end"].isoformat(),
                "timeZone": "Asia/Ho_Chi_Minh"
            }
        }

        event = service.events().insert(
            calendarId="primary",
            body=body
        ).execute()

        print("Created:", event.get("htmlLink"))


# hàm chính
def sync_to_google_calendar(html):

    print("📅 Sync Google Calendar...")

    service = get_service()

    events = parse_schedule(html)

    print("Found", len(events), "events")

    create_events(service, events)

    print("✅ Sync xong")
