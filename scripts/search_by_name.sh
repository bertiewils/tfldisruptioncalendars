#!/usr/bin/env bash

MODES="dlr,elizabeth-line,overground,tube"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <station_name>"
    exit 1
fi

name=$(echo "$*")
url="https://api.tfl.gov.uk/StopPoint/Search/${name// /%20}?modes=${MODES}&includeHubs=true"

res=$(curl -fsSL "$url")

matches=$(echo "$res" | jq '.matches | length')
if [[ "$matches" -gt 0 ]]; then
    echo "Found $matches matches for '$name'"
   echo "$res" | jq -r '.matches[] | "\(.id)\t\(.name)\t\(.modes | join(", "))"'
else
    echo "No matches found for '$name'" >&2
    exit 1
fi
