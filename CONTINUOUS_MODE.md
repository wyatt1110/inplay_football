# InPlay Football Scraper - Continuous Mode

## 🚀 Quick Start

### On VPS (Recommended)
```bash
cd inplay_football
./start_continuous.sh
```

### Manual Options

#### Option 1: Python Continuous Runner (Recommended for VPS)
```bash
python3 continuous_runner.py
```

#### Option 2: Node.js Server (Recommended for Railway/Cloud)
```bash
node server.js
```

## 📋 How It Works

### Continuous Mode Features:
- ✅ **Instant Restart**: Starts next run immediately after completion (1 second delay)
- ✅ **No Overlapping**: Prevents multiple instances running simultaneously
- ✅ **Error Recovery**: Automatically retries after 30 seconds on errors
- ✅ **Logging**: Full logging to files and console
- ✅ **Health Monitoring**: HTTP health check endpoint (Node.js version)
- ✅ **Graceful Shutdown**: Handles Ctrl+C and system signals

### Timing:
- **Normal Run**: Completes → waits 1 second → starts next run
- **On Error**: Waits 30 seconds → retries
- **Startup**: Starts first run after 10 seconds

## 🔧 Configuration

### Environment Variables (automatically set by start script):
```bash
export DISPLAY=:99
export SUPABASE_URL="https://gwvnmzflxttdlhrkejmy.supabase.co"
export SUPABASE_SERVICE_KEY="your_key_here"
```

### Performance:
- **Expected Runtime**: ~1.5-2 minutes per run (optimized)
- **Frequency**: Continuous (no gaps between runs)
- **Resource Usage**: Optimized for minimal database queries

## 📊 Monitoring

### Python Runner:
- Logs to: `continuous_runner.log`
- Console output shows run count, duration, and status

### Node.js Server:
- Health check: `http://your-server:3000/health`
- Returns JSON with scraper status and timestamp

## 🛑 Stopping

### To Stop:
- Press `Ctrl+C` in terminal
- Or kill the process: `pkill -f continuous_runner` or `pkill -f server.js`

### Graceful Shutdown:
Both runners handle shutdown signals properly and will:
1. Wait for current scrape to complete
2. Clean up resources
3. Exit cleanly

## 🔍 Troubleshooting

### Common Issues:

1. **Chrome/Display Issues**:
   ```bash
   export DISPLAY=:99
   Xvfb :99 -screen 0 1920x1080x24 &
   ```

2. **Permission Issues**:
   ```bash
   chmod +x start_continuous.sh
   ```

3. **Environment Variables**:
   Check that SUPABASE_URL and SUPABASE_SERVICE_KEY are set

### Logs:
- Python runner: `continuous_runner.log`
- Scraper logs: `inplay_scraper.log`

## 🚀 Deployment

### VPS Deployment:
1. `git pull origin main`
2. `./start_continuous.sh`
3. Choose option 2 (Python runner)

### Cloud Deployment (Railway):
1. Push to GitHub
2. Railway will automatically use `server.js`
3. Continuous mode starts automatically

## ⚡ Performance Optimizations

The scraper now includes:
- Batch database queries (1 query vs N queries)
- Reduced wait times throughout the process
- Automatic cleanup of old records
- Optimized Chrome settings for VPS

Expected improvement: **3 minutes → 1.5-2 minutes per run**
