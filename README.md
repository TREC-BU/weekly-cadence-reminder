# weekly-cadence-reminder

Posts the open tasks from the Notion **Weekly Cadence** database that are dated this week (Mon–Sun, Eastern) to Slack, grouped by subteam. Runs every Sunday and Thursday at 3:00 PM ET via cron on the Oracle host.

## Setup

1. **Slack webhook:** api.slack.com/apps → Create New App → From scratch → Incoming Webhooks → on → Add New Webhook → pick the channel → copy the URL.
2. **Notion token:** notion.so/profile/integrations → New integration (internal) → copy the secret. Then open the Weekly Cadence database → ••• → Connections → add the integration.
3. `cp .env.example .env` and fill in both values.
4. Test locally: `python3 weekly_digest.py --dry-run`
5. One-time host setup: `./deploy.sh` (clones this repo to `oracle:~/weekly-cadence-reminder`, copies `.env`, and installs `crontab.txt`). Re-run it only to push a new `.env`.

## Deploying

Every push to `main` runs the **Deploy** GitHub Action (`.github/workflows/deploy.yml`), which SSHes into the host and runs `update.sh`: it checks out `origin/main` and reinstalls `crontab.txt`. To change the code or the schedule, push to `main`. You can also re-run it from the Actions tab (**Deploy → Run workflow**). Don't edit files on the host; they get overwritten.

The workflow's key (`DEPLOY_SSH_KEY` secret) is restricted in the host's `~/.ssh/authorized_keys` to running `update.sh` only, so it can't open a shell. `DEPLOY_KNOWN_HOSTS` holds the host's SSH fingerprint.

Logs on the host: `~/weekly-cadence-reminder/digest.log`. To send one now: `ssh oracle python3 weekly-cadence-reminder/weekly_digest.py`.
