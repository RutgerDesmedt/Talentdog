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

# --- 2. APP INITIALISATIE ---
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
    """Controleert of de tekst een echte functietitel is."""
    title_clean = " ".join(title.lower().split())
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
    noise = [r'bekijk vacature', r'solliciteer direct', r'view job', r'lees meer']
    clean = title
    for word in noise:
        clean = re.sub(word, '', clean, flags=re.IGNORECASE)
    return " ".join(clean.split()).strip()

def extract_requirements(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text(" ", strip=True).lower()
    skills = ['python', 'react', 'javascript', 'aws', 'azure', 'php', 'java', 'management', 'sales', 'hbo', 'wo', 'nederlands', 'engels']
    found = [s for s in skills if re.search(rf'\b{s}\b', text)]
    return ", ".join(found)

def calculate_match_score(vacancy_title, vacancy_reqs, talent):
    score = 0
    t_data = (talent['role'] + " " + talent['background']).lower()
    if vacancy_title.lower() in talent['role'].lower():
        score += 50
    for req in vacancy_reqs.lower().split(", "):
        if req.strip()
