from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

APP_TITLE = "IP Tracker"
TIMEZONE = ZoneInfo("Europe/Berlin")

DATA_DIR = Path(os.environ.get("IP_TRACKER_DATA_DIR", "data"))
HISTORY_FILE = DATA_DIR / os.environ.get("IP_TRACKER_HISTORY_FILE", "ip_history.jsonl")
INTERVAL_MINUTES_RAW = os.environ.get("IP_TRACKER_INTERVAL_MINUTES", "720")
IP_ENDPOINT = os.environ.get(
    "IP_TRACKER_IP_ENDPOINT", "https://api.ipify.org?format=json"
)

app = FastAPI(title=APP_TITLE)
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.touch()


def _parse_interval_minutes(raw_value: str) -> int:
    try:
        minutes = int(raw_value)
    except ValueError:
        return 720
    return minutes if minutes > 0 else 720


def _format_interval_label(minutes: int) -> str:
    if minutes % 60 == 0:
        hours = minutes // 60
        return f"every {hours} hour" + ("s" if hours != 1 else "")
    return f"every {minutes} min"


async def fetch_current_ip() -> str | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(IP_ENDPOINT)
            response.raise_for_status()
            payload = response.json()
            return payload.get("ip")
    except Exception:
        return None


def _append_entry(ip: str, timestamp: datetime) -> None:
    entry = {
        "ip": ip,
        "timestamp": timestamp.isoformat(),
    }
    with HISTORY_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def _read_history() -> list[dict[str, str]]:
    if not HISTORY_FILE.exists():
        return []
    entries: list[dict[str, str]] = []
    with HISTORY_FILE.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


async def record_ip() -> None:
    _ensure_storage()
    ip = await fetch_current_ip()
    if not ip:
        return
    now = datetime.now(tz=TIMEZONE)
    _append_entry(ip, now)


@app.on_event("startup")
async def startup() -> None:
    _ensure_storage()
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    interval_minutes = _parse_interval_minutes(INTERVAL_MINUTES_RAW)
    trigger = IntervalTrigger(minutes=interval_minutes)
    scheduler.add_job(record_ip, trigger=trigger, id="ip-fetch-interval")
    scheduler.start()
    app.state.scheduler = scheduler


@app.on_event("shutdown")
async def shutdown() -> None:
    scheduler = getattr(app.state, "scheduler", None)
    if scheduler:
        scheduler.shutdown(wait=False)


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    history = _read_history()
    interval_minutes = _parse_interval_minutes(INTERVAL_MINUTES_RAW)
    interval_label = _format_interval_label(interval_minutes)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "history": history,
            "app_title": APP_TITLE,
            "interval_label": interval_label,
        },
    )


@app.get("/api/history")
async def api_history() -> JSONResponse:
    history = _read_history()
    return JSONResponse(history)
