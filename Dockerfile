# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data
RUN mkdir -p /app/data /app/downloads /app/logs /app/charts

# Set permissions
RUN chmod +x /app/cli.py

# Create non-root user
RUN useradd -m -u 1000 crawler && \
    chown -R crawler:crawler /app
USER crawler

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python cli.py --help || exit 1

# Default command
ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
