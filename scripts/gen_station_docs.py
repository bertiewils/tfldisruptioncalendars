import json

import mkdocs_gen_files

FILE = "docs/calendars/all.json"
SITE_URL = "tfldisruptioncalendars.uk"

PER_STATION_FORMAT = """
## {station_name}

Modes: {station_modes}

ID: {station_id}

[Add to calendar :fontawesome-brands-apple:]({webcal_link}){{ .md-button }}
[Add to calendar :fontawesome-brands-google:](https://www.google.com/calendar/render?cid={webcal_link}){{ .md-button }}
[Copy to clipboard :fontawesome-regular-copy:](javascript:;){{ data-clipboard-text="{webcal_link}"  .md-button }}

"""

with open(FILE, "r") as file:
    all_stations = json.load(file)

first_letters = {station["commonName"][0].lower() for station in all_stations}

for letter in sorted(first_letters):
    filename = f"stations/{letter}.md"

    with mkdocs_gen_files.open(filename, "w") as f:
        print(f"# Stations beginning with {letter.upper()}", file=f)

        for station in all_stations:
            if station["commonName"][0].lower() == letter:
                station_id = station["naptanId"]
                station_name = station["commonName"]
                station_modes = ", ".join(station["modes"])
                webcal_link = f"webcal://{SITE_URL}/calendars/{station_id}.ics"

                print(
                    PER_STATION_FORMAT.format(
                        station_name=station_name,
                        station_modes=station_modes,
                        station_id=station_id,
                        webcal_link=webcal_link,
                    ),
                    file=f,
                )

    mkdocs_gen_files.set_edit_path(filename, "gen_calendar_docs.py")
