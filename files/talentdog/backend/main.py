from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests
from datetime import datetime, timedelta
import uvicorn

app = FastAPI(title="TalentDog Intelligence v2.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cruciaal: Gebruik een pad dat werkt binnen de Docker /app context
# Railway volume mount moet op /app/database staan
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
    # Maak de map aan als deze niet bestaat
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Tabel voor opgeslagen signalen (Caching)
    cursor.execute('''CREATE TABLE IF NOT EXISTS cached_signals 
                      (company TEXT, type TEXT, data TEXT, timestamp TIMESTAMP)''')
    # Tabel voor de slimme scheduler
    cursor.execute('''CREATE TABLE IF NOT EXISTS signal_scheduler 
                      (company TEXT, type TEXT, next_check TIMESTAMP, PRIMARY KEY(company, type))''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()

# --- Root endpoint voor Healthcheck ---
@app.get("/")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# --- Helper: Moeten we checken? ---
def should_check(company, sig_type):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT next_check FROM signal_scheduler WHERE company = ? AND type = ?", (company, sig_type))
        row = cursor.fetchone()
        conn.close()
        if not row: return True
        return datetime.now() >= datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S.%f')
    except:
        return True

# --- Helper: Haal Cache op ---
def get_cached_data(company, sig_type):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM cached_signals WHERE company = ? AND type = ? ORDER BY timestamp DESC LIMIT 1", (company, sig_type))
        row = cursor.fetchone()
        conn.close()
        return eval(row[0]) if row else None
    except:
        return None

# --- De Core Smart Engine ---
@app.get("/api/detect-signals/{company}")
async def get_smart_signals(company: str):
    if not SERPER_API_KEY: 
        raise HTTPException(status_code=500, detail="Serper Key Missing")
    
    final_report = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for sig_id, config in SIGNAL_CONFIG.items():
        if should_check(company, sig_id):
            payload = {"q": config["q"].format(company=company), "tbs": config["tbs"], "num": 4}
            try:
                resp = requests.post("https://google.serper.dev/search", 
                                     headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}, 
                                     json=payload, timeout=10)
                
                if resp.status_code == 200:
                    data = resp.json().get("organic", [])
                    cursor.execute("INSERT OR REPLACE INTO cached_signals (company, type, data, timestamp) VALUES (?, ?, ?, ?)",
                                   (company, sig_id, str(data), datetime.now()))
                    next_date = datetime.now() + timedelta(days=config["interval_days"])
                    cursor.execute("INSERT OR REPLACE INTO signal_scheduler (company, type, next_check) VALUES (?, ?, ?)",
                                   (company, sig_id, next_date))
                    current_data = data
                else:
                    current_data = get_cached_data(company, sig_id) or []
            except:
                current_data = get_cached_data(company, sig_id) or []
        else:
            current_data = get_cached_data(company, sig_id) or []

        if current_data:
            final_report.append({"signal_id": sig_id, "signal_label": sig_id.replace("_", " ").capitalize(), "found_items": current_data})

    conn.commit()
    conn.close()
    return {"company": company, "signals": final_report, "last_update": datetime.now()}

# --- Start configuratie voor Railway ---
if __name__ == "__main__":
    # Railway stelt automatisch een PORT omgevingsvariabele in
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
