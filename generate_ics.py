#!/usr/bin/env python3

import argparse
import logging
from datetime import date
from math import ceil

import requests
from dateutil.parser import isoparse
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

TFL_API_BASE = "https://api.tfl.gov.uk"
ALL_MODES = "dlr,elizabeth-line,overground,tube"
MODES = "overground"
STOP_TYPES = ["NaptanMetroStation", "NaptanRailStation", "TransportInterchange"]
CALENDAR_OUTPUT_DIR = "calendars"


def get_tube_stations(modes):
    session = requests.Session()
    url = f"{TFL_API_BASE}/StopPoint/Mode/{modes}"

    first_page = session.get(url, params={"page": "1"}).json()
    yield first_page
    num_pages = ceil(first_page["total"] / 1000)

    for page in range(2, num_pages + 1):
        next_page = session.get(url, params={"page": page}).json()
        yield next_page


def lookup_station_name(station_id):
    url = f"{TFL_API_BASE}/StopPoint/{station_id}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("commonName")
    else:
        logging.error(f"Failed to retrieve station name for ID {station_id}")
        return None


def generate_ics(station_id, station_name):
    logging.info(f"Generating {station_name}...")

    calendar = Calendar()

    disruptions_url = f"{TFL_API_BASE}/StopPoint/{station_id}/Disruption"
    response = requests.get(
        disruptions_url,
        params={"getFamily": "true", "includeRouteBlockedStops": "true", "flattenResponse": "true"},
    )
    disruptions = response.json()
    planned_works = [disruption for disruption in disruptions if disruption["appearance"] == "PlannedWork"]
    logging.info(f"Found {len(planned_works)} planned works in {len(disruptions)} disruptions for {station_name}")

    if len(planned_works) > 0:
        for work in planned_works:
            event = Event(
                summary=f"{work['type']}: {work['description']}",
                start=isoparse(work["fromDate"]).date(),
                end=isoparse(work["toDate"]).date(),
            )
            calendar.events.append(event)
        # calendar.events.append(
        #     Event(summary="Event summary", start=date(2022, 7, 3), end=date(2022, 7, 4)),
        # )

        print("Printing event summaries:")
        for event in calendar.timeline:
            print(event.summary)

    with open(f"{CALENDAR_OUTPUT_DIR}/{station_id}.ics", "w") as ics_file:
        ics_file.write(IcsCalendarStream.calendar_to_ics(calendar))

    logging.info(f"Finished {station_name}")


def main(modes=None, station_ids=None):
    if station_ids:
        for station in station_ids.split(","):
            station_id = station
            station_name = lookup_station_name(station_id)
            generate_ics(station_id, station_name)
    elif modes:
        for mode in modes.split(","):
            for page in get_tube_stations(modes=mode):
                stations = [station for station in page["stopPoints"] if station["stopType"] in STOP_TYPES]
                for station in stations:
                    generate_ics(station["naptanId"], station["commonName"])
    else:
        for page in get_tube_stations(modes=ALL_MODES):
            stations = [station for station in page["stopPoints"] if station["stopType"] in STOP_TYPES]
            for station in stations:
                generate_ics(station["naptanId"], station["commonName"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tube disruption calendars")

    parser.add_argument("-m", "--modes", type=str, help="Comma separated list of station modes to generate")
    parser.add_argument("-s", "--station_ids", type=str, help="Comma separated list of station NaptanIDs to generate")
    args = parser.parse_args()

    main(modes=args.modes, station_ids=args.station_ids)
