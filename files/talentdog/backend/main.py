from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os
import requests

app = FastAPI(title="TalentDog API", version="2.0")

# --- Config ---
DB_PATH = os.getenv("DB_PATH", "/home/claude/talentdog/database/talentdog.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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

# --- Utility functions ---
def generate_gemini_content(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "⚠️ GEMINI_API_KEY not set"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    resp = requests.post(url, json=payload)
    if resp.status_code != 200:
        return f"⚠️ Gemini error: {resp.text}"
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def send_slack_message(message: str):
    if SLACK_WEBHOOK_URL:
        requests.post(SLACK_WEBHOOK_URL, json={"text": message})

def send_teams_message(message: str):
    if TEAMS_WEBHOOK_URL:
        requests.post(TEAMS_WEBHOOK_URL, json={"text": message})

# --- Endpoints ---
@app.get("/")
async def root():
    return {"status": "online", "version": "2.0"}

@app.post("/api/talent/add")
async def add_talent(talent: Talent):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO talent_profiles 
        (name, role, currentCompany, location, sector, linkedinUrl, email, startDate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (talent.name, talent.role, talent.currentCompany, talent.location,
          talent.sector, talent.linkedinUrl, talent.email, talent.startDate))
    conn.commit()
    conn.close()

    # Gemini AI matching
    gemini_text = generate_gemini_content(f"Match talent: {talent.name}, role: {talent.role}")
    
    # Slack/Teams notifications
    send_slack_message(f"New Talent Added: {talent.name} → {gemini_text}")
    send_teams_message(f"New Talent Added: {talent.name} → {gemini_text}")

    return {"status": "success", "name": talent.name, "gemini_match": gemini_text}

@app.post("/api/vacancies/sync")
async def add_vacancy(vacancy: Vacancy):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vacancies (title, url)
        VALUES (?, ?)
    ''', (vacancy.title, vacancy.url))
    conn.commit()
    conn.close()

    # Gemini AI content generation
    gemini_text = generate_gemini_content(f"Analyze vacancy: {vacancy.title}, {vacancy.url}")

    # Slack/Teams notifications
    send_slack_message(f"New Vacancy Added: {vacancy.title} → {gemini_text}")
    send_teams_message(f"New Vacancy Added: {vacancy.title} → {gemini_text}")

    return {"status": "success", "title": vacancy.title, "gemini_analysis": gemini_text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
