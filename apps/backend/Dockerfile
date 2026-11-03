FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic
COPY src ./src
RUN pip install --no-cache-dir .
EXPOSE 8000 8001 8090
HEALTHCHECK --interval=10s --timeout=3s --start-period=40s --retries=8 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["sh", "-c", "alembic upgrade head && python -m finbank.seed && exec uvicorn finbank.main:app --host 0.0.0.0 --port 8000"]
