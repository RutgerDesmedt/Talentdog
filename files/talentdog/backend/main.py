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

# --- 1. CONFIGURATIE & MODELLEN ---
class VacancySync(BaseModel):
    url: str
    title: str = "Nieuwe URL Sync"

# --- 2. APP INITIALISATIE (Moet voor de routes!) ---
app = FastAPI(title="TalentDog Intelligence v2.6")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_DIR = os.path.join(os.getcwd(), "database")
DB_PATH = os.path.join(DB_DIR, "talentdog.db")

# --- 3. DATABASE SETUP ---
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

# --- 4. HULPFUNCTIES & FILTERS ---
def is_genuine_job_title(title):
    """Controleert of de tekst een echte functie is."""
    title_clean = " ".join(title.lower().split())
    
    # De lijst met markers die je specifiek vroeg voor Conxion
    job_markers = [
        'engineer', 'developer', 'manager', 'consultant', 'advisor', 
        'specialist', 'partner', 'ciso', 'lead', 'sales', 'account', 
        'support', 'project', 'central', 'cloud', 'data', 'software', 'architect'
    ]
    
    blacklist = ['klik hier', 'solliciteer', 'spontaan', 'lees meer', 'cookies', 'privacy', 'onze vacatures']

    if any(word in title_clean for word in blacklist):
        return False
    
    has_marker = any(marker in title_clean for marker in job_markers)
    is_correct_length = 5 < len(title_clean) < 100
    
    return has_marker and is_correct_length

def clean_job_title(title):
    """Verwijdert UI-rommel van de titel."""
    noise = [r'bekijk vacature', r'solliciteer direct', r'view job', r'lees meer']
    clean = title
    for word in noise:
        clean = re.sub(word, '', clean, flags=re.IGNORECASE)
    return " ".join(clean.split()).strip()

def extract_requirements(html_content):
    """Haalt technische skills uit de detailpagina."""
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(" ", strip=True).lower()
    skills = ['python', 'react', 'javascript', 'aws', 'azure', 'php', 'java', 'management', 'sales', 'hbo', 'wo', 'nederlands', 'engels']
    found = [s for s in skills if re.search(rf'\b{s}\b', text)]
    return ", ".join(found)

def calculate_match_score(vacancy_title, vacancy_reqs, talent):
    """Berekent de match tussen vacature en talent."""
    score = 0
    t_data = (talent['role'] + " " + talent['background']).lower()
    if vacancy_title.lower() in talent['role'].lower():
        score += 50
    for req in vacancy_reqs.lower().split(", "):
        if req.strip() and req.strip() in t_data:
            score += 20
    return score

# --- 5. API ROUTES ---

@app.get("/")
async def root():
    return {"status": "TalentDog Engine Online", "db": "Connected"}

@app.get("/api/talent-pool")
async def get_talent_pool(limit: int = 100):
    talents = [
        {"id": 1, "name": "Emma de Vries", "role": "Senior Python Developer", "background": "AWS en Python", "signalType": "TENURE EXPIRY"},
        {"id": 2, "name": "Lucas Bakker", "role": "Project Manager IT", "background": "HBO, Agile ervaring", "signalType": "LAYOFFS"},
        {"id": 3, "name": "Sophie Jansen", "role": "Frontend Developer", "background": "React en Javascript", "signalType": None}
    ]
    return talents[:limit]

@app.post("/api/vacancies/sync")
async def sync_vacancies(data: VacancySync):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(data.url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found_count = 0
        processed_urls = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            raw_text = link.get_text(" ", strip=True)
            
            if is_genuine_job_title(raw_text):
                full_url = urllib.parse.urljoin(data.url, href)
                if full_url in processed_urls:
                    continue
                
                processed_urls.add(full_url)
                clean_title = clean_job_title(raw_text)
                
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
                                  (clean_title, "Gedetecteerd", reqs, "Open", full_url))
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
    vacancies = [dict(r) for r in cursor.fetchall()]
    conn.close()

    talent_pool = await get_talent_pool()
    for vac in vacancies:
        scored = []
        for t in talent_pool:
            score = calculate_match_score(vac['title'], vac['requirements'] or "", t)
            if score > 0:
                t_copy = t.copy()
                t_copy['match_score'] = score
                scored.append(t_copy)
        vac['matches'] = sorted(scored, key=lambda x: x['match_score'], reverse=True)
    
    return vacancies

@app.delete("/api/vacancies/{vacancy_id}")
async def delete_vacancy(vacancy_id: int):
    """De gevraagde vuilbak-functie"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM vacancies WHERE id = ?', (vacancy_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Vacature verwijderd"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- 6. RUN ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
