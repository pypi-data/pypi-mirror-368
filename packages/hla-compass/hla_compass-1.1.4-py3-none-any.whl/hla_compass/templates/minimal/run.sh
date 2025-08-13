#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              Minimal Module - Development Server             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# TODO: Uncomment these lines if you need a database
# 
# # Check if Docker is running
# if ! docker info > /dev/null 2>&1; then
#     echo "❌ Docker is not running. Please start Docker Desktop first."
#     exit 1
# fi
# 
# # Start PostgreSQL
# echo "🚀 Starting PostgreSQL database..."
# docker-compose up -d
# 
# # Wait for database
# sleep 5

# Start the server
echo "🎯 Starting server on http://localhost:3333"
echo ""
echo "TODO: Implement your module logic in backend/main.py"
echo ""

python3 server.py