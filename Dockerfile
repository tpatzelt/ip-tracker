FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md /app/

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    tzdata \
    gosu \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    apscheduler \
    httpx \
    jinja2

COPY app /app/app

RUN mkdir -p /app/data

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENV IP_TRACKER_DATA_DIR=/app/data

VOLUME ["/app/data"]

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
