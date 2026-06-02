#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
DIR="$HOME/producer-camp-cal"
cd "$DIR" || exit 1
LOG="$DIR/sync.log"
echo "[$(date)] start" >> "$LOG"
curl -s -m 30 "$(cat $HOME/.producer_camp_ics)" -o /tmp/pc_cal.ics 2>>"$LOG" || { echo "[$(date)] curl failed" >>"$LOG"; exit 1; }
/usr/bin/python3 "$DIR/render_cal.py" /tmp/pc_cal.ics "$DIR/calendar.png" >> "$LOG" 2>&1
git add calendar.png
if git commit -m "Update calendar $(date +%Y-%m-%dT%H:%M)" >>"$LOG" 2>&1; then
  git push origin main >>"$LOG" 2>&1 && echo "[$(date)] pushed" >>"$LOG"
else
  echo "[$(date)] no changes" >>"$LOG"
fi
