# TWGY_V3 Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY pyproject.toml .
COPY README.md .

# Create necessary directories
RUN mkdir -p logs output data/cache

# Set Python path
ENV PYTHONPATH=/app

# Create non-root user
RUN useradd --create-home --shell /bin/bash twgy
RUN chown -R twgy:twgy /app
USER twgy

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m src.cli system-info > /dev/null || exit 1

# Default command
CMD ["python", "-m", "src.cli", "--help"]

# Labels
LABEL maintainer="TWGY Team <team@twgy.dev>"
LABEL version="3.0.0"
LABEL description="Advanced Chinese Phonetic Similarity System"