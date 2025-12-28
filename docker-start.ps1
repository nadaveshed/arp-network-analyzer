# Quick start script for Docker setup (PowerShell)
# Usage: .\docker-start.ps1

Write-Host "🐳 ARP Network Analyzer - Docker Quick Start" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed." -ForegroundColor Red
    Write-Host "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    Write-Host "Please install Docker Desktop (includes Compose)" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Build and start
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker-compose build

Write-Host ""
Write-Host "🚀 Starting ARP Network Analyzer..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for service to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check if container is running
$containerRunning = docker ps --filter "name=arp-network-analyzer" --format "{{.Names}}"

if ($containerRunning) {
    Write-Host "✅ Container is running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Web UI: " -NoNewline
    Write-Host "http://localhost:5000" -ForegroundColor Cyan
    Write-Host "📡 API: " -NoNewline
    Write-Host "http://localhost:5000/api/stats" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Useful commands:" -ForegroundColor Yellow
    Write-Host "  View logs:        docker-compose logs -f"
    Write-Host "  Stop service:     docker-compose down"
    Write-Host "  Restart:          docker-compose restart"
    Write-Host ""
    Write-Host "💡 Generate test traffic with: " -NoNewline
    Write-Host "ping 192.168.1.1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 Setup complete! Open http://localhost:5000 in your browser." -ForegroundColor Green
} else {
    Write-Host "❌ Container failed to start. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}
