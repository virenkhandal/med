FROM python:3.12-slim

WORKDIR /app

# System deps: ffmpeg for audio decoding (webm/opus/m4a), curl for healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer caching).
COPY pyproject.toml .
RUN mkdir -p medstudy && touch medstudy/__init__.py && \
    pip install --no-cache-dir -e .

# Pre-download the tiny.en Whisper model so first-request latency is low.
ENV WHISPER_MODEL=tiny.en
ENV WHISPER_COMPUTE=int8
ENV HF_HOME=/app/.cache/huggingface
RUN python -c "from faster_whisper import WhisperModel; WhisperModel('tiny.en', device='cpu', compute_type='int8')"

ARG CACHE_BUST=1
COPY medstudy/ medstudy/
COPY static/ static/
COPY data/ data/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "medstudy.main:app", "--host", "0.0.0.0", "--port", "8000"]
