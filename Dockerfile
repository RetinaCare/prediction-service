FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

COPY requirements.txt .

RUN uv pip install --system -r requirements.txt

COPY main/ ./main/

EXPOSE 8000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main/app.py

CMD ["gunicorn", "main.app:app", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2"]
