#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║               Base Module - Development Server               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Start the server
echo "🎯 Starting server on http://localhost:3333"
echo ""

# Open browser (works on macOS and Linux)
if command -v open > /dev/null; then
    # macOS
    (sleep 2 && open http://localhost:3333) &
elif command -v xdg-open > /dev/null; then
    # Linux
    (sleep 2 && xdg-open http://localhost:3333) &
fi

python3 server.py