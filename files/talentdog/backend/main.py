from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import requests
import re
import urllib.parse
from bs4 import BeautifulSoup
from datetime import datetime
import uvicorn

# --- CONFIGURATIE & MODELLEN ---
class VacancySync(BaseModel):
    url: str
    title: str = "Nieuwe URL Sync"

app = FastAPI(title="TalentDog Intelligence v2.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_DIR = os.path.join(os.getcwd(), "database")
DB_PATH = os.path.join(DB_DIR, "talentdog.db")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# --- DATABASE INITIALISATIE ---
def init_database():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS vacancies (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, company TEXT, location TEXT, requirements TEXT, status TEXT, url TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()

# --- HELPER FUNCTIES VOOR SCHONERE DATA ---
def clean_job_title(title):
    """Maakt de titels schoon (bijv. verwijdert 'Bekijk vacature')"""
    noise = [r'bekijk vacature', r'solliciteer direct', r'view job', r'lees meer', r'details', r'apply now']
    clean_title = title
    for word in noise:
        clean_title = re.sub(word, '', clean_title, flags=re.IGNORECASE)
    clean_title = re.sub(r'^[ \t\n\r\f\v\W]+|[ \t\n\r\f\v\W]+$', '', clean_title)
    return " ".join(clean_title.split())

def extract_requirements(html_content):
    """Scant de tekst op keywords voor matching"""
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(" ", strip=True).lower()
    skill_library = ['python', 'react', 'javascript', 'aws', 'azure', 'php', 'java', 'management', 'sales', 'hbo', 'wo', 'nederlands', 'engels']
    found = [skill for skill in skill_library if re.search(rf'\b{skill}\b', text)]
    return ", ".join(found)

def calculate_match_score(vacancy_title, vacancy_reqs, talent):
    """Berekent hoe goed een talent past bij een vacature"""
    score = 0
    talent_data = (talent['role'] + " " + talent['background']).lower()
    
    # Match op titel (zwaar gewogen)
    if vacancy_title.lower() in talent['role'].lower():
        score += 50
    
    # Match op skills/requirements
    req_list = vacancy_reqs.lower().split(", ")
    for req in req_list:
        if req and req in talent_data:
            score += 20
            
    return score

# --- API ENDPOINTS ---

@app.get("/")
async def root():
    return {"status": "TalentDog Engine Online", "port": os.environ.get("PORT", "8080")}

@app.get("/api/talent-pool")
async def get_talent_pool(limit: int = 20):
    """Mock talent pool data (in een echte app komt dit uit je DB)"""
    talents = [
        {"id": 1, "name": "Emma de Vries", "role": "Senior Python Developer", "background": "Ervaren met AWS en Python", "signalType": "TENURE EXPIRY"},
        {"id": 2, "name": "Lucas Bakker", "role": "Project Manager", "background": "HBO werk- en denkniveau, Agile ervaring", "signalType": "LAYOFFS"},
        {"id": 3, "name": "Sophie Jansen", "role": "Frontend Developer", "background": "Expert in React en Javascript", "signalType": None}
    ]
    return talents[:limit]

@app.post("/api/vacancies/sync")
async def sync_vacancies(data: VacancySync):
    """Bezoekt de URL, vindt vacatures en slaat ze op met requirements"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(data.url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found_count = 0
        for link in soup.find_all('a', href=True):
            href = link['href']
            raw_text = link.get_text().strip()
            
            # Filter op links die op vacatures lijken
            if len(raw_text) > 8 and any(k in href.lower() for k in ['job', 'vacature', 'vacancy', '/p/']):
                full_url = urllib.parse.urljoin(data.url, href)
                clean_title = clean_job_title(raw_text)
                
                # Deep scan voor requirements
                try:
                    detail_res = requests.get(full_url, headers=headers, timeout=5)
                    reqs = extract_requirements(detail_res.text)
                except:
                    reqs = ""

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                # Voorkom dubbele urls
                cursor.execute('SELECT id FROM vacancies WHERE url = ?', (full_url,))
                if not cursor.fetchone():
                    cursor.execute('''INSERT INTO vacancies (title, company, requirements, status, url) 
                                     VALUES (?, ?, ?, ?, ?)''', 
                                  (clean_title, "Gedestilleerd Bedrijf", reqs, "Open", full_url))
                    found_count += 1
                conn.commit()
                conn.close()
        
        return {"success": True, "new_vacancies": found_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vacancies")
async def get_vacancies():
    """Haalt vacatures op inclusief de gerankte matches per vacature"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM vacancies ORDER BY created_at DESC')
    rows = cursor.fetchall()
    vacancies = [dict(r) for r in rows]
    conn.close()

    talent_pool = await get_talent_pool()
    
    for vac in vacancies:
        scored_talents = []
        for t in talent_pool:
            score = calculate_match_score(vac['title'], vac['requirements'] or "", t)
            if score > 0:
                t_copy = t.copy()
                t_copy['match_score'] = score
                scored_talents.append(t_copy)
        
        # Sorteer matches: Hoogste score bovenaan
        vac['matches'] = sorted(scored_talents, key=lambda x: x['match_score'], reverse=True)
    
    return vacancies

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
