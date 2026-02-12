# 🚀 TalentDog - Intelligence-First Recruitment Platform

**Automatically detect career signals, match talent to vacancies, and generate AI-powered recruitment briefings.**

![TalentDog Banner](https://img.shields.io/badge/TalentDog-HR_Intelligence-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=flat-square)
![React](https://img.shields.io/badge/React-18+-blue?style=flat-square)
![AI Powered](https://img.shields.io/badge/AI-Gemini_1.5-orange?style=flat-square)

---

## ✨ Features

- ✅ **AI-Powered Matching** - Gemini 1.5 Flash automatically matches talent to vacancies
- ✅ **Signal Detection** - Monitor 2000+ profiles for tenure expiry, layoffs, M&A, and leadership changes
- ✅ **Smart Scraping** - Extract job details from any career page
- ✅ **HR Intelligence Briefings** - Get actionable recruitment strategies for each talent
- ✅ **Multi-Channel Alerts** - Push notifications to Slack, Teams, or Email
- ✅ **Cost Effective** - ~$96/month vs $500+ for competitors (80% savings)

---

## 🎯 What Problem Does This Solve?

Traditional recruitment tools are **reactive** - they wait for candidates to apply.

**TalentDog is PROACTIVE:**

1. **Detects signals** - "Emma just hit 2.5 years at Company X (above industry average)"
2. **Finds opportunities** - "We have a Senior Dev role that matches her skills"
3. **Generates strategy** - "Approach her with focus on ownership and greenfield projects"
4. **Delivers briefing** - HR team gets a ready-to-use outreach message

---

## 🏃 Quick Start (3 minutes)

### Prerequisites
- Python 3.10+
- Node.js 18+

### Setup

```bash
# 1. Navigate to project
cd talentdog

# 2. Start Backend
cd backend
pip install -r requirements.txt
python main.py

# 3. Start Frontend (new terminal)
cd frontend
npm install
npm start
```

**🎉 Done!** Open http://localhost:3000

The app will load with 100 realistic mock profiles. You can start testing immediately.

---

## 📊 Architecture

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   React     │ ────▶ │   FastAPI    │ ────▶ │  Gemini AI  │
│  Frontend   │       │   Backend    │       │  (Matching) │
└─────────────┘       └──────────────┘       └─────────────┘
                            │
                            ├─▶ SQLite (2000 profiles)
                            ├─▶ Serper.dev (News)
                            ├─▶ ScrapingDog (LinkedIn)
                            └─▶ Slack/Teams (Alerts)
```

---

## 🔑 Configuration

### Required for Full Functionality

1. **Gemini API** (AI Matching)
   - Get key: https://makersuite.google.com/app/apikey
   - Free tier available

2. **Serper.dev** (Signal Detection)
   - Get key: https://serper.dev
   - $50/month for 5,000 searches

### Optional

3. **ScrapingDog** (LinkedIn Scraping)
   - $40/month - can use mock data instead

4. **Slack/Teams** (Notifications)
   - Free - get webhooks from respective platforms

**Setup:** Copy `.env.example` to `.env` in both backend and frontend folders, then add your keys.

---

## 💡 Core Workflows

### 1. Add Talent to Pool

**Via UI:**
- Click "Add Talent" in sidebar
- Fill in LinkedIn URL or manual details

**Via API:**
```bash
curl -X POST http://localhost:8000/api/talent/add \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Emma de Vries",
    "role": "Senior Developer",
    "currentCompany": "TechCorp",
    "startDate": "2022-01-15",
    "sector": "Technology"
  }'
```

### 2. Scrape Vacancies

```bash
# Paste any career page URL
curl -X POST http://localhost:8000/api/vacancies/sync \
  -d '{"url": "https://yourcompany.com/careers"}'

# AI will extract all jobs and requirements
```

### 3. View Matches

- Navigate to "My Vacancies"
- Each vacancy shows top matching talent with scores
- Click any match to see AI-generated briefing

### 4. Share with Team

- Click on any talent profile
- Click "Share via Slack" or "Share via Teams"
- Team receives full intelligence report

---

## 📈 Signal Types Detected

| Signal | Description | Use Case |
|--------|-------------|----------|
| **TENURE EXPIRY** | Talent exceeds industry avg tenure | "Emma has been at Google for 3.5 years (avg is 2.8)" |
| **LAYOFFS** | Company announces restructuring | "TechCorp laid off 15%, survivors seeking stability" |
| **M&A / FUNDING** | Acquisition or major funding | "Startup acquired by BigCorp, culture clash likely" |
| **LEADERSHIP SHIFT** | New C-level executive | "New CTO hired, previous roadmap in flux" |
| **CORPORATE SHOCKWAVE** | Major company event | "IPO announced, equity lock-up ending soon" |

---

## 🌐 Deployment

### Option 1: Railway (Recommended)

**Backend:**
```bash
cd backend
railway init
railway up
# Add env vars in Railway dashboard
```

**Frontend:**
```bash
cd frontend
npm run build
vercel --prod
```

**Cost:** ~$10/month

### Option 2: DigitalOcean

Full guide in `SETUP_GUIDE.md`

**Cost:** $6/month droplet + free frontend

---

## 💰 Total Cost Breakdown

| Service | Monthly Cost |
|---------|-------------|
| Gemini AI | Free (60/min) |
| Serper.dev | $50 |
| ScrapingDog (optional) | $40 |
| Hosting (Railway) | $10 |
| **TOTAL** | **$100/month** |

**vs ProntoHQ:** €500+/month → **80% savings**

---

## 🛠️ Tech Stack

- **Frontend:** React 18, Tailwind CSS, Lucide Icons
- **Backend:** FastAPI, Python 3.10+
- **Database:** SQLite (can swap to PostgreSQL)
- **AI:** Google Gemini 1.5 Flash
- **Scraping:** BeautifulSoup4, ScrapingDog
- **Search:** Serper.dev (Google News API)

---

## 📚 Documentation

- **Full Setup Guide:** [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- **API Documentation:** http://localhost:8000/docs (when running)
- **Database Schema:** See `backend/main.py` → `init_database()`

---

## 🔧 Troubleshooting

### Backend won't start
```bash
python --version  # Should be 3.10+
pip install --upgrade -r requirements.txt
```

### Frontend can't connect
```bash
# Check backend is running
curl http://localhost:8000/

# Verify .env file
cat frontend/.env
# Should have: REACT_APP_API_URL=http://localhost:8000
```

### No signals detected
- Verify `SERPER_API_KEY` is set in backend/.env
- Run manual trigger: `curl -X POST http://localhost:8000/api/monitor/run`

---

## 🎓 Example Use Cases

### 1. Proactive Outreach
"We have 12 Senior Developers at competitors who hit 2+ year tenure this month. Let's reach out before they start job hunting."

### 2. Post-Layoff Targeting
"Google announced 5% cuts. We have 8 matched profiles from their Cloud team. Strike now while they're actively looking."

### 3. M&A Arbitrage
"Startup X was acquired 30 days ago. Their top IC's equity is locked up for 6 months. Add to pipeline for Q3 outreach."

---

## 📦 What's Included

```
talentdog/
├── backend/
│   ├── main.py              # FastAPI app with all endpoints
│   ├── requirements.txt     # Python dependencies
│   └── .env.example        # Environment template
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── index.js        # Entry point
│   │   └── index.css       # Tailwind styles
│   ├── package.json        # Node dependencies
│   └── .env.example        # Frontend config
├── database/
│   └── talentdog.db        # SQLite (auto-created)
├── SETUP_GUIDE.md          # Detailed setup instructions
└── README.md               # This file
```

---

## 🚀 Roadmap

- [ ] Chrome Extension for 1-click LinkedIn import
- [ ] Email outreach templates
- [ ] CRM integrations (HubSpot, Salesforce)
- [ ] Mobile app (iOS/Android)
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard

---

## 📄 License

This project is built for demonstration and educational purposes. Modify and use as you see fit.

---

## 🙏 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)
- [Gemini AI](https://ai.google.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)

---

## 🤝 Support

Need help? Check:
1. [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Comprehensive setup instructions
2. API Docs - http://localhost:8000/docs
3. Code comments - Heavily documented codebase

---

**Ready to revolutionize your recruitment process? Let's go! 🚀**

```bash
cd talentdog/backend && python main.py
cd talentdog/frontend && npm start
```

Open http://localhost:3000 and start building your intelligence-first talent pipeline!
