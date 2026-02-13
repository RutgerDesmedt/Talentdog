from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import os
import xml.etree.ElementTree as ET
import uvicorn

app = FastAPI(title="TalentDog Enterprise ATS Integrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.getcwd(), "database", "talentdog.db")

class ATSConfig(BaseModel):
    system: str  # greenhouse, lever, workday, jobtoolz, etc.
    subdomain: str 
    api_key: str = None
    feed_url: str = None # Specifiek voor Workday/iCIMS XML feeds

class ATSManager:
    @staticmethod
    def fetch_jobs(config: ATSConfig):
        s = config.system.lower()
        
        # 1. JOBTOOLZ (Belgische focus)
        if s == "jobtoolz":
            url = f"https://api.jobtoolz.com/v1/public/jobs/{config.subdomain}"
            res = requests.get(url).json()
            # Jobtoolz mapping
            return [{"title": j['title'], "url": j['url'], "id": j['id']} for j in res.get('data', [])]

        # 2. GREENHOUSE
        elif s == "greenhouse":
            url = f"https://boards-api.greenhouse.io/v1/boards/{config.subdomain}/jobs"
            res = requests.get(url).json()
            return [{"title": j['title'], "url": j['absolute_url'], "id": j['id']} for j in res.get('jobs', [])]

        # 3. LEVER
        elif s == "lever":
            url = f"https://api.lever.co/v0/postings/{config.subdomain}"
            res = requests.get(url).json()
            return [{"title": j['text'], "url": j['hostedUrl'], "id": j['id']} for j in res]

        # 4. WORKDAY / iCIMS (XML Parsing)
        elif s in ["workday", "icims"]:
            target_url = config.feed_url or f"https://{config.subdomain}.{s}.com/rss"
            response = requests.get(target_url)
            root = ET.fromstring(response.content)
            jobs = []
            # Zoek naar standaard RSS/XML items
            for item in root.findall('.//item'):
                jobs.append({
                    "title": item.find('title').text,
                    "url": item.find('link').text,
                    "id": item.find('guid').text if item.find('guid') is not None else item.find('link').text
                })
            return jobs

        # 5. SMARTRECRUITERS
        elif s == "smartrecruiters":
            url = f"https://api.smartrecruiters.com/v1/companies/{config.subdomain}/postings"
            res = requests.get(url).json()
            return [{"title": j['name'], "url": f"https://jobs.smartrecruiters.com/{config.subdomain}/{j['id']}", "id": j['id']} for j in res.get('content', [])]

        return []

@app.post("/api/vacancies/sync-ats")
async def sync_ats(config: ATSConfig):
    try:
        jobs = ATSManager.fetch_jobs(config)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        new_count = 0

        for job in jobs:
            cursor.execute('SELECT id FROM vacancies WHERE url = ?', (job['url'],))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO vacancies (title, company, status, url) VALUES (?, ?, ?, ?)', 
                              (job['title'], config.subdomain, "Open", job['url']))
                new_count += 1
        
        conn.commit()
        conn.close()
        return {"success": True, "total": len(jobs), "new": new_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Behoud hier je bestaande GET /api/vacancies en DELETE /api/vacancies endpoints...
