from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import os
import uvicorn
from typing import Optional, List
from datetime import datetime

# --- CONFIGURATIE ---
app = FastAPI(title="TalentDog Enterprise ATS Integrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database pad (Railway Volume ondersteuning)
DB_PATH = os.path.join(os.getcwd(), "database", "talentdog.db")

# TESTING MODE - Altijd True voor jouw demo-omgeving
TESTING_MODE = os.getenv("TESTING_MODE", "true").lower() == "true"

# --- MODELLEN ---
class ATSConnectionRequest(BaseModel):
    provider: str
    subdomain: Optional[str] = None
    api_key: Optional[str] = None
    feed_url: Optional[str] = None

# --- DATABASE INITIALISATIE ---
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ats_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL UNIQUE,
            subdomain TEXT,
            api_key TEXT,
            feed_url TEXT,
            is_active INTEGER DEFAULT 1,
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            department TEXT,
            status TEXT DEFAULT 'Open',
            url TEXT UNIQUE,
            external_id TEXT,
            source_provider TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- MOCK DATA GENERATOR ---
class MockATSData:
    @staticmethod
    def get_mock_jobs(provider: str, company: str = "Demo Corp"):
        jobs = {
            "greenhouse": [
                {"title": "Senior Software Engineer", "id": "gh_1", "location": "Amsterdam", "dept": "Engineering"},
                {"title": "Product Manager", "id": "gh_2", "location": "Remote", "dept": "Product"}
            ],
            "lever": [
                {"title": "Frontend Developer", "id": "lv_1", "location": "Brussels", "dept": "Engineering"},
                {"title": "Data Scientist", "id": "lv_2", "location": "Antwerp", "dept": "Data"}
            ],
            "jobtoolz": [
                {"title": "Marketing Manager", "id": "jt_1", "location": "Ghent", "dept": "Marketing"},
                {"title": "Sales Representative", "id": "jt_2", "location": "Brussels", "dept": "Sales"}
            ],
            "recruitee": [
                {"title": "UX/UI Designer", "id": "rc_1", "location": "Rotterdam", "dept": "Design"},
                {"title": "Backend Engineer", "id": "rc_2", "location": "Amsterdam", "dept": "Engineering"}
            ],
            "workday": [
                {"title": "HR Business Partner", "id": "wd_1", "location": "Mechelen", "dept": "HR"}
            ],
            "icims": [
                {"title": "Customer Success Manager", "id": "ic_1", "location": "Eindhoven", "dept": "Success"}
            ],
            "smartrecruiters": [
                {"title": "Technical Writer", "id": "sr_1", "location": "Remote", "dept": "Product"}
            ],
            "bamboohr": [
                {"title": "Operations Manager", "id": "bh_1", "location": "The Hague", "dept": "Ops"}
            ]
        }
        
        selected_jobs = jobs.get(provider.lower(), [{"title": "General Position", "id": "gen_1", "location": "Benelux", "dept": "General"}])
        
        return [{
            "title": j["title"],
            "url": f"https://jobs.{provider}.com/{company}/{j['id']}",
            "id": j["id"],
            "location": j["location"],
            "department": j["dept"],
            "description": f"Dit is een gesimuleerde vacature voor {j['title']} via {provider}."
        } for j in selected_jobs]

# --- API ENDPOINTS ---

@app.get("/")
async def root():
    return {"message": "TalentDog ATS API Online", "mode": "TESTING" if TESTING_MODE else "PROD"}

@app.get("/health")
async def health():
    return {"status": "healthy", "testing_mode": TESTING_MODE}

@app.post("/api/ats/connect")
async def connect_ats(request: ATSConnectionRequest):
    provider = request.provider.lower()
    
    if TESTING_MODE:
        print(f"🧪 Mocking verbinding voor: {provider}")
        mock_jobs = MockATSData.get_mock_jobs(provider, request.subdomain or "Demo")
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 1. Sla configuratie op
            cursor.execute('''
                INSERT OR REPLACE INTO ats_configurations (provider, subdomain, is_active, last_sync)
                VALUES (?, ?, 1, ?)
            ''', (provider, request.subdomain, datetime.now()))
            
            # 2. Voeg mock vacatures toe
            for job in mock_jobs:
                cursor.execute('''
                    INSERT OR IGNORE INTO vacancies 
                    (title, url, external_id, location, department, source_provider, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (job['title'], job['url'], job['id'], job['location'], 
                      job['department'], provider, job['description']))
            
            conn.commit()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Verbonden met {provider} (TEST MODE)",
                "jobs_imported": len(mock_jobs)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Echte API logica zou hier komen
    raise HTTPException(status_code=400, detail="Echte API niet geconfigureerd.")

@app.get("/api/vacancies")
async def get_vacancies():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vacancies ORDER BY created_at DESC')
    vacancies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return vacancies

@app.post("/api/ats/sync")
async def sync_all():
    # In test mode is sync simpelweg een bevestiging
    return {"status": "success", "message": "Alle ATS systemen zijn gesynchroniseerd (Mock)"}

@app.delete("/api/ats/disconnect/{provider}")
async def disconnect_ats(provider: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM ats_configurations WHERE provider = ?', (provider.lower(),))
    cursor.execute('DELETE FROM vacancies WHERE source_provider = ?', (provider.lower(),))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"{provider} ontkoppeld."}

# --- SERVER START ---
if __name__ == "__main__":
    # Cruciaal voor Railway: lees de PORT variabele uit
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
