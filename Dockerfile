FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev && \
    # These files are unnecessary
    find /app/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type f -name "*.pyc" -delete && \
    rm -rf /app/.venv/lib/python3.12/site-packages/torch/test 2>/dev/null || true && \
    rm -rf /app/.venv/lib/python3.12/site-packages/torch/include 2>/dev/null || true && \
    rm -rf /app/.venv/lib/python3.12/site-packages/torch/share 2>/dev/null || true

COPY . .

EXPOSE 3000

CMD ["uv", "run", "gunicorn", "main.app:app", "--bind", "0.0.0.0:3000", "--timeout", "120", "--workers", "2"]
