#!/bin/bash
# Start script for continuous InPlay Football scraper

echo "🚀 InPlay Football Scraper - Continuous Mode Startup"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "inplay_football_scraper.py" ]; then
    echo "❌ Error: inplay_football_scraper.py not found"
    echo "Please run this script from the inplay_football directory"
    exit 1
fi

# Set environment variables for VPS
export DISPLAY=:99
export SUPABASE_URL="https://gwvnmzflxttdlhrkejmy.supabase.co"
export SUPABASE_SERVICE_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3dm5temZseHR0ZGxocmtlam15Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzkwODc5NSwiZXhwIjoyMDQ5NDg0Nzk1fQ.5FcuTSXJJLGhfnAVhOEKACTBGCxiDMdMIQeOR2n19eI"

echo "✅ Environment variables set"

# Start virtual display if not running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "🖥️ Starting virtual display..."
    Xvfb :99 -screen 0 1920x1080x24 &
    sleep 2
fi

echo "🔄 Choose running mode:"
echo "1) Node.js server (recommended for Railway/cloud)"
echo "2) Python continuous runner (recommended for VPS)"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo "🚀 Starting Node.js server..."
        node server.js
        ;;
    2)
        echo "🚀 Starting Python continuous runner..."
        python3 continuous_runner.py
        ;;
    *)
        echo "❌ Invalid choice. Starting Python runner by default..."
        python3 continuous_runner.py
        ;;
esac
