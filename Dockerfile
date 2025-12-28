FROM python:3.11-slim

# Install system dependencies for packet capture
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose API port
EXPOSE 5000

# Set environment variable to reduce Scapy warnings
ENV PYTHONUNBUFFERED=1

# Default command: start with API
CMD ["python", "main.py", "--api", "--log-level", "INFO"]
