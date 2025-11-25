FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY main/ ./main/

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main/app.py

CMD ["gunicorn", "main.app:app", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2"]
