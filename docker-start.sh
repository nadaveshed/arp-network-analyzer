#!/bin/bash

# Quick start script for Docker setup
# Usage: ./docker-start.sh

set -e

echo "🐳 ARP Network Analyzer - Docker Quick Start"
echo "=============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ Docker Compose is installed"
echo ""

# Build and start
echo "🔨 Building Docker image..."
docker-compose build

echo ""
echo "🚀 Starting ARP Network Analyzer..."
docker-compose up -d

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

# Check if container is running
if docker ps | grep -q arp-network-analyzer; then
    echo "✅ Container is running!"
    echo ""
    echo "📊 Web UI: http://localhost:5000"
    echo "📡 API: http://localhost:5000/api/stats"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs:        docker-compose logs -f"
    echo "  Stop service:     docker-compose down"
    echo "  Restart:          docker-compose restart"
    echo ""
    echo "💡 Generate test traffic with: ping 192.168.1.1"
    echo ""
    echo "🎉 Setup complete! Open http://localhost:5000 in your browser."
else
    echo "❌ Container failed to start. Check logs with: docker-compose logs"
    exit 1
fi
