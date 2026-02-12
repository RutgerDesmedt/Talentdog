# 🎯 TalentDog - Getting Started Guide

**For Recruiters, HR Managers, and Non-Technical Users**

---

## What is TalentDog?

TalentDog is your intelligent recruitment assistant that:

1. **Monitors** 2000+ talent profiles for career signals
2. **Detects** when someone is likely to change jobs
3. **Matches** them to your open vacancies
4. **Generates** personalized outreach strategies

Think of it as having an AI analyst working 24/7 to find your next hire.

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Access TalentDog

Open your browser and go to:
```
http://localhost:3000
```

(Or the URL your IT team provided)

### Step 2: Understand the Interface

You'll see 3 main tabs:

#### 📊 My Talent Pool
- See all tracked talent
- Filter by signal type (Tenure Expiry, Layoffs, etc.)
- Click any profile for detailed AI briefing

#### 💼 My Vacancies
- View all open positions
- See matched candidates for each role
- Add new vacancy URLs

#### ⚙️ System Settings
- View pool statistics
- Configure notifications

---

## 📘 How to Use TalentDog

### 1. Add Talent to Your Pool

**Option A: Upload a List**
(Ask your IT team to help import a CSV with LinkedIn URLs)

**Option B: Add Manually**
1. Click "Add Talent" button
2. Paste LinkedIn profile URL
3. Click "Save"
4. AI will automatically extract details

**Option C: Let it Run**
TalentDog comes pre-loaded with 100 sample profiles for testing!

---

### 2. Add Your Open Vacancies

**This is the magic part!**

1. Go to "My Vacancies" tab
2. Copy the URL of any job posting (yours or a competitor's)
3. Paste it in the "Paste vacancy URL" field
4. Click "Sync Vacancy"

**What happens next:**
- AI reads the job description
- Extracts required skills
- Matches it against your talent pool
- Shows you the top candidates

**Examples of URLs that work:**
```
https://yourcompany.com/careers/senior-developer
https://boards.greenhouse.io/company/jobs/123456
https://jobs.lever.co/company/position
```

---

### 3. Understanding Signals

#### 🟠 TENURE EXPIRY
**What it means:** Someone has been at their current job longer than average for their industry.

**Why it matters:** People who've "learned everything" at their current role are most open to new challenges.

**Example:** "Mark has been at CloudScale for 2.5 years. Average in Cloud Infrastructure is 2.0 years."

**Action:** Reach out NOW before competitors do.

---

#### 🔴 LAYOFFS
**What it means:** The company recently announced job cuts.

**Why it matters:** Even people who kept their jobs are nervous and actively looking.

**Example:** "Picnic restructured hubs. Jasper's team shrank 30%."

**Action:** Offer stability and a fresh start.

---

#### 🟣 M&A / FUNDING
**What it means:** The company was acquired or got major funding.

**Why it matters:** Culture changes. Early employees often leave after acquisitions.

**Example:** "Aura AI was acquired by Meta 48 hours ago."

**Action:** Contact before equity packages are re-negotiated.

---

#### 🟡 LEADERSHIP SHIFT
**What it means:** New CEO/CTO was appointed.

**Why it matters:** Strategic direction changes. Some people won't align.

**Example:** "New CTO at Shell focuses on cost-cutting vs innovation."

**Action:** Present your role as a better cultural fit.

---

### 4. Reading AI Briefings

Click on any talent profile to see:

#### **Market Intelligence**
- What's happening at their company
- Why they might be open to moving
- Industry context

#### **Talent Analysis**
- Current tenure status
- Risk factors (why they'd leave)
- Matching reasons (why your role fits)

#### **Recruitment Action Plan**
- **Angle:** How to approach them
- **Icebreaker:** Exact first message to send
- **Hook:** Their main motivation

**Example Briefing:**

```
MARKET CONTEXT: 
ASML is consolidating after EUV growth. Pioneers 
like Thomas seek new "blank canvas" challenges.

RECRUITMENT ANGLE:
Focus on ownership and greenfield projects.

ICEBREAKER:
"Thomas, impressive how you scaled ASML's cloud 
infrastructure. Usually after such a milestone, 
experts seek a new canvas where their impact is 
more direct..."

HOOK:
Autonomy and technical ownership
```

**You can copy/paste this into LinkedIn!**

---

### 5. Share with Your Team

1. Click on any talent profile
2. Click **"Share via Slack"** or **"Share via Teams"**
3. Your team receives the full briefing

The message includes:
- Candidate name and current role
- Signal detected
- Match score
- Why to reach out NOW

---

## 📈 Daily Workflow (15 Minutes)

**Morning Routine:**

1. **Check "My Talent Pool"**
   - Look for new High Priority signals (red badges)
   - These are the hottest leads

2. **Review Matches**
   - Go to "My Vacancies"
   - See new candidates matched overnight

3. **Read AI Briefings**
   - Click top 3 matches
   - Copy the "Icebreaker" message

4. **Take Action**
   - Send LinkedIn messages
   - Share with hiring managers via Slack/Teams

**That's it!** 15 minutes per day to stay ahead of your recruiting pipeline.

---

## 💡 Pro Tips from HR Leaders

### Tip #1: Act Fast on "Corporate Shockwave" Signals
When a company gets acquired or announces layoffs, you have a 30-60 day window before competitors flood the market.

### Tip #2: Use Tenure Signals for "Passive" Candidates
People at 2+ years aren't actively looking but are most receptive to good opportunities.

### Tip #3: Personalize the Icebreaker
The AI gives you the strategy. Add a personal touch:
```
AI: "Impressive how you scaled infrastructure..."
You: "Impressive how you scaled infrastructure at ASML! 
      I saw your talk at KubeCon - really insightful."
```

### Tip #4: Share Context with Hiring Managers
Don't just send a resume. Share the AI briefing:
```
"This candidate is a 94% match for our Lead role. 
They just hit 2.5 years (above industry avg) and their 
company is restructuring. Perfect timing to reach out."
```

### Tip #5: Track Your Success
When someone you contacted gets hired, note which signal type led to them. Over time, you'll learn which signals work best for your industry.

---

## 🆘 Common Questions

**Q: How often does the data update?**  
A: Automatically every 24 hours. You can also trigger manual updates.

**Q: Can I import my existing talent pool?**  
A: Yes! Ask your IT team to import via CSV or API.

**Q: What if I don't have Gemini/Serper API keys?**  
A: TalentDog works with sample data for testing. For production, you'll need API keys (IT can set this up).

**Q: Is this legal?**  
A: Yes! TalentDog only uses publicly available data (LinkedIn public profiles, company news). Same as what you'd Google manually.

**Q: How much does it cost?**  
A: About $100/month for 2000 profiles. Compare that to recruiting agencies (15-25% of salary) or platforms like LinkedIn Recruiter ($8,000+/year).

---

## 📞 Need Help?

**Can't log in?**  
Contact your IT team or system administrator.

**Feature request?**  
All code is open source and customizable!

**Want training?**  
This guide covers 90% of daily use. For advanced features, see the Technical Documentation.

---

## ✅ You're Ready!

**Next steps:**

1. ✅ Explore the 100 sample profiles
2. ✅ Try adding a test vacancy URL
3. ✅ Read a few AI briefings
4. ✅ Share one with your team via Slack/Teams
5. ✅ Import your real talent pool

**Welcome to intelligence-first recruiting! 🚀**
