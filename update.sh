#!/usr/bin/env bash
# Runs on the Oracle host from cron: if origin/main has new commits, check them
# out and reinstall crontab.txt. Pass --force to reinstall regardless.
set -euo pipefail

# Wrapped in a function so bash parses the whole file before the reset below
# replaces it on disk.
main() {
  cd "$(dirname "$0")"
  git fetch --quiet origin main
  local old new
  old="$(git rev-parse HEAD)"
  new="$(git rev-parse origin/main)"
  if [ "$old" = "$new" ] && [ "${1:-}" != "--force" ]; then
    return
  fi

  git reset --hard --quiet origin/main
  ( crontab -l 2>/dev/null | sed '/^# BEGIN weekly-cadence-reminder$/,/^# END weekly-cadence-reminder$/d' ;
    cat crontab.txt ) | crontab -
  echo "$(date '+%F %T') deployed ${new:0:7} (was ${old:0:7})"
}

main "$@"
exit
