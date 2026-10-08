FROM python:3.12-slim AS base

# Install PostgreSQL client tools (for pg_dump / psql)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Ensure output directories exist
RUN mkdir -p exports imports backups logs

CMD ["python", "main.py"]
