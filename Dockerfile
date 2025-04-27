FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libspatialindex-dev \
    gdal-bin \
    libproj-dev \
    proj-bin \
    libgeos-dev \
    libopencv-dev \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/src/api /app/src/processing /app/src/dashboard /app/src/data /app/src/models /app/src/utils

# Copy application code
COPY src/ /app/src/

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python", "-m", "src.api.main"]

