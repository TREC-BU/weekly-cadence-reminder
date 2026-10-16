#!/usr/bin/env bash
# Copy the script to the Oracle host and install the weekly cron job.
set -euo pipefail

HOST="${HOST:-oracle}"
DIR="weekly-cadence-reminder"
cd "$(dirname "$0")"

ssh "$HOST" "mkdir -p ~/$DIR"
scp weekly_digest.py "$HOST:~/$DIR/"
[ -f .env ] && scp .env "$HOST:~/$DIR/.env" && ssh "$HOST" "chmod 600 ~/$DIR/.env"

# Sundays and Thursdays 3:00 PM Eastern (CRON_TZ handles daylight saving; host is on GMT)
ssh "$HOST" bash -s <<EOF
( crontab -l 2>/dev/null | grep -v "$DIR" | grep -v '^CRON_TZ=America/New_York' ;
  echo 'CRON_TZ=America/New_York' ;
  echo '0 15 * * 0,4 /usr/bin/python3 \$HOME/$DIR/weekly_digest.py >> \$HOME/$DIR/digest.log 2>&1 # $DIR' ) | crontab -
crontab -l
EOF
