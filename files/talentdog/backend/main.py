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

app = FastAPI(title="TalentDog Intelligence v2.6")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_DIR = os.path.join(os.getcwd(), "database")
DB_PATH = os.path.join(DB_DIR, "talentdog.db")

# --- DATABASE INITIALISATIE ---
def init_database():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS vacancies 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      title TEXT, company TEXT, location TEXT, 
                      requirements TEXT, status TEXT, url TEXT, 
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()

# --- INTELLIGENTE FILTERS ---
def is_genuine_job_title(title):
    """Controleert of de tekst echt een functie is en geen menu-item of knop."""
    title_clean = title.lower()
    
    # Woorden die MOETEN voorkomen voor een positieve match
    job_markers = [
        'engineer', 'developer', 'manager', 'consultant', 'medewerker', 
        'specialist', 'analyst', 'lead', 'architect', 'expert', 'adviseur',
        'monteur', 'operator', 'verpleegkundige', 'steward', 'designer',
        'beheerder', 'coördinator', 'sales', 'account', 'technieker', 'it', 'ict'
    ]
    
    # Woorden die we NOOIT als titel willen (de 'Klik hier' ruis)
    blacklist = [
        'klik hier', 'solliciteer', 'spontaan', 'onze vacatures', 
        'over ons', 'privacy', 'cookie', 'lees meer', 'nieuws', 'blog',
        'bekijk', 'ga naar', 'login', 'register'
    ]
    
    if any(word in title_clean for word in blacklist):
        return False
        
    # Moet een marker bevatten EN een redelijke lengte hebben
    return any(marker in title_clean for marker in job_markers) and len(title) > 5

def clean_job_title(title):
    """Schoont de titel op van resterende ruis."""
    noise = [r'bekijk vacature', r'solliciteer direct', r'view job', r'lees meer']
    clean = title
    for word in noise:
        clean = re.sub(word, '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'^[ \t\n\r\f\v\W]+|[ \t\n\r\f\v\W]+$', '', clean)
    return " ".join(clean.split())

def extract_requirements(html_content):
    """Scant de pagina op technische keywords."""
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(" ", strip=True).lower()
    skill_library = ['python', 'react', 'javascript', 'aws', 'azure', 'php', 'java', 'management', 'sales', 'hbo', 'wo', 'nederlands', 'engels']
    found = [skill for skill in skill_library if re.search(rf'\b{skill}\b', text)]
    return ", ".join(found)

def calculate_match_score(vacancy_title, vacancy_reqs, talent):
    """Matching logica tussen vacature en talent pool."""
    score = 0
    talent_data = (talent['role'] + " " + talent['background']).lower()
    if vacancy_title.lower() in talent['role'].lower():
        score += 50
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
async def get_talent_pool(limit: int = 100):
    talents = [
        {"id": 1, "name": "Emma de Vries", "role": "Senior Python Developer", "background": "Ervaren met AWS en Python", "signalType": "TENURE EXPIRY"},
        {"id": 2, "name": "Lucas Bakker", "role": "Project Manager IT", "background": "HBO werk- en denkniveau, Agile ervaring", "signalType": "LAYOFFS"},
        {"id": 3, "name": "Sophie Jansen", "role": "Frontend Developer", "background": "Expert in React en Javascript", "signalType": None}
    ]
    return talents[:limit]

@app.post("/api/vacancies/sync")
async def sync_vacancies(data: VacancySync):
    """Scraper met strenge functie-validatie."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(data.url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found_count = 0
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Zoek tekst in de link, of in een koptekst (h1-h4) binnen de link
            inner_header = link.find(['h1', 'h2', 'h3', 'h4'])
            raw_text = inner_header.get_text().strip() if inner_header else link.get_text().strip()
            
            # STRENG FILTER: Alleen als het op een echte baan lijkt
            if is_genuine_job_title(raw_text) and any(k in href.lower() for k in ['job', 'vacature', 'vacancy', '/p/']):
                full_url = urllib.parse.urljoin(data.url, href)
                
                # Check op PDF
                if full_url.lower().endswith('.pdf'): continue

                clean_title = clean_job_title(raw_text)
                
                # Deep scan voor requirements
                try:
                    detail_res = requests.get(full_url, headers=headers, timeout=5)
                    reqs = extract_requirements(detail_res.text)
                except:
                    reqs = ""

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM vacancies WHERE url = ?', (full_url,))
                if not cursor.fetchone():
                    cursor.execute('''INSERT INTO vacancies (title, company, requirements, status, url) 
                                     VALUES (?, ?, ?, ?, ?)''', 
                                  (clean_title, "Gedetecteerd Bedrijf", reqs, "Open", full_url))
                    found_count += 1
                conn.commit()
                conn.close()
        
        return {"success": True, "new_vacancies": found_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vacancies")
async def get_vacancies():
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
        vac['matches'] = sorted(scored_talents, key=lambda x: x['match_score'], reverse=True)
    
    return vacancies

@app.delete("/api/vacancies/{vacancy_id}")
async def delete_vacancy(vacancy_id: int):
    """Verwijder een vacature (Vuilbak functie)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vacancies WHERE id = ?', (vacancy_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Verwijderd"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
