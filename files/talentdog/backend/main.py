from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title="TalentDog Intelligence v2.2")

# CORS toestaan voor je frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database paden instellen voor de Docker container
DB_DIR = os.path.join(os.getcwd(), "database")
DB_PATH = os.path.join(DB_DIR, "talentdog.db")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# --- Smart Scheduler Config ---
SIGNAL_CONFIG = {
    "layoffs": {"interval_days": 1, "q": '"{company}" (ontslaggolf OR layoffs OR reorganisatie)', "tbs": "qdr:d"},
    "ma_activity": {"interval_days": 14, "q": '"{company}" (overgenomen OR acquisitie OR merger)', "tbs": "qdr:m"},
    "tenure": {"interval_days": 30, "q": 'site:linkedin.com/in/ "{company}" "3 years" OR "3 jaar"', "tbs": ""},
    "leadership": {"interval_days": 7, "q": '"{company}" ("nieuwe" OR "welkom") (CEO OR VP OR Director)', "tbs": "qdr:m"},
    "sentiment": {"interval_days": 14, "q": 'site:glassdoor.nl "{company}" ("niet aanbevolen" OR "toxic")', "tbs": "qdr:m3"}
}

def init_database():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS cached_signals (company TEXT, type TEXT, data TEXT, timestamp TIMESTAMP)')
    cursor.execute('CREATE TABLE IF NOT EXISTS signal_scheduler (company TEXT, type TEXT, next_check TIMESTAMP, PRIMARY KEY(company, type))')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()

# CRUCIAAL: Root endpoint voor de Railway Healthcheck
@app.get("/")
async def root():
    return {"status": "TalentDog Engine is Online", "port_active": os.environ.get("PORT", "8080")}

@app.get("/api/vacancies")
async def get_vacancies():
    """Get all vacancies"""
    # Mock data voor nu - later kun je dit uit een database halen
    return [
        {
            "id": 1,
            "title": "Senior Software Engineer",
            "company": "ASML",
            "location": "Eindhoven, NL",
            "department": "Engineering",
            "type": "Full-time",
            "status": "Open"
        },
        {
            "id": 2,
            "title": "Product Manager",
            "company": "Adyen",
            "location": "Amsterdam, NL",
            "department": "Product",
            "type": "Full-time",
            "status": "Open"
        },
        {
            "id": 3,
            "title": "Data Scientist",
            "company": "Booking.com",
            "location": "Amsterdam, NL",
            "department": "Data & Analytics",
            "type": "Full-time",
            "status": "Open"
        }
    ]

@app.get("/api/talent-pool")
async def get_talent_pool(limit: int = 100):
    """Get talent pool with optional limit"""
    # Mock talent pool data
    first_names = ['Emma', 'Liam', 'Sophie', 'Noah', 'Lisa', 'Lucas', 'Anna', 'Max', 'Julia', 'Tom']
    last_names = ['de Vries', 'Jansen', 'Bakker', 'Visser', 'Smit', 'Meijer', 'de Boer', 'Mulder']
    roles = ['Senior DevOps Engineer', 'Product Lead', 'Data Scientist', 'Cloud Architect']
    companies = ['ASML', 'Adyen', 'Picnic', 'Bunq', 'Booking.com', 'Philips', 'Shell']
    cities = ['Amsterdam', 'Rotterdam', 'Utrecht', 'Eindhoven', 'Den Haag']
    sectors = ['Technology', 'FinTech', 'E-commerce', 'Healthcare Tech']
    signal_types = ['TENURE EXPIRY', 'CORPORATE SHOCKWAVE', 'LAYOFFS', 'M&A / FUNDING']
    
    profiles = []
    for i in range(min(limit, 100)):
        name = f"{first_names[i % len(first_names)]} {last_names[i % len(last_names)]}"
        profiles.append({
            "id": i + 1,
            "rank": f"#{i + 1}",
            "name": name,
            "role": roles[i % len(roles)],
            "currentCompany": companies[i % len(companies)],
            "location": f"{cities[i % len(cities)]}, NL",
            "sector": sectors[i % len(sectors)],
            "points": 50 + (i % 50),
            "photo": f"https://images.pexels.com/photos/{220453 + (i % 10)}/pexels-photo.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop",
            "signalType": signal_types[i % len(signal_types)],
            "signalDescription": f"{name} heeft belangrijke ontwikkelingen.",
            "story": f"{name} is klaar voor een nieuwe uitdaging.",
            "background": f"Ervaren {roles[i % len(roles)]}.",
            "email": f"{name.lower().replace(' ', '.')}@example.com"
        })
    
    return profiles

@app.get("/api/detect-signals/{company}")
async def get_smart_signals(company: str):
    if not SERPER_API_KEY: 
        raise HTTPException(status_code=500, detail="Serper Key Missing")
    
    final_report = []
    # (Rest van je logica blijft hetzelfde...)
    # [Hieronder de verkorte logica voor de leesbaarheid]
    return {"company": company, "signals": "Data wordt opgehaald..."} # Vul aan met de rest van de eerdere logica

if __name__ == "__main__":
    # Railway gebruikt poort 8080 volgens je instellingen
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
