from bs4 import BeautifulSoup
from datetime import datetime
import pytz


def parse_schedule(html):

    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table")

    events = []

    timezone = pytz.timezone("Asia/Ho_Chi_Minh")

    headers = table.find_all("th")[1:]

    dates = []

    for th in headers:
        text = th.get_text("\n")
        parts = text.split("\n")

        if len(parts) > 1:
            dates.append(parts[1].strip())

    rows = table.find_all("tr")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) <= 1:
            continue

        for i, col in enumerate(cols[1:]):

            content = col.find("div", class_="content")

            if not content:
                continue

            subject = content.find("b").get_text(strip=True)

            room_tag = content.find("font")
            room = room_tag.get_text(strip=True) if room_tag else ""

            time_tag = content.find(string=lambda x: x and "Giờ" in x)

            time_p = content.find("p", string=lambda x: x and "Giờ" in x)

            time_text = content.get_text()

            import re

            match = re.search(r'(\d{2}:\d{2})\s*-\s*(\d{2}:\d{2})', time_text)

            if not match:
                continue

            start_time = match.group(1)
            end_time = match.group(2)

            date = dates[i]

            start = timezone.localize(
                datetime.strptime(
                    date + " " + start_time,
                    "%d/%m/%Y %H:%M"
                )
            )

            end = timezone.localize(
                datetime.strptime(
                    date + " " + end_time,
                    "%d/%m/%Y %H:%M"
                )
            )

            is_cancel = content.find("div", class_="tamngung")

            if is_cancel:
                subject += " (TẠM NGƯNG)"

            # Tìm IDLichHoc để lấy link Teams/Zoom
            id_lich_hoc = None
            # Thử tìm trong attribute onclick, data-id, hoặc trong button
            parent_td = content.parent
            if parent_td:
                # Tìm button hoặc link có chứa IDLichHoc
                onclick_elem = parent_td.find(attrs={"onclick": True})
                if onclick_elem:
                    onclick_text = onclick_elem.get("onclick", "")
                    # Extract ID từ onclick, ví dụ: JoinZoomClass(560039)
                    id_match = re.search(r'JoinZoomClass\((\d+)\)', onclick_text)
                    if id_match:
                        id_lich_hoc = id_match.group(1)
                
                # Hoặc tìm trong data-id
                if not id_lich_hoc:
                    data_id_elem = parent_td.find(attrs={"data-id": True})
                    if data_id_elem:
                        id_lich_hoc = data_id_elem.get("data-id")

            event = {

                "summary": subject,

                "location": room,

                "description": "Sync từ HUCE",

                "start": {
                    "dateTime": start.isoformat(),
                    "timeZone": "Asia/Ho_Chi_Minh"
                },

                "end": {
                    "dateTime": end.isoformat(),
                    "timeZone": "Asia/Ho_Chi_Minh"
                }
            }
            
            # Lưu IDLichHoc để sau này lấy link
            if id_lich_hoc:
                event["_idLichHoc"] = id_lich_hoc

            events.append(event)

    return events
