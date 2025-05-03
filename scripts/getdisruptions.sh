#!/usr/bin/env bash

case $1 in
    all) MODE=dlr,elizabeth-line,overground,tube ;;
    *) MODE=$1 ;;
esac

curl -s https://api.tfl.gov.uk/StopPoint/Mode/$MODE/Disruption | jq
