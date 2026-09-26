FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    INITIALIZE_DETECTOR_ON_IMPORT=1 \
    HOST=0.0.0.0 \
    PORT=5000

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/src/backend

COPY src/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend/ ./
COPY data/ /app/data/
COPY test/ /app/test/

EXPOSE 5000

HEALTHCHECK --interval=10s --timeout=10s --start-period=30s --retries=12 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f\"http://localhost:{os.getenv('PORT', '5000')}/status\", timeout=5)"

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120 app:app"]
