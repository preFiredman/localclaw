FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install localclaw
RUN pip install -e .

# Create workspace directory
RUN mkdir -p /workspace

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOCALCLAW_WORKSPACE=/workspace

# Expose port for potential web interface
EXPOSE 8080

# Default command
CMD ["python", "-m", "localclaw"]
