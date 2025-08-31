# 🚀 Deploy to Render.com (Chrome Scraper Friendly)

## Why Render.com?
- ✅ **Chrome/Selenium works perfectly** (unlike Railway)
- ✅ **FREE tier** for small scrapers
- ✅ **Direct GitHub integration** (just like Railway)
- ✅ **Auto-deploys** on git push

## Setup Steps (3 minutes):

### 1. Create Render.com Account
- Go to [render.com](https://render.com)
- Click "Sign up with GitHub"

### 2. Create New Web Service
- Click "New +" → "Web Service"
- Connect your GitHub account
- Select `wyatt1110/inplay_football` repository
- Click "Connect"

### 3. Configure Service
- **Name**: `inplay-football-scraper`
- **Environment**: `Docker`
- **Plan**: `Free`
- **Auto-Deploy**: `Yes`

### 4. Add Environment Variables
In the Render.com dashboard, add these environment variables:
- `SUPABASE_URL`: `https://gwvnmzflxttdlhrkejmy.supabase.co`
- `SUPABASE_SERVICE_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd3dm5temZseHR0ZGxocmtlam15Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzkwODc5NSwiZXhwIjoyMDQ5NDg0Nzk1fQ.5FcuTSXJJLGhfnAVhOEKACTBGCxiDMdMIQeOR2n19eI`

### 5. Deploy
- Click "Create Web Service"
- Render.com will automatically build and deploy
- **Chrome will work!** (Unlike Railway)

## What Happens Next:
- ✅ Every git push automatically deploys
- ✅ Chrome scraper runs successfully
- ✅ Data gets inserted into Supabase
- ✅ Continuous scraping every few minutes

## Cost:
- **FREE** for up to 750 hours/month (enough for continuous scraping)
- No credit card required for free tier
