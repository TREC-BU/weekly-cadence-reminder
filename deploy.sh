#!/usr/bin/env bash
# One-time setup of the Oracle host, or re-run to push a new .env.
# After this, the host deploys itself from origin/main (see update.sh).
set -euo pipefail

HOST="${HOST:-oracle}"
DIR="weekly-cadence-reminder"
REPO="git@github.com:TREC-BU/weekly-cadence-reminder.git"
cd "$(dirname "$0")"

# Turn ~/$DIR into a checkout of the repo (works whether or not it already exists)
ssh "$HOST" bash -s <<EOF
set -euo pipefail
mkdir -p ~/$DIR
if [ ! -d ~/$DIR/.git ]; then
  tmp=\$(mktemp -d)
  git clone --quiet --no-checkout "$REPO" "\$tmp/repo"
  mv "\$tmp/repo/.git" ~/$DIR/
  rm -rf "\$tmp"
fi
EOF

[ -f .env ] && scp .env "$HOST:~/$DIR/.env" && ssh "$HOST" "chmod 600 ~/$DIR/.env"

ssh "$HOST" "cd ~/$DIR && git fetch --quiet origin main && git reset --hard --quiet origin/main && ./update.sh --force && crontab -l"
