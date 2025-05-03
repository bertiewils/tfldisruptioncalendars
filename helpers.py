from urllib.parse import quote as urlencode

import requests

MODES = "dlr,elizabeth-line,overground,tube"


def search_by_name(name: str) -> str:
    """
    Search for and return matching station info.
    """
    url = f"https://api.tfl.gov.uk/StopPoint/Search/{urlencode(name)}?modes={MODES}&includeHubs=true"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data["matches"]:
            print(f"Found {len(data['matches'])} matches for '{name}'")
            for match in data["matches"]:
                print(match["id"], match["name"], str(match["modes"]), sep="\t")
        else:
            raise ValueError(f"No matches found for '{name}'")
    else:
        raise Exception(f"HTTP error: {response.status_code}")
