# InPlay Football Scraper

🏈 **Real-time football odds scraper** for inplayfootballtips.co.uk with Railway deployment.

## 📋 Overview

This system provides **live football match data** with:

- ✅ **Full match data** (51 columns including odds, scores, analysis)
- ✅ **Smart duplicate handling** (same team + same date = update existing)
- ✅ **Continuous updates** (runs immediately after each completion)
- ✅ **Headless operation** for cloud deployment
- ✅ **Robust error handling** with stale element recovery

## 🏗️ Architecture

### Continuous Server System

#### 🌐 **Server** (`server.js`)
- **Runs**: Continuously on Railway
- **Purpose**: Health checks and process scheduling
- **Logic**: Prevents overlapping runs, manages process queue

#### 🏈 **Scraper** (`inplay_football_scraper.py`)  
- **Runs**: Continuously (starts immediately after previous run completes)
- **Purpose**: Scrape latest match data and odds
- **Logic**: UPSERT (updates existing records, creates new ones)

## 🚀 Railway Deployment

### Prerequisites

1. **Railway account** for deployment
2. **Supabase project** with `inplay_football` table
3. **GitHub repository** connected to Railway

### Environment Variables

Set these in Railway dashboard:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
NODE_ENV=production
```

### Deployment Steps

1. **Connect Railway to this repository**
2. **Set environment variables** in Railway dashboard  
3. **Deploy** - Railway will automatically:
   - Install Python dependencies from `requirements.txt`
   - Install Node.js dependencies from `package.json`
   - Start the continuous server via `npm start`
   - Begin internal scheduling of scraper runs

### Continuous Server Architecture

This deployment uses a **continuous server approach**:

- **`server.js`** runs continuously as a long-running process
- **Continuous scheduling** with overlap protection (runs immediately after completion)
- **Health monitoring** at `/health` endpoint
- **Process queue** prevents multiple scrapers running simultaneously
- **Automatic restart** on crashes via Railway's restart policy

## 📊 Data Flow

1. **Login** to inplayfootballtips.co.uk
2. **Navigate** to Full-Time Model Raw tab
3. **Scrape** all match data (96+ matches typically)
4. **Process** and clean data (handle timestamps, numeric conversions)
5. **Upsert** to Supabase:
   - **Existing matches**: Update all columns with latest data
   - **New matches**: Create new records with auto-generated IDs

## 🔧 Duplicate Prevention

**Smart Logic**: Same `hometeam` + same `date` = duplicate

- ✅ **Updates existing**: All 51 columns refreshed with latest odds
- ✅ **Creates new**: Genuinely new matches get new database IDs
- ✅ **No conflicts**: Same team can't play twice on same date

## 📈 Monitoring

### Health Check
```bash
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "service": "inplay-football-scraper", 
  "uptime": 3600,
  "scraperRunning": false,
  "lastScraperTime": "2025-08-29T20:30:00.000Z",
  "queueLength": 0
}
```

### Logs
- **Real-time scraping progress** with match counts
- **Database operation results** (inserts/updates)
- **Error handling** with detailed error messages
- **UK timezone** logging for easy monitoring

## 🛡️ Error Handling

- **Stale element recovery** for dynamic web content
- **Login failure detection** with detailed debugging
- **Database connection resilience** 
- **Process timeout protection** (10 minute limit)
- **Graceful shutdown** on SIGTERM/SIGINT

## 🔒 Security

- **Environment variables** for sensitive data
- **Headless browser** operation
- **No hardcoded credentials** in repository
- **Service role authentication** for Supabase

## 📋 Requirements

- **Python 3.11+** with Selenium, Supabase client
- **Node.js 18+** for server management
- **Chrome/Chromium** for web scraping
- **Railway Pro plan** (recommended for static IP if needed)

## 🚨 Static IP Considerations

The scraper may work without a static IP, but if inplayfootballtips.co.uk blocks Railway's dynamic IPs:

- **Railway Pro plan** offers static outbound IPs
- **Enable in Railway dashboard** under Networking → Static IPs
- **Alternative**: Connect your own proxy service

## 📞 Support

For issues or questions, check:
- **Railway logs** for deployment issues
- **Health endpoint** for service status  
- **Supabase dashboard** for database connectivity