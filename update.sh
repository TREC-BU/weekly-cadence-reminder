#!/usr/bin/env bash
# Runs on the Oracle host when the Deploy workflow SSHes in (its key is locked
# to this command): check out origin/main and reinstall crontab.txt.
set -euo pipefail

# Wrapped in a function so bash parses the whole file before the reset below
# replaces it on disk.
main() {
  cd "$(dirname "$0")"
  local old new
  old="$(git rev-parse HEAD)"
  git fetch --quiet origin main
  git reset --hard --quiet origin/main
  new="$(git rev-parse HEAD)"
  ( crontab -l 2>/dev/null | sed '/^# BEGIN weekly-cadence-reminder$/,/^# END weekly-cadence-reminder$/d' ;
    cat crontab.txt ) | crontab -
  echo "$(date '+%F %T') deployed ${new:0:7} (was ${old:0:7})"
}

main "$@"
exit
