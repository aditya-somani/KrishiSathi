# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS base

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN mkdir -p src/krishisathi

RUN uv sync --locked --no-dev

COPY . .
RUN chown -R appuser:appuser /app

USER appuser

# Pre-fetch Silero VAD and LiveKit turn-detector weights at image build time
RUN uv run src/krishisathi/main.py download-files

CMD ["uv", "run", "src/krishisathi/main.py", "start"]
