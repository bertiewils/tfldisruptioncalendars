#!/usr/bin/env python3

import argparse
import json
import logging
from datetime import date
from math import ceil
from os import getenv

import requests
from dateutil.parser import isoparse
from ical.calendar import Calendar
from ical.calendar_stream import IcsCalendarStream
from ical.event import Event

from utils import listToCSV

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

TFL_API_BASE = "https://api.tfl.gov.uk"
MODES = ["dlr", "elizabeth-line", "overground", "tube"]
STOP_TYPES = ["NaptanMetroStation", "NaptanRailStation", "TransportInterchange"]
CALENDAR_OUTPUT_DIR = "docs/calendars"
TFL_API_KEY = getenv("TFL_API_KEY", "")


def make_request(endpoint: str, params: dict = None) -> requests.Response:
    """
    Makes a GET request to the given endpoint.

    Args:
        endpoint (str): The API endpoint path.
        params (dict): Additional query parameters for the request.

    Returns:
        Response: The response object from the request.
    """
    if params is None:
        params = {}
    params["app_key"] = TFL_API_KEY

    logging.debug(f"Making request to {TFL_API_BASE}{endpoint} with params {params}")
    response = requests.get(f"{TFL_API_BASE}{endpoint}", params=params)
    response.raise_for_status()
    return response


def get_stoppoints_by_mode(modes):
    """
    Generator function to retrieve StopPoints from the TFL API.
    Args:
        modes (str): Comma-separated string of transport modes.
    Yields:
        dict: A dictionary containing the stop points for each page.
    """
    session = requests.Session()
    url = f"{TFL_API_BASE}/StopPoint/Mode/{modes}"

    first_page = session.get(url, params={"page": "1"}).json()
    yield first_page
    num_pages = ceil(first_page["total"] / 1000)

    for page in range(2, num_pages + 1):
        next_page = session.get(url, params={"page": page}).json()
        yield next_page


def lookup_station_name(station_id):
    path = f"/StopPoint/{station_id}"
    res = make_request(path)
    if res.status_code == 200:
        return res.json().get("commonName")
    else:
        logging.error(f"Failed to retrieve station name for ID {station_id}")
        return None


def generate_ics(station_id, station_name):
    logging.info(f"Generating {station_name}...")

    calendar = Calendar()

    disruptions_path = f"/StopPoint/{station_id}/Disruption"
    response = make_request(
        disruptions_path,
        params={"getFamily": "true", "includeRouteBlockedStops": "true", "flattenResponse": "true"},
    )
    disruptions = response.json()
    planned_works = [
        disruption
        for disruption in disruptions
        if disruption["appearance"] == "PlannedWork" and disruption["mode"] in MODES
    ]
    logging.info(f"Found {len(planned_works)} planned works in {len(disruptions)} disruptions for {station_name}")

    if len(planned_works) > 0:
        for work in planned_works:
            event = Event(
                summary=f"{work['type']}: {work['description']}",
                start=isoparse(work["fromDate"]).date(),
                end=isoparse(work["toDate"]).date(),
            )
            calendar.events.append(event)

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
        for page in get_stoppoints_by_mode(modes=modes):
            stations = [station for station in page["stopPoints"] if station["stopType"] in STOP_TYPES]
            for station in stations:
                generate_ics(station["naptanId"], station["commonName"])
    else:
        all_stations = []
        for page in get_stoppoints_by_mode(modes=listToCSV(MODES)):
            stations = [station for station in page["stopPoints"] if station["stopType"] in STOP_TYPES]

            for station in stations:
                generate_ics(station["naptanId"], station["commonName"])

                relevant_modes = [mode for mode in station["modes"] if mode in MODES]
                all_stations.append(
                    {"naptanId": station["naptanId"], "commonName": station["commonName"], "modes": relevant_modes}
                )

        with open(f"{CALENDAR_OUTPUT_DIR}/all.json", "w") as file:
            json.dump(all_stations, file, indent=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate tube disruption calendars")

    parser.add_argument("-m", "--modes", type=str, help="Comma separated list of station modes to generate")
    parser.add_argument("-s", "--station_ids", type=str, help="Comma separated list of station NaptanIDs to generate")
    args = parser.parse_args()

    if len(TFL_API_KEY) == 0:
        logging.warning("No TFL API key provided. You will be rate limited")

    main(modes=args.modes, station_ids=args.station_ids)
