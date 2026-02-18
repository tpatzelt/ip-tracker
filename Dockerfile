FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md /app/

RUN uv pip compile pyproject.toml --no-dev -o /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY app /app/app

RUN useradd -r -u 10001 -g root appuser \
    && mkdir -p /app/data \
    && chown -R appuser:root /app

USER appuser

ENV IP_TRACKER_DATA_DIR=/app/data

VOLUME ["/app/data"]

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
