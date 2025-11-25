FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

COPY main/ ./main/

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main/app.py
CMD ["gunicorn", "main.app:app", "--bind", "0.0.0.0:8000", "--timeout", "120", "--workers", "2"]
