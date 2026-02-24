
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8000
