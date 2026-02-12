# 🚀 TalentDog - Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Local Testing (Complete This First)
- [ ] Backend runs successfully (`python backend/main.py`)
- [ ] Frontend runs successfully (`npm start` in frontend/)
- [ ] Database is seeded with sample data
- [ ] API tests pass (`python backend/test_api.py`)
- [ ] All 100 mock profiles visible in UI
- [ ] Can add new talent via UI
- [ ] Can sync vacancy URLs
- [ ] Slack/Teams notifications work (if configured)

### 2. Environment Configuration
- [ ] `backend/.env` created from `.env.example`
- [ ] `frontend/.env` created with correct API URL
- [ ] Gemini API key added (required for AI features)
- [ ] Serper API key added (required for signal detection)
- [ ] ScrapingDog key added (optional - can use mock data)
- [ ] Slack webhook URL added (optional)
- [ ] Teams webhook URL added (optional)

### 3. Production Readiness
- [ ] Change `REACT_APP_API_URL` to production backend URL
- [ ] Update CORS settings in `backend/main.py` (line 21)
- [ ] Review security settings
- [ ] Test all API endpoints work remotely
- [ ] Verify database is backed up

---

## 🌐 Deployment Options

### Option 1: Quick Deploy (Railway + Vercel) - Recommended

**Backend (Railway):**
```bash
cd backend
npm install -g @railway/cli
railway login
railway init
railway up

# In Railway dashboard:
# - Add all environment variables from .env
# - Note the deployed URL (e.g., https://talentdog-backend.railway.app)
```

**Frontend (Vercel):**
```bash
cd frontend
npm run build

# Update .env
echo "REACT_APP_API_URL=https://talentdog-backend.railway.app" > .env

npx vercel --prod

# When prompted:
# - Link to your Vercel account
# - Accept default settings
# - Note the deployed URL
```

**Estimated Time:** 15 minutes  
**Monthly Cost:** ~$10 (Railway) + Free (Vercel)

---

### Option 2: Docker Deployment (Any VPS)

**On your server:**
```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your code
git clone your-repo talentdog
cd talentdog

# Create .env file
cat > .env << EOF
GEMINI_API_KEY=your_key
SERPER_API_KEY=your_key
SCRAPINGDOG_KEY=your_key
SLACK_WEBHOOK_URL=your_webhook
TEAMS_WEBHOOK_URL=your_webhook
EOF

# Start services
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

**Nginx Reverse Proxy (Optional):**
```nginx
server {
    listen 80;
    server_name talentdog.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

**Estimated Time:** 30 minutes  
**Monthly Cost:** $6-20 (depending on VPS provider)

---

### Option 3: DigitalOcean Droplet (Manual Setup)

**1. Create Droplet ($6/month)**
- Ubuntu 22.04
- Basic plan
- SSH key authentication

**2. Connect & Setup:**
```bash
ssh root@your-droplet-ip

# Install dependencies
apt update
apt install python3-pip python3-venv nodejs npm nginx -y

# Clone code
cd /var/www
git clone your-repo talentdog
cd talentdog

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd service
cat > /etc/systemd/system/talentdog-backend.service << EOF
[Unit]
Description=TalentDog Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/talentdog/backend
Environment="PATH=/var/www/talentdog/backend/venv/bin"
ExecStart=/var/www/talentdog/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable talentdog-backend
systemctl start talentdog-backend

# Setup frontend
cd /var/www/talentdog/frontend
npm install
REACT_APP_API_URL=http://your-ip:8000 npm run build

# Configure Nginx
cat > /etc/nginx/sites-available/talentdog << EOF
server {
    listen 80;
    server_name _;
    
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
rm /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

**3. Setup SSL (Optional but Recommended):**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d talentdog.yourdomain.com
```

**Estimated Time:** 45-60 minutes  
**Monthly Cost:** $6

---

## 📊 Post-Deployment Verification

**1. Backend Health Check:**
```bash
curl https://your-backend-url/
# Should return: {"status": "online", "version": "2.0", ...}
```

**2. Frontend Access:**
```bash
curl https://your-frontend-url/
# Should return HTML
```

**3. API Functionality:**
```bash
# Test talent pool
curl https://your-backend-url/api/talent-pool?limit=5

# Test manual trigger
curl -X POST https://your-backend-url/api/monitor/run
```

**4. UI Testing:**
- Open frontend URL in browser
- Navigate to "My Talent Pool" - should see profiles
- Click on a profile - should see detailed view
- Navigate to "My Vacancies" - should load
- Try adding a test vacancy URL

---

## 🔄 Ongoing Maintenance

### Daily Signal Detection (Cron Job)

**On your server:**
```bash
crontab -e

# Add this line to run daily at 8 AM:
0 8 * * * curl -X POST https://your-backend-url/api/monitor/run
```

**Via external service (e.g., EasyCron):**
- Create account at EasyCron.com
- Add cron job: `POST https://your-backend-url/api/monitor/run`
- Set schedule: Daily at 8:00 AM

### Database Backups

**Automated backup script:**
```bash
#!/bin/bash
# backup-db.sh

DATE=$(date +%Y%m%d)
cp /path/to/talentdog/database/talentdog.db \
   /path/to/backups/talentdog-$DATE.db

# Keep only last 30 days
find /path/to/backups -name "talentdog-*.db" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup-db.sh
```

### Monitoring

**Setup health check monitoring:**
- UptimeRobot (Free): Monitor frontend/backend URLs
- Better Uptime: More advanced monitoring
- Set alert email/Slack notifications

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check logs
journalctl -u talentdog-backend -f

# Or if running directly
cd backend
source venv/bin/activate
python main.py
# Look for error messages
```

### Frontend shows "Failed to fetch"
```bash
# Check if API URL is correct
cat frontend/.env

# Verify backend is accessible
curl https://your-backend-url/

# Check browser console for CORS errors
# If present, update CORS settings in backend/main.py
```

### Database errors
```bash
# Reinitialize database
python backend/main.py
# Then seed again
python backend/seed_database.py
```

---

## 💡 Pro Tips

1. **Start Small:** Deploy locally first, test thoroughly, then deploy to production
2. **Environment Variables:** Never commit `.env` files to git
3. **SSL Certificates:** Use Let's Encrypt (free) via Certbot
4. **Database:** Consider upgrading to PostgreSQL for production
5. **Caching:** Add Redis for better performance with large datasets
6. **Monitoring:** Set up error tracking (e.g., Sentry)

---

## 📞 Support Resources

- **Setup Guide:** `SETUP_GUIDE.md`
- **API Documentation:** `http://your-backend-url/docs`
- **Test Suite:** Run `python backend/test_api.py`
- **Database Schema:** See `backend/main.py` → `init_database()`

---

## ✅ Deployment Complete!

Once deployed, your team can:
- ✅ Access TalentDog from anywhere
- ✅ Import 2000 talent profiles
- ✅ Add vacancy URLs for auto-matching
- ✅ Receive daily signal alerts
- ✅ Share AI briefings via Slack/Teams

**Need help?** All code is heavily documented and ready to customize!
