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
