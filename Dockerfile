FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    apscheduler \
    httpx \
    jinja2

COPY app /app/app

RUN useradd -r -u 10001 -g root appuser \
    && mkdir -p /app/data \
    && chown -R appuser:root /app

USER appuser

ENV IP_TRACKER_DATA_DIR=/app/data

VOLUME ["/app/data"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
