"""
TalentDog Backend - Intelligence-First Recruitment Platform
FastAPI backend met Gemini AI, web scraping en signal detection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import sqlite3
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import os

app = FastAPI(title="TalentDog API", version="2.0")

# CORS configuratie voor React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In productie: vervang met je frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CONFIGURATIE ====================
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")
SCRAPINGDOG_KEY = os.getenv("SCRAPINGDOG_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL", "")

# Industrie benchmarks voor tenure analysis
INDUSTRY_BENCHMARKS = {
    "Technology": 1.8,
    "Finance": 3.5,
    "Legal": 4.2,
    "Consulting": 2.1,
    "Retail": 1.2,
    "Healthcare": 3.8,
    "Cloud Infrastructure": 2.0,
    "Artificial Intelligence": 1.9,
    "E-commerce": 2.2,
    "FinTech": 2.0,
}

# ==================== DATA MODELS ====================
class TalentProfile(BaseModel):
    name: str
    role: str
    currentCompany: str
    location: str
    sector: str
    linkedinUrl: Optional[str] = None
    email: Optional[str] = None
    startDate: Optional[str] = None

class Vacancy(BaseModel):
    title: str
    url: str
    department: Optional[str] = None
    location: Optional[str] = None

class SignalAlert(BaseModel):
    talentId: int
    signalType: str
    channel: str  # 'slack' | 'teams' | 'email'

# ==================== DATABASE SETUP ====================
def init_database():
    """Initialize SQLite database with all tables"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    cursor = conn.cursor()
    
    # Talent profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talent_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            current_company TEXT,
            location TEXT,
            sector TEXT,
            linkedin_url TEXT,
            email TEXT,
            start_date TEXT,
            tenure_months INTEGER,
            last_snippet TEXT,
            signal_type TEXT,
            signal_description TEXT,
            points INTEGER DEFAULT 0,
            photo_url TEXT,
            story TEXT,
            background TEXT,
            last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Vacancies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT,
            department TEXT,
            location TEXT,
            status TEXT DEFAULT 'Active',
            job_description TEXT,
            required_skills TEXT,
            seniority_level TEXT,
            posted_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Talent-Vacancy matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_id INTEGER,
            vacancy_id INTEGER,
            match_score INTEGER,
            match_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (talent_id) REFERENCES talent_profiles(id),
            FOREIGN KEY (vacancy_id) REFERENCES vacancies(id)
        )
    ''')
    
    # Company monitoring table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            last_news_check TIMESTAMP,
            layoff_detected BOOLEAN DEFAULT 0,
            ma_detected BOOLEAN DEFAULT 0,
            last_signal_date TIMESTAMP
        )
    ''')
    
    # Signals history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS signals_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            talent_id INTEGER,
            company_id INTEGER,
            signal_type TEXT,
            signal_data TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (talent_id) REFERENCES talent_profiles(id),
            FOREIGN KEY (company_id) REFERENCES companies(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== GEMINI AI INTEGRATION ====================
def call_gemini_api(prompt: str) -> str:
    """Call Gemini 1.5 Flash for AI analysis"""
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API key not configured. Using mock response."
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

# ==================== VACANCY SCRAPING ====================
def scrape_vacancy_page(url: str) -> Dict:
    """Scrape vacancy page and extract job details using Gemini AI"""
    try:
        # Use ScrapingDog if API key available, otherwise basic scraping
        if SCRAPINGDOG_KEY:
            api_url = f"https://api.scrapingdog.com/scrape?api_key={SCRAPINGDOG_KEY}&url={url}&dynamic=true"
            response = requests.get(api_url, timeout=30)
        else:
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()[:10000]  # First 10k chars
        
        # Use Gemini to extract structured data
        prompt = f"""
        Analyseer deze vacaturepagina en extraheer de volgende informatie als JSON:
        
        Text: {page_text}
        
        Geef terug:
        {{
            "is_overview_page": true/false,
            "vacancies": [
                {{
                    "title": "job title",
                    "url": "specific job url if available",
                    "department": "department name",
                    "location": "location",
                    "required_skills": ["skill1", "skill2"],
                    "seniority": "junior/medior/senior/lead",
                    "description": "short summary"
                }}
            ]
        }}
        
        Als het een enkele vacature is, geef 1 item in de array.
        Als het een overzichtspagina is, geef alle gevonden vacatures.
        """
        
        result = call_gemini_api(prompt)
        
        # Parse JSON from Gemini response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            return json.loads(result.strip())
        except:
            # Fallback to basic extraction
            return {
                "is_overview_page": False,
                "vacancies": [{
                    "title": soup.find('h1').text if soup.find('h1') else "Unknown Position",
                    "url": url,
                    "department": "Unknown",
                    "location": "Unknown",
                    "required_skills": [],
                    "seniority": "Unknown",
                    "description": page_text[:200]
                }]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scrape vacancy: {str(e)}")

# ==================== MATCHING ENGINE ====================
def match_talent_to_vacancy(talent_profile: Dict, vacancy: Dict) -> Dict:
    """Use Gemini AI to match talent to vacancy and generate briefing"""
    prompt = f"""
    Je bent een expert HR Intelligence Analyst. Match dit talent aan deze vacature:
    
    **TALENT:**
    - Naam: {talent_profile.get('name')}
    - Rol: {talent_profile.get('role')}
    - Bedrijf: {talent_profile.get('current_company')}
    - Sector: {talent_profile.get('sector')}
    - Signaal: {talent_profile.get('signal_type')}
    - Tenure: {talent_profile.get('tenure_months', 0)} maanden
    
    **VACATURE:**
    - Titel: {vacancy.get('title')}
    - Skills: {', '.join(vacancy.get('required_skills', []))}
    - Seniority: {vacancy.get('seniority')}
    - Beschrijving: {vacancy.get('description', '')}
    
    Geef als JSON terug:
    {{
        "match_score": 0-100,
        "match_reason": "waarom deze match nu goed is (1 zin)",
        "briefing": {{
            "market_context": "wat er speelt bij het bedrijf",
            "impact_score": 0-10,
            "tenure_status": "beschrijving tenure situatie",
            "risk_factors": "waarom deze persoon nu mogelijk openstaat",
            "match_reasons": "specifieke skills/ervaring die matchen",
            "angle": "hoe benadeer je deze persoon",
            "icebreaker": "concrete openingszin voor recruiter",
            "hook": "wat is de belangrijkste motivatie voor deze persoon"
        }}
    }}
    """
    
    result = call_gemini_api(prompt)
    
    try:
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        return json.loads(result.strip())
    except:
        # Fallback basic matching
        return {
            "match_score": 70,
            "match_reason": "Ervaring en skills komen overeen met de vacature",
            "briefing": {
                "market_context": "Analyse niet beschikbaar",
                "impact_score": 7,
                "tenure_status": f"{talent_profile.get('tenure_months', 0)} maanden bij huidige werkgever",
                "risk_factors": talent_profile.get('signal_description', ''),
                "match_reasons": "Relevante ervaring in de sector",
                "angle": "Focus op groei en nieuwe uitdagingen",
                "icebreaker": f"Hoi {talent_profile.get('name', '')}, ik zag je ervaring bij {talent_profile.get('current_company', '')}...",
                "hook": "Nieuwe uitdaging met meer verantwoordelijkheid"
            }
        }

# ==================== SIGNAL DETECTION ====================
def detect_tenure_expiry(talent_id: int) -> Optional[Dict]:
    """Check if talent has exceeded industry benchmark tenure"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT sector, tenure_months, name, current_company 
        FROM talent_profiles 
        WHERE id = ?
    ''', (talent_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    sector, tenure_months, name, company = result
    benchmark = INDUSTRY_BENCHMARKS.get(sector, 2.5) * 12  # Convert years to months
    
    if tenure_months >= benchmark * 0.95:  # 95% of benchmark
        return {
            "signal_type": "TENURE EXPIRY",
            "description": f"{name} heeft de {int(tenure_months)}-maanden drempel bereikt. "
                          f"Benchmark voor {sector} is {int(benchmark)} maanden. "
                          f"Window of Opportunity staat NU open.",
            "impact_score": min(10, int((tenure_months / benchmark) * 10))
        }
    
    return None

def detect_company_signals(company_name: str) -> List[Dict]:
    """Search for layoffs, M&A, and leadership changes"""
    signals = []
    
    if not SERPER_API_KEY:
        return signals
    
    # Search for layoffs
    layoff_query = f'"{company_name}" (layoff OR ontslagen OR reorganisatie)'
    
    # Search for M&A
    ma_query = f'"{company_name}" (acquired OR overname OR fusie OR merger)'
    
    for query, signal_type in [(layoff_query, "LAYOFFS"), (ma_query, "M&A / FUNDING")]:
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                json={"q": query, "tbm": "nws"},  # News search
                headers={'X-API-KEY': SERPER_API_KEY},
                timeout=10
            )
            
            data = response.json()
            
            if data.get('news'):
                for article in data['news'][:3]:  # Top 3 results
                    signals.append({
                        "signal_type": signal_type,
                        "title": article.get('title'),
                        "snippet": article.get('snippet'),
                        "date": article.get('date'),
                        "source": article.get('link')
                    })
        except:
            continue
    
    return signals

# ==================== NOTIFICATION SYSTEM ====================
def send_slack_notification(message: str):
    """Send notification to Slack"""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack webhook not configured")
        return
    
    try:
        requests.post(SLACK_WEBHOOK_URL, json={"text": message})
    except Exception as e:
        print(f"Failed to send Slack notification: {e}")

def send_teams_notification(card_data: Dict):
    """Send notification to Microsoft Teams"""
    if not TEAMS_WEBHOOK_URL:
        print("⚠️ Teams webhook not configured")
        return
    
    try:
        requests.post(TEAMS_WEBHOOK_URL, json=card_data)
    except Exception as e:
        print(f"Failed to send Teams notification: {e}")

# ==================== API ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()
    print("✅ TalentDog API is online!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "2.0",
        "features": [
            "AI-powered matching",
            "Real-time signal detection",
            "Vacancy scraping",
            "Multi-channel notifications"
        ]
    }

@app.get("/api/talent-pool")
async def get_talent_pool(signal_type: Optional[str] = None, limit: int = 100):
    """Get all talent profiles with optional signal filter"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if signal_type and signal_type != "All Signals":
        cursor.execute('''
            SELECT * FROM talent_profiles 
            WHERE signal_type LIKE ? 
            ORDER BY points DESC 
            LIMIT ?
        ''', (f'%{signal_type}%', limit))
    else:
        cursor.execute('''
            SELECT * FROM talent_profiles 
            ORDER BY points DESC 
            LIMIT ?
        ''', (limit,))
    
    profiles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Format for frontend
    formatted_profiles = []
    for i, profile in enumerate(profiles):
        formatted_profiles.append({
            "id": profile['id'],
            "rank": f"#{i+1}",
            "name": profile['name'],
            "role": profile['role'],
            "currentCompany": profile['current_company'],
            "location": profile['location'],
            "sector": profile['sector'],
            "points": profile['points'],
            "photo": profile['photo_url'],
            "signalType": profile['signal_type'],
            "signalDescription": profile['signal_description'],
            "matchedVacancy": "",  # Will be filled by matching
            "story": profile['story'],
            "background": profile['background'],
            "email": profile['email']
        })
    
    return formatted_profiles

@app.post("/api/talent/add")
async def add_talent(profile: TalentProfile):
    """Add new talent profile to pool"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    cursor = conn.cursor()
    
    # Calculate tenure if start_date provided
    tenure_months = 0
    if profile.startDate:
        try:
            start = datetime.strptime(profile.startDate, "%Y-%m-%d")
            tenure_months = (datetime.now() - start).days // 30
        except:
            pass
    
    # Detect initial signal
    signal = None
    if tenure_months > 0:
        benchmark = INDUSTRY_BENCHMARKS.get(profile.sector, 2.5) * 12
        if tenure_months >= benchmark * 0.95:
            signal = {
                "type": "TENURE EXPIRY",
                "description": f"Heeft {tenure_months} maanden tenure, benchmark is {int(benchmark)} maanden"
            }
    
    cursor.execute('''
        INSERT INTO talent_profiles 
        (name, role, current_company, location, sector, linkedin_url, email, start_date, tenure_months, signal_type, signal_description, points)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        profile.name,
        profile.role,
        profile.currentCompany,
        profile.location,
        profile.sector,
        profile.linkedinUrl,
        profile.email,
        profile.startDate,
        tenure_months,
        signal['type'] if signal else None,
        signal['description'] if signal else None,
        70 + (tenure_months if signal else 0)  # Base score + tenure bonus
    ))
    
    conn.commit()
    talent_id = cursor.lastrowid
    conn.close()
    
    return {"status": "success", "talent_id": talent_id}

@app.post("/api/vacancies/sync")
async def sync_vacancies(vacancy: Vacancy):
    """Scrape vacancy URL and add to database"""
    # Scrape vacancy page
    vacancy_data = scrape_vacancy_page(vacancy.url)
    
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    cursor = conn.cursor()
    
    vacancy_ids = []
    
    for vac in vacancy_data.get('vacancies', []):
        cursor.execute('''
            INSERT INTO vacancies 
            (title, url, department, location, job_description, required_skills, seniority_level, posted_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            vac.get('title', vacancy.title),
            vac.get('url', vacancy.url),
            vac.get('department', vacancy.department),
            vac.get('location', vacancy.location),
            vac.get('description', ''),
            json.dumps(vac.get('required_skills', [])),
            vac.get('seniority', ''),
            datetime.now().strftime("%Y-%m-%d")
        ))
        
        vacancy_ids.append(cursor.lastrowid)
    
    conn.commit()
    conn.close()
    
    # Trigger matching for new vacancies
    for vac_id in vacancy_ids:
        await match_vacancy_to_talent(vac_id)
    
    return {
        "status": "success",
        "vacancies_added": len(vacancy_ids),
        "vacancy_ids": vacancy_ids
    }

@app.get("/api/vacancies")
async def get_vacancies():
    """Get all vacancies with matched talent"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM vacancies ORDER BY created_at DESC')
    vacancies = [dict(row) for row in cursor.fetchall()]
    
    # Get matches for each vacancy
    for vacancy in vacancies:
        cursor.execute('''
            SELECT tp.*, m.match_score, m.match_reason
            FROM matches m
            JOIN talent_profiles tp ON m.talent_id = tp.id
            WHERE m.vacancy_id = ?
            ORDER BY m.match_score DESC
            LIMIT 10
        ''', (vacancy['id'],))
        
        matches = []
        for match in cursor.fetchall():
            match_dict = dict(match)
            matches.append({
                "id": match_dict['id'],
                "name": match_dict['name'],
                "role": match_dict['role'],
                "currentCompany": match_dict['current_company'],
                "photo": match_dict['photo_url'],
                "signalType": match_dict['signal_type'],
                "points": match_dict['match_score']
            })
        
        vacancy['matches'] = matches
    
    conn.close()
    
    return vacancies

async def match_vacancy_to_talent(vacancy_id: int):
    """Match a vacancy to all talent in the pool"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get vacancy details
    cursor.execute('SELECT * FROM vacancies WHERE id = ?', (vacancy_id,))
    vacancy = dict(cursor.fetchone())
    
    # Get all talent
    cursor.execute('SELECT * FROM talent_profiles LIMIT 100')
    talents = [dict(row) for row in cursor.fetchall()]
    
    # Match each talent
    for talent in talents:
        match_result = match_talent_to_vacancy(talent, vacancy)
        
        if match_result['match_score'] >= 60:  # Only save good matches
            cursor.execute('''
                INSERT INTO matches (talent_id, vacancy_id, match_score, match_reason)
                VALUES (?, ?, ?, ?)
            ''', (
                talent['id'],
                vacancy_id,
                match_result['match_score'],
                match_result['match_reason']
            ))
    
    conn.commit()
    conn.close()

@app.post("/api/signals/share")
async def share_signal(alert: SignalAlert):
    """Share signal alert via Slack/Teams/Email"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM talent_profiles WHERE id = ?', (alert.talentId,))
    talent = dict(cursor.fetchone())
    conn.close()
    
    message = f"""
🚀 HR INTELLIGENCE ALERT: {alert.signalType}

**Talent:** {talent['name']}
**Bedrijf:** {talent['current_company']}
**Signaal:** {talent['signal_description']}
**Score:** {talent['points']}

Dit talent is nu goed te benaderen voor nieuwe opportuniteiten.
    """
    
    if alert.channel == 'slack':
        send_slack_notification(message)
    elif alert.channel == 'teams':
        send_teams_notification({"text": message})
    
    return {"status": "success", "message": "Alert verstuurd"}

@app.post("/api/monitor/run")
async def run_daily_monitor():
    """Run daily monitoring check (called by cron job)"""
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    cursor = conn.cursor()
    
    # Check tenure for all profiles
    cursor.execute('SELECT id, name FROM talent_profiles')
    talents = cursor.fetchall()
    
    new_signals = 0
    
    for talent_id, name in talents:
        signal = detect_tenure_expiry(talent_id)
        if signal:
            cursor.execute('''
                UPDATE talent_profiles 
                SET signal_type = ?, signal_description = ?, points = points + 10
                WHERE id = ?
            ''', (signal['signal_type'], signal['description'], talent_id))
            new_signals += 1
    
    # Check companies for layoffs/M&A
    cursor.execute('SELECT DISTINCT current_company FROM talent_profiles')
    companies = cursor.fetchall()
    
    for (company,) in companies:
        signals = detect_company_signals(company)
        for signal in signals:
            # Update all talent at this company
            cursor.execute('''
                UPDATE talent_profiles 
                SET signal_type = ?, signal_description = ?
                WHERE current_company = ? AND signal_type IS NULL
            ''', (signal['signal_type'], signal['snippet'], company))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "new_signals_detected": new_signals,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
