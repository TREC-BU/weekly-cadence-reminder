# weekly-cadence-reminder

Posts the open tasks from the Notion **Weekly Cadence** database that are dated this week (Mon–Sun, Eastern) to Slack, grouped by subteam. Runs every Sunday and Thursday at 3:00 PM ET via cron on the Oracle host.

## Setup

1. **Slack webhook:** api.slack.com/apps → Create New App → From scratch → Incoming Webhooks → on → Add New Webhook → pick the channel → copy the URL.
2. **Notion token:** notion.so/profile/integrations → New integration (internal) → copy the secret. Then open the Weekly Cadence database → ••• → Connections → add the integration.
3. `cp .env.example .env` and fill in both values.
4. Test locally: `python3 weekly_digest.py --dry-run`
5. Deploy: `./deploy.sh` (copies the script + `.env` to `oracle:~/weekly-cadence-reminder` and installs the cron job)

Logs on the host: `~/weekly-cadence-reminder/digest.log`. To send one now: `ssh oracle python3 weekly-cadence-reminder/weekly_digest.py`.
