FROM python:3.12-slim

WORKDIR /app

# System deps for psycopg (PostgreSQL client) and geoalchemy2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy dependency manifests first for Docker layer caching
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system --no-cache -e ".[dev]"

# Copy application source
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
