FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN mkdir -p medstudy && touch medstudy/__init__.py && \
    pip install --no-cache-dir -e .

ARG CACHE_BUST=1
COPY medstudy/ medstudy/
COPY static/ static/
COPY data/ data/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "medstudy.main:app", "--host", "0.0.0.0", "--port", "8000"]
