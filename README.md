# TfL Disruption Calendars

Calendars for planned works on the London Underground.

Note: This is not for, and will not show, live service disruptions. Use TFL Go, Citymapper or something else for that.

## How to use

1. Right-click and copy the link of the station you want a calendar for.
2. In your calendar app, add a new calendar from URL and paste in the link you copied.


<!-- --------  DESIGN  ---------------- -->

For station in list_of_stations:



---

## Development

### Design Overview

```
for station in all_stations:
    get planned works

    for work in planned_works:
        add work to calendar
    write calendar to disk
```

### Devcontainer

A devcontainer config exists in the repo.

### Python venv

Create a venv and install the requirements. E.g.
```
uv venv --python 3.12
uv pip install -r requirements.txt
source .venv/bin/activate
# Do stuff
deactivate
```

## TODO

- Rewrite to use https://api.tfl.gov.uk/swagger/ui/index.html?url=/swagger/docs/v1#!/StopPoint/StopPoint_GetByTypeWithPagination endpoint
- Or use https://github.com/ZackaryH8/tfl-api-wrapper-py ?
- Frontend single page with search and copy url button
- Filter disruptions by mode DONE
- Make the index json available (fake api?)
- Actions badge to show if failing
- add link to https://www.homepages.ucl.ac.uk/~ucahmto/programming/2024/11/02/tube-disruption-calendar.html
- add disclaimer to site

## Disclaimer

This repository is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Transport for London (TfL) or it's parent organisation Greater London Authority (GLA)
