#!/bin/bash
set -e
DIR="$HOME/producer-camp-cal"
cd "$DIR"
curl -s -m 30 "$(cat $HOME/.producer_camp_ics)" -o /tmp/pc_cal.ics
python3 "$DIR/render_cal.py" /tmp/pc_cal.ics "$DIR/calendar.png"
git add calendar.png
git commit -m "Update calendar $(date +%Y-%m-%dT%H:%M)" || { echo "no changes"; exit 0; }
git push origin main
