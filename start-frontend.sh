#!/bin/bash
#
# Start Frontend - RealtyAI
# Simple HTTP server for frontend
#

echo "=========================================="
echo "🌐 RealtyAI - Frontend Server"
echo "=========================================="
echo ""

cd "$(dirname "$0")/frontend"

echo "🚀 Starting frontend on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start simple HTTP server
python3 -m http.server 3000
