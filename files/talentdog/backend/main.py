from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests

app = FastAPI(title="TalentDog API", version="2.0")

# --- CORS Settings (Zorgt dat je frontend met je backend kan praten) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Config ---
DB_PATH = os.getenv("DB_PATH", "/home/claude/talentdog/database/talentdog.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY") # Nieuw: Voor Serper
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# --- Database init ---
def init_database():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talent_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT,
            currentCompany TEXT,
            location TEXT,
            sector TEXT,
            linkedinUrl TEXT,
            email TEXT,
            startDate TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()
    print("✅ TalentDog API is online!")

# --- Models ---
class Talent(BaseModel):
    name: str
    role: str = None
    currentCompany: str = None
    location: str = None
    sector: str = None
    linkedinUrl: str = None
    email: str = None
    startDate: str = None

class Vacancy(BaseModel):
    title: str
    url: str

# --- Signal Scanner Logica (Nieuw) ---
class SignalScanner:
    def __init__(self):
        self.url = "https://google.serper.dev/search"
        self.headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }

    def scan_company(self, company_name: str):
        spotlights = [
            {"id": "layoffs", "label": "Layoffs", "q": f'"{company_name}" (ontslaggolf OR layoffs OR reorganisatie)', "tbs": "qdr:m"},
            {"id": "ma_activity", "label": "Overnames", "q": f'"{company_name}" (overgenomen OR acquisitie OR merger)', "tbs": "qdr:m6"},
            {"id": "tenure", "label": "Tenure Expire", "q": f'site:linkedin.com/in/ "{company_name}" "3 years" OR "3 jaar"', "tbs": ""},
            {"id": "leadership", "label": "Leadership Shift", "q": f'"{company_name}" ("nieuwe" OR "welkom" OR "starts as") (CEO OR VP OR Director)', "tbs": "qdr:m"},
            {"id": "sentiment", "label": "Glassdoor Sentiment", "q": f'site:glassdoor.nl "{company_name}" ("niet aanbevolen" OR "toxic")', "tbs": "qdr:m3"}
        ]
        
        detected_signals = []
        for spot in spotlights:
            payload = {"q": spot["q"], "tbs": spot["tbs"], "num": 4}
            try:
                resp = requests.post(self.url, headers=self.headers, json=payload)
                data = resp.json()
                if data.get("organic"):
                    detected_signals.append({
                        "signal_id": spot["id"],
                        "signal_label": spot["label"],
                        "found_items": [{"title": i.get("title"), "snippet": i.get("snippet"), "link": i.get("link")} for i in data["organic"]]
                    })
            except: continue
        return detected_signals

# --- Utility functions ---
def generate_gemini_content(prompt: str) -> str:
    if not GEMINI_API_KEY: return "⚠️ GEMINI_API_KEY not set"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload)
    if resp.status_code != 200: return f"⚠️ Gemini error"
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def send_slack_message(message: str):
    if SLACK_WEBHOOK_URL: requests.post(SLACK_WEBHOOK_URL, json={"text": message})

def send_teams_message(message: str):
    if TEAMS_WEBHOOK_URL: requests.post(TEAMS_WEBHOOK_URL, json={"text": message})

# --- Endpoints ---
@app.get("/")
async def root():
    return {"status": "online", "version": "2.1", "feature": "signal_detection_ready"}

# NIEUW ENDPOINT: Signaal Detectie
@app.get("/api/detect-signals/{company_name}")
async def get_signals(company_name: str):
    if not SERPER_API_KEY:
        raise HTTPException(status_code=500, detail="SERPER_API_KEY missing")
    scanner = SignalScanner()
    signals = scanner.scan_company(company_name)
    return {"company": company_name, "signals": signals}

@app.post("/api/talent/add")
async def add_talent(talent: Talent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO talent_profiles (name, role, currentCompany, location, sector, linkedinUrl, email, startDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (talent.name, talent.role, talent.currentCompany, talent.location, talent.sector, talent.linkedinUrl, talent.email, talent.startDate))
    conn.commit()
    conn.close()
    gemini_text = generate_gemini_content(f"Match talent: {talent.name}, role: {talent.role}")
    send_slack_message(f"New Talent: {talent.name} → {gemini_text}")
    return {"status": "success", "gemini_match": gemini_text}

@app.post("/api/vacancies/sync")
async def add_vacancy(vacancy: Vacancy):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO vacancies (title, url) VALUES (?, ?)', (vacancy.title, vacancy.url))
    conn.commit()
    conn.close()
    gemini_text = generate_gemini_content(f"Analyze vacancy: {vacancy.title}")
    send_slack_message(f"New Vacancy: {vacancy.title} → {gemini_text}")
    return {"status": "success", "gemini_analysis": gemini_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
