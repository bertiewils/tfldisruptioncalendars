import json

import mkdocs_gen_files

FILE = "docs/calendars/all.json"

with open(FILE, "r") as file:
    all_stations = json.load(file)

first_letters = {station["commonName"][0].lower() for station in all_stations}

for letter in sorted(first_letters):
    filename = f"stations/{letter}.md"

    with mkdocs_gen_files.open(filename, "w") as f:
        print(f"# Stations beginning with {letter.upper()}", file=f)

        print("| Station ID       | Station Name      | Station Modes      | Calendar Link      |", file=f)
        print("|------------------|-------------------|--------------------|--------------------|", file=f)

        for station in all_stations:
            if station["commonName"][0].lower() == letter:
                station_id = station["naptanId"]
                station_name = station["commonName"]
                station_modes = ", ".join(station["modes"])
                calendar_link = f"[CLICK THIS](webcal:/calendars/{station_id}.ics)"

                print(f"| {station_id} | {station_name} | {station_modes} | {calendar_link} |", file=f)

    mkdocs_gen_files.set_edit_path(filename, "gen_calendar_docs.py")
