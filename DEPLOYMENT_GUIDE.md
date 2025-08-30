# InPlay Football Scraper - Railway Deployment Guide

## 📁 Files to Upload to GitHub Repository

Upload these files to your `inplay_football` repository at https://github.com/wyatt1110/inplay_football:

### Core Application Files
- ✅ `inplay_football_scraper.py` - Main scraper (modified for Railway)
- ✅ `server.js` - Continuous server with scheduling
- ✅ `requirements.txt` - Python dependencies
- ✅ `package.json` - Node.js configuration

### Railway Configuration
- ✅ `railway.toml` - Railway deployment configuration
- ✅ `Procfile` - Process definition for Railway

### Database Schema
- ✅ `inplay_football_table.sql` - Database table creation script

### Documentation
- ✅ `README.md` - Comprehensive deployment documentation
- ✅ `DEPLOYMENT_GUIDE.md` - This deployment guide
- ✅ `.gitignore` - Git ignore rules

## 🚀 Railway Deployment Steps

### 1. Repository Setup
```bash
# Clone or create the repository
git clone https://github.com/wyatt1110/inplay_football.git
cd inplay_football

# Add all files
git add .
git commit -m "Initial Railway deployment setup"
git push origin main
```

### 2. Railway Project Setup
1. **Go to Railway.app** → New Project → GitHub Repo
2. **Select repository**: `wyatt1110/inplay_football`
3. **Configure environment variables** in Railway dashboard:

```env
SUPABASE_URL=https://gwvnmzflxttdlhrkejmy.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3dm5temZseHR0ZGxocmtlam15Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzkwODc5NSwiZXhwIjoyMDQ5NDg0Nzk1fQ.5FcuTSXJJLGhfnAVhOEKACTBGCxiDMdMIQeOR2n19eI
NODE_ENV=production
```

### 3. Database Setup
Run the SQL script in your Supabase dashboard:
```sql
-- Execute inplay_football_table.sql in Supabase SQL Editor
```

### 4. Deploy
Railway will automatically:
- ✅ Install Python dependencies from `requirements.txt`
- ✅ Install Node.js dependencies from `package.json`
- ✅ Start the continuous server via `npm start`
- ✅ Begin scraper scheduling (every 5 minutes)

## 🔧 Static IP Configuration (If Needed)

If the scraper gets blocked by inplayfootballtips.co.uk:

### Option 1: Railway Pro Static IP
1. **Upgrade to Railway Pro plan**
2. **Go to service Settings** → Networking
3. **Enable Static IPs** (assigns permanent IPv4)
4. **Redeploy** to activate static IP

### Option 2: External Proxy (You Handle)
If Railway's static IP doesn't work:
- **You mentioned you can set up proxy**
- **Modify scraper** to use proxy settings
- **Add proxy configuration** to environment variables

## 📊 Monitoring & Health Checks

### Health Endpoint
```bash
GET https://your-railway-app.railway.app/health
```

### Expected Response
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

### Railway Logs
Monitor in Railway dashboard:
- ✅ **Deployment logs** for setup issues
- ✅ **Application logs** for scraper progress
- ✅ **Error logs** for debugging

## ⚡ Scheduling Details

### Automatic Scheduling
- **Runs**: Every 5 minutes continuously
- **Overlap protection**: Won't start if already running
- **Minimum gap**: 5 minutes between runs
- **Timeout**: 10 minutes per scraper run
- **Restart policy**: Always (Railway auto-restarts on crashes)

### No Manual Cron Jobs Needed
The `server.js` handles all scheduling internally:
- ✅ **No Railway cron configuration required**
- ✅ **No external schedulers needed**
- ✅ **Self-managing process queue**
- ✅ **Automatic restart on failures**

## 🛡️ Error Handling

### Built-in Protections
- ✅ **Login failure detection** with detailed logging
- ✅ **Stale element recovery** for dynamic content
- ✅ **Database connection resilience**
- ✅ **Process timeout protection**
- ✅ **Graceful shutdown** handling

### Common Issues & Solutions

#### 1. Login Failures
- **Check credentials** in scraper code
- **Monitor logs** for specific error messages
- **Verify website accessibility** from Railway IPs

#### 2. Database Connection Issues
- **Verify environment variables** in Railway
- **Check Supabase service status**
- **Confirm table exists** with correct schema

#### 3. Chrome/Selenium Issues
- **Railway includes Chrome** in nixpacks configuration
- **Headless mode** enabled for cloud deployment
- **WebDriver manager** handles driver installation

## 📋 Post-Deployment Checklist

### ✅ Verify Deployment
1. **Check Railway logs** for successful startup
2. **Test health endpoint** returns 200 OK
3. **Monitor first scraper run** in logs
4. **Verify database records** in Supabase

### ✅ Confirm Scheduling
1. **Wait 5 minutes** for first scheduled run
2. **Check logs** for "Scheduled check" messages
3. **Verify scraper completion** messages
4. **Confirm data updates** in database

### ✅ Monitor Performance
1. **Track success rates** in logs
2. **Monitor memory usage** in Railway
3. **Check for any error patterns**
4. **Verify continuous operation**

## 🚨 Troubleshooting

### If Scraper Fails to Start
1. **Check Python dependencies** in Railway logs
2. **Verify Chrome installation** in build logs
3. **Confirm environment variables** are set

### If Website Blocks Requests
1. **Enable Railway Pro static IP** first
2. **If still blocked**, you'll need to set up proxy
3. **Contact me** to modify scraper for proxy use

### If Database Operations Fail
1. **Verify Supabase credentials** in Railway env vars
2. **Check table schema** matches scraper expectations
3. **Confirm network connectivity** to Supabase

## 📞 Support

**Ready for deployment!** The scraper is production-ready with:
- ✅ **Continuous operation** every 5 minutes
- ✅ **Smart duplicate handling** (same team + date = update)
- ✅ **Robust error recovery** for web scraping challenges
- ✅ **Professional logging** for easy monitoring
- ✅ **Railway-optimized** configuration

If you encounter any issues during deployment, check the Railway logs first - they'll show exactly what's happening during startup and operation.
