# 🚀 TalentDog - Complete Setup Guide

## Intelligence-First Recruitment Platform
**Automatically detect career signals, match talent to vacancies, and generate AI-powered recruitment briefings.**

---

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Local Development Setup](#local-development-setup)
4. [API Keys & Configuration](#api-keys--configuration)
5. [Deployment Guide](#deployment-guide)
6. [Features & Usage](#features--usage)
7. [Cost Breakdown](#cost-breakdown)

---

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1-Minute Setup (Local Testing)

```bash
# Clone or download the TalentDog folder

# Backend Setup
cd talentdog/backend
pip install -r requirements.txt
python main.py

# Frontend Setup (new terminal)
cd talentdog/frontend
npm install
npm start
```

**That's it!** Open http://localhost:3000 to see TalentDog running with 100 mock profiles.

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  React Frontend │────▶│  FastAPI Backend │────▶│ Gemini AI       │
│  (Port 3000)    │     │  (Port 8000)     │     │ (Matching)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ├──▶ SQLite Database
                              ├──▶ Serper.dev (News Search)
                              ├──▶ ScrapingDog (LinkedIn)
                              └──▶ Slack/Teams Webhooks
```

### Core Components

1. **Frontend (React + Tailwind CSS)**
   - Talent pool visualization
   - Vacancy management
   - AI-generated briefings
   - Real-time signal monitoring

2. **Backend (FastAPI + Python)**
   - RESTful API for all data operations
   - Gemini AI integration for matching
   - Web scraping engine for vacancies
   - Signal detection algorithms

3. **Database (SQLite)**
   - Talent profiles
   - Vacancies
   - Matches (talent ↔ vacancy)
   - Company signals history

4. **AI Layer (Gemini 1.5 Flash)**
   - Vacancy parsing
   - Talent-to-job matching
   - HR briefing generation

---

## 💻 Local Development Setup

### Backend Setup

```bash
cd talentdog/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
SCRAPINGDOG_KEY=your_key_here
SLACK_WEBHOOK_URL=your_webhook_here
TEAMS_WEBHOOK_URL=your_webhook_here
EOF

# Run backend
python main.py
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
cd talentdog/frontend

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Run development server
npm start
```

Frontend will open at: http://localhost:3000

---

## 🔑 API Keys & Configuration

### 1. Gemini API (Required for AI Matching)
- **Where:** https://makersuite.google.com/app/apikey
- **Cost:** Free tier available (60 requests/minute)
- **Usage:** AI matching, vacancy parsing, briefing generation

### 2. Serper.dev (Required for Signal Detection)
- **Where:** https://serper.dev
- **Cost:** $50/month for 5,000 searches
- **Usage:** News search for layoffs, M&A, leadership changes

### 3. ScrapingDog (Optional - for LinkedIn scraping)
- **Where:** https://www.scrapingdog.com
- **Cost:** $40/month for dynamic scraping
- **Usage:** Extract LinkedIn profile data
- **Alternative:** Use mock data or manual import

### 4. Slack Webhook (Optional)
- **Where:** https://api.slack.com/messaging/webhooks
- **Cost:** Free
- **Usage:** Send alerts to Slack channel

### 5. Microsoft Teams Workflow (Optional)
- **Where:** Teams → Workflows → "When a webhook request is received"
- **Cost:** Free
- **Usage:** Send alerts to Teams channel

---

## 🚀 Deployment Guide

### Option 1: Railway (Recommended - Easiest)

**Backend Deployment:**
```bash
cd talentdog/backend

# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Add environment variables in Railway dashboard
```

**Frontend Deployment:**
```bash
cd talentdog/frontend

# Build for production
npm run build

# Deploy to Vercel (free)
npx vercel --prod
```

**Total Cost:** ~$10/month (Railway backend + free Vercel frontend)

### Option 2: DigitalOcean Droplet

**1. Create Droplet ($6/month)**
```bash
# SSH into droplet
ssh root@your-droplet-ip

# Install dependencies
apt update
apt install python3-pip nodejs npm nginx -y

# Clone your code
cd /var/www
git clone your-repo-url talentdog
```

**2. Setup Backend**
```bash
cd /var/www/talentdog/backend
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/talentdog.service << EOF
[Unit]
Description=TalentDog API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/talentdog/backend
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable talentdog
systemctl start talentdog
```

**3. Setup Frontend**
```bash
cd /var/www/talentdog/frontend
npm install
npm run build

# Configure Nginx
cat > /etc/nginx/sites-available/talentdog << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        root /var/www/talentdog/frontend/build;
        try_files \$uri /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
EOF

ln -s /etc/nginx/sites-available/talentdog /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Option 3: Render (Backend) + Netlify (Frontend)

Both have generous free tiers for testing!

---

## 🎯 Features & Usage

### 1. Talent Pool Management

**Add Talent Manually:**
```bash
curl -X POST http://localhost:8000/api/talent/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emma de Vries",
    "role": "Senior Developer",
    "currentCompany": "TechCorp",
    "location": "Amsterdam, NL",
    "sector": "Technology",
    "linkedinUrl": "https://linkedin.com/in/emma-devries",
    "startDate": "2022-01-15"
  }'
```

**Import CSV:**
```python
import pandas as pd
import requests

df = pd.read_csv('talent_list.csv')
for _, row in df.iterrows():
    requests.post('http://localhost:8000/api/talent/add', json=row.to_dict())
```

### 2. Vacancy Scraping

**Scrape Single Vacancy:**
```bash
curl -X POST http://localhost:8000/api/vacancies/sync \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lead Engineer",
    "url": "https://yourcompany.com/jobs/lead-engineer"
  }'
```

**Scrape Career Page:**
```bash
# The AI will automatically detect all jobs on the page
curl -X POST http://localhost:8000/api/vacancies/sync \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourcompany.com/careers"
  }'
```

### 3. Signal Detection

**Manual Trigger:**
```bash
curl -X POST http://localhost:8000/api/monitor/run
```

**Setup Cron Job (Daily at 8 AM):**
```bash
crontab -e

# Add this line:
0 8 * * * curl -X POST http://localhost:8000/api/monitor/run
```

### 4. Sharing Alerts

Via UI: Click "Share via Slack/Teams" on any talent profile

Via API:
```bash
curl -X POST http://localhost:8000/api/signals/share \
  -H "Content-Type: application/json" \
  -d '{
    "talentId": 1,
    "signalType": "TENURE EXPIRY",
    "channel": "slack"
  }'
```

---

## 💰 Cost Breakdown (for 2000 profiles)

### Monthly Costs

| Service | Purpose | Cost |
|---------|---------|------|
| **Gemini AI** | Matching & briefings | Free tier (up to 60/min) |
| **Serper.dev** | News/signal search | $50 (5,000 searches) |
| **ScrapingDog** | LinkedIn scraping | $40 (optional) |
| **Railway/DO** | Backend hosting | $6-10 |
| **Vercel/Netlify** | Frontend hosting | Free |
| **Slack/Teams** | Notifications | Free |

**Total:** ~$96/month (or $56 without LinkedIn scraping)

**Compared to ProntoHQ:** €500+/month → **80% cost savings**

---

## 🧪 Testing with Mock Data

The system comes with 100 realistic mock profiles. To test:

1. Start backend: `python main.py`
2. Start frontend: `npm start`
3. Navigate to "My Talent Pool"
4. Click on any profile to see AI-generated briefing
5. Try filtering by signal type
6. Add a test vacancy URL to see matching

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check database
ls -la /home/claude/talentdog/database/
```

### Frontend connection error
```bash
# Verify backend is running
curl http://localhost:8000/

# Check .env file
cat frontend/.env
# Should contain: REACT_APP_API_URL=http://localhost:8000
```

### API keys not working
```bash
# Test Gemini API
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"

# Test Serper
curl -X POST https://google.serper.dev/search \
  -H "X-API-KEY: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"q":"test"}'
```

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs (when backend is running)
- **Database Schema:** See `backend/main.py` → `init_database()`
- **Frontend Components:** See `frontend/src/App.jsx`

---

## 🎉 You're Ready!

TalentDog is now set up. Here's what you can do:

1. ✅ Import your talent pool
2. ✅ Add vacancy URLs
3. ✅ Let AI generate matches
4. ✅ Share briefings with team
5. ✅ Monitor signals daily

**Need help?** The code is fully documented and ready to customize for your needs.
