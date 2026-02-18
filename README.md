# ip-tracker
Tracks your public IP over time with a FastAPI dashboard.

## Quick start

Install dependencies:

```bash
uv sync
```

Run the server:

```bash
uv run uvicorn app.main:app
```

Visit `http://localhost:8000` to see the dashboard.

## Container image (GHCR)

Build and run locally:

```bash
docker build -t ip-tracker .
docker run --rm -p 8000:8000 -v "${PWD}/data:/app/data" ip-tracker
```

Pull and run from GHCR:

```bash
docker pull ghcr.io/tpatzelt/ip-tracker:latest
docker run --rm -p 8000:8000 -v "${PWD}/data:/app/data" ghcr.io/tpatzelt/ip-tracker:latest
```

Environment variables (optional):

```bash
TZ=Europe/Berlin
IP_TRACKER_DATA_DIR=/app/data
IP_TRACKER_HISTORY_FILE=ip_history.jsonl
IP_TRACKER_INTERVAL_MINUTES=720
IP_TRACKER_IP_ENDPOINT=https://api.ipify.org?format=json
```

Example docker compose:

```yaml
services:
  ip-tracker:
    image: ghcr.io/tpatzelt/ip-tracker:latest
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    user: "${PUID:-1000}:${PGID:-1000}"
    environment:
      IP_TRACKER_INTERVAL_MINUTES: "720"
    env_file: .env
```

## Configuration

Environment variables (optional):

- `IP_TRACKER_DATA_DIR` (default: `data`)
- `IP_TRACKER_HISTORY_FILE` (default: `ip_history.jsonl`)
- `IP_TRACKER_INTERVAL_MINUTES` (default: `720`)
- `IP_TRACKER_IP_ENDPOINT` (default: `https://api.ipify.org?format=json`)

## Notes

- Scheduler uses Europe/Berlin time zone by default.
- The tracker runs every 720 minutes by default; adjust `IP_TRACKER_INTERVAL_MINUTES` as needed.
