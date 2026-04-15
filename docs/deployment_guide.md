# Aetherius Deployment Guide (VPS)

This guide covers deploying the top-level orchestrator and core modules on a Linux VPS.

## 1) Prerequisites
- Ubuntu 22.04+ (or equivalent Linux)
- Python 3.11+
- Outbound internet access for source foraging and model APIs
- SMTP credentials for delivery (optional in `pilot_safe` mode)

## 2) Clone and environment setup
```bash
git clone <your-repo-url> /opt/aetherius
cd /opt/aetherius
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3) Runtime environment variables
Create `/opt/aetherius/.env`:

```bash
AETHERIUS_MODE=pilot_safe
AETHERIUS_LOOP_SECONDS=21600
AETHERIUS_RISK_THRESHOLD=0.70
AETHERIUS_RECIPIENT=

SMTP_HOST=smtp.postmarkapp.com
SMTP_PORT=587
SMTP_FROM=verified-sender@yourdomain.com
SMTP_USE_TLS=true
SMTP_USERNAME=<POSTMARK_SERVER_TOKEN>
SMTP_PASSWORD=<POSTMARK_SERVER_TOKEN>
```

## 4) Run once locally for smoke check
```bash
source .venv/bin/activate
python orchestrator.py
```

Expected artifacts:
- `aetherius_system.log` created in project root
- markdown outputs under `simulations/generated_logs/`

## 5) Run as a systemd service
Create `/etc/systemd/system/aetherius.service`:

```ini
[Unit]
Description=Aetherius Orchestrator
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/aetherius
EnvironmentFile=/opt/aetherius/.env
ExecStart=/opt/aetherius/.venv/bin/python /opt/aetherius/orchestrator.py
Restart=always
RestartSec=10
User=ubuntu

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable aetherius
sudo systemctl start aetherius
sudo systemctl status aetherius
```

## 6) Logging and observability
- Runtime events are written to `aetherius_system.log` as JSON lines.
- Use log rotation for long-running deployments:
  - rotate daily
  - keep 14 to 30 days
- Track these fields at minimum:
  - `run_id`
  - stage timing
  - token spend estimate
  - cache-hit ratio
  - error/retry state

## 7) Safety modes
- `pilot_safe` (default): never auto-sends; outputs require human review.
- `autonomous_research`: can auto-send only if `AETHERIUS_RECIPIENT` is set.

## 8) Troubleshooting
- **Service crash loop:** check `journalctl -u aetherius -f`
- **No output files:** verify `AETHERIUS_RISK_THRESHOLD` and forager output count
- **SMTP errors:** confirm credentials, sender verification, and TLS settings
- **Permission issues:** ensure service user can write logs/output directories

## 9) Security notes
- Never commit `.env` with real secrets.
- Rotate SMTP/API keys periodically.
- Restrict VPS ingress to required ports only.
