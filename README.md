# TfL Disruption Calendars

Calendars for planned works on the London Underground.

See <https://tfldisruptioncalendars.uk> for more info.

## Development

### Design Overview

[generate_ics.py](generate_ics.py) runs every night ([workflow generate_ics.yml](.github/workflows/generate_ics.yml)), and does the following:

```
for station in all_stations:
    get planned works

    for work in planned_works:
        add work to calendar
    write calendar to disk
```

This triggers `mkdocs` to rebuild and deploy the site, ics files included ([workflow deploy_docs.yml](.github/workflows/deploy_docs.yml)).

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
- Make the index json available (fake api?)
- add app_id to reqs?
- Handle 429s with backoff

## Disclaimer

This repository is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Transport for London (TfL) or it's parent organisation Greater London Authority (GLA).
