FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY alembic.ini ./
COPY migrations/ ./migrations/
COPY app/ ./app/

# Install Python dependencies
RUN pip install --no-cache-dir -e "."

EXPOSE 8000
