FROM python:3.11-slim

WORKDIR /app

# PostgreSQL client für Django

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python Abhängigkeit

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# pytest für CI Tests

RUN pip install --no-cache-dir pytest pytest-django pytest-cov

COPY . .

EXPOSE 8001

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]