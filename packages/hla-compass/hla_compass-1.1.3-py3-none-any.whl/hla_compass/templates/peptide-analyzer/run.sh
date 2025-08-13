#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           Peptide Analyzer Module - Quick Start              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if psycopg2-binary is installed
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "📦 Installing psycopg2-binary..."
    pip install psycopg2-binary
fi

# Stop any existing containers
echo "🧹 Cleaning up any existing containers..."
docker-compose down 2>/dev/null

# Start PostgreSQL
echo "🚀 Starting PostgreSQL database..."
docker-compose up -d

# Wait for database to be ready
echo "⏳ Waiting for database to initialize..."
for i in {1..30}; do
    if docker exec peptide-analyzer-db pg_isready -U postgres > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Database failed to start. Check Docker logs."
        exit 1
    fi
    sleep 1
done

# Give it another second for tables to be created
sleep 2

# Start the server
echo ""
echo "🎯 Starting web server on http://localhost:3333"
echo ""

# Open browser (works on macOS and Linux)
if command -v open > /dev/null; then
    # macOS
    (sleep 2 && open http://localhost:3333) &
elif command -v xdg-open > /dev/null; then
    # Linux
    (sleep 2 && xdg-open http://localhost:3333) &
fi

# Run the server
python3 server.py