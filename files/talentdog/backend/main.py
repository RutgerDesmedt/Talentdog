from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import os
import xml.etree.ElementTree as ET
import uvicorn
from typing import Optional
from datetime import datetime

app = FastAPI(title="TalentDog Enterprise ATS Integrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.getcwd(), "database", "talentdog.db")

# Pydantic Models
class ATSConfig(BaseModel):
    system: str  # greenhouse, lever, workday, jobtoolz, recruitee, etc.
    subdomain: str 
    api_key: Optional[str] = None
    feed_url: Optional[str] = None

class ATSConnectionRequest(BaseModel):
    provider: str
    subdomain: Optional[str] = None
    api_key: Optional[str] = None
    feed_url: Optional[str] = None

# Initialize database
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create ATS configurations table
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
    
    # Create vacancies table if not exists
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
    
    # Create talent_pool table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talent_pool (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT,
            current_company TEXT,
            location TEXT,
            sector TEXT,
            photo TEXT,
            points INTEGER DEFAULT 0,
            signal_type TEXT,
            signal_description TEXT,
            background TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create talent_matches table (many-to-many between vacancies and talent)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talent_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER NOT NULL,
            talent_id INTEGER NOT NULL,
            match_score INTEGER DEFAULT 0,
            signal_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (vacancy_id) REFERENCES vacancies(id),
            FOREIGN KEY (talent_id) REFERENCES talent_pool(id),
            UNIQUE(vacancy_id, talent_id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

class ATSManager:
    @staticmethod
    def fetch_jobs(config: ATSConfig):
        """
        Fetch jobs from various ATS providers
        Returns: List of job dictionaries with standardized fields
        """
        s = config.system.lower()
        jobs = []
        
        try:
            # 1. JOBTOOLZ (Belgische ATS)
            if s == "jobtoolz":
                url = f"https://api.jobtoolz.com/v1/public/jobs/{config.subdomain}"
                headers = {}
                if config.api_key:
                    headers['Authorization'] = f"Bearer {config.api_key}"
                
                res = requests.get(url, headers=headers, timeout=30).json()
                jobs = [{
                    "title": j.get('title', 'Untitled'),
                    "url": j.get('url', ''),
                    "id": str(j.get('id', '')),
                    "location": j.get('location', ''),
                    "department": j.get('department', ''),
                    "description": j.get('description', '')
                } for j in res.get('data', [])]

            # 2. RECRUITEE (Nederlandse ATS)
            elif s == "recruitee":
                # Recruitee API endpoint
                url = f"https://api.recruitee.com/c/{config.subdomain}/offers"
                headers = {
                    'Authorization': f"Bearer {config.api_key}"
                }
                
                res = requests.get(url, headers=headers, timeout=30).json()
                jobs = [{
                    "title": j.get('title', 'Untitled'),
                    "url": j.get('careers_url', ''),
                    "id": str(j.get('id', '')),
                    "location": j.get('location', ''),
                    "department": j.get('department', ''),
                    "description": j.get('description', '')
                } for j in res.get('offers', [])]

            # 3. GREENHOUSE
            elif s == "greenhouse":
                url = f"https://boards-api.greenhouse.io/v1/boards/{config.subdomain}/jobs"
                params = {'content': 'true'}  # Get full job content
                
                res = requests.get(url, params=params, timeout=30).json()
                jobs = [{
                    "title": j.get('title', 'Untitled'),
                    "url": j.get('absolute_url', ''),
                    "id": str(j.get('id', '')),
                    "location": j.get('location', {}).get('name', '') if isinstance(j.get('location'), dict) else '',
                    "department": j.get('departments', [{}])[0].get('name', '') if j.get('departments') else '',
                    "description": j.get('content', '')
                } for j in res.get('jobs', [])]

            # 4. LEVER
            elif s == "lever":
                url = f"https://api.lever.co/v0/postings/{config.subdomain}"
                params = {'mode': 'json'}
                
                res = requests.get(url, params=params, timeout=30).json()
                jobs = [{
                    "title": j.get('text', 'Untitled'),
                    "url": j.get('hostedUrl', ''),
                    "id": j.get('id', ''),
                    "location": j.get('categories', {}).get('location', ''),
                    "department": j.get('categories', {}).get('team', ''),
                    "description": j.get('description', '')
                } for j in res if isinstance(j, dict)]

            # 5. WORKDAY / iCIMS (XML/RSS Feeds)
            elif s in ["workday", "icims"]:
                target_url = config.feed_url or f"https://{config.subdomain}.{s}.com/wday/cxs/jobs"
                response = requests.get(target_url, timeout=30)
                root = ET.fromstring(response.content)
                
                # Try both RSS and Workday XML formats
                for item in root.findall('.//item') or root.findall('.//job'):
                    title_elem = item.find('title') or item.find('jobTitle')
                    link_elem = item.find('link') or item.find('jobUrl')
                    guid_elem = item.find('guid') or item.find('jobId')
                    loc_elem = item.find('location') or item.find('jobLocation')
                    dept_elem = item.find('department') or item.find('jobDepartment')
                    desc_elem = item.find('description') or item.find('jobDescription')
                    
                    jobs.append({
                        "title": title_elem.text if title_elem is not None else "Untitled",
                        "url": link_elem.text if link_elem is not None else "",
                        "id": guid_elem.text if guid_elem is not None else "",
                        "location": loc_elem.text if loc_elem is not None else "",
                        "department": dept_elem.text if dept_elem is not None else "",
                        "description": desc_elem.text if desc_elem is not None else ""
                    })

            # 6. SMARTRECRUITERS
            elif s == "smartrecruiters":
                url = f"https://api.smartrecruiters.com/v1/companies/{config.subdomain}/postings"
                params = {'limit': 100}
                
                res = requests.get(url, params=params, timeout=30).json()
                jobs = [{
                    "title": j.get('name', 'Untitled'),
                    "url": f"https://jobs.smartrecruiters.com/{config.subdomain}/{j.get('id', '')}",
                    "id": str(j.get('id', '')),
                    "location": j.get('location', {}).get('city', '') if isinstance(j.get('location'), dict) else '',
                    "department": j.get('department', {}).get('label', '') if isinstance(j.get('department'), dict) else '',
                    "description": ''
                } for j in res.get('content', [])]

            # 7. BAMBOOHR
            elif s == "bamboohr":
                # BambooHR careers page API
                url = f"https://{config.subdomain}.bamboohr.com/jobs/embed2.php"
                headers = {
                    'Accept': 'application/json'
                }
                if config.api_key:
                    headers['Authorization'] = f"Basic {config.api_key}"
                
                response = requests.get(url, headers=headers, timeout=30)
                # BambooHR returns HTML, would need scraping or their API key
                # For now, return empty if no proper API access
                jobs = []

        except Exception as e:
            print(f"Error fetching from {s}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch jobs from {s}: {str(e)}")

        return jobs

# API Endpoints

@app.post("/api/ats/connect")
async def connect_ats(request: ATSConnectionRequest):
    """
    Connect to an ATS provider and save configuration
    """
    try:
        # Validate required fields based on provider
        provider_lower = request.provider.lower()
        
        # Store configuration in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if provider already exists
        cursor.execute('SELECT id FROM ats_configurations WHERE provider = ?', (provider_lower,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing configuration
            cursor.execute('''
                UPDATE ats_configurations 
                SET subdomain = ?, api_key = ?, feed_url = ?, is_active = 1, last_sync = ?
                WHERE provider = ?
            ''', (request.subdomain, request.api_key, request.feed_url, datetime.now(), provider_lower))
        else:
            # Insert new configuration
            cursor.execute('''
                INSERT INTO ats_configurations (provider, subdomain, api_key, feed_url, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (provider_lower, request.subdomain, request.api_key, request.feed_url))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully connected to {request.provider}",
            "provider": request.provider
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ats/disconnect/{provider}")
async def disconnect_ats(provider: str):
    """
    Disconnect from an ATS provider
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE ats_configurations SET is_active = 0 WHERE provider = ?', (provider.lower(),))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Disconnected from {provider}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ats/status")
async def get_ats_status():
    """
    Get status of all ATS connections
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT provider, subdomain, is_active, last_sync 
            FROM ats_configurations
        ''')
        
        configs = cursor.fetchall()
        conn.close()
        
        return [{
            "provider": c[0],
            "subdomain": c[1],
            "is_active": bool(c[2]),
            "last_sync": c[3]
        } for c in configs]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vacancies/sync-ats")
async def sync_ats(config: ATSConfig):
    """
    Sync vacancies from a specific ATS provider
    Can be called manually or automatically
    """
    try:
        jobs = ATSManager.fetch_jobs(config)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        new_count = 0
        updated_count = 0

        for job in jobs:
            # Check if vacancy already exists by external_id or URL
            cursor.execute(
                'SELECT id FROM vacancies WHERE external_id = ? OR url = ?', 
                (job['id'], job['url'])
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing vacancy
                cursor.execute('''
                    UPDATE vacancies 
                    SET title = ?, location = ?, department = ?, 
                        description = ?, updated_at = ?, source_provider = ?
                    WHERE id = ?
                ''', (
                    job['title'], 
                    job.get('location', ''), 
                    job.get('department', ''),
                    job.get('description', ''),
                    datetime.now(),
                    config.system,
                    existing[0]
                ))
                updated_count += 1
            else:
                # Insert new vacancy
                cursor.execute('''
                    INSERT INTO vacancies 
                    (title, company, location, department, description, status, url, external_id, source_provider) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job['title'], 
                    config.subdomain, 
                    job.get('location', ''),
                    job.get('department', ''),
                    job.get('description', ''),
                    "Open", 
                    job['url'], 
                    job['id'],
                    config.system
                ))
                new_count += 1
        
        # Update last sync time for this provider
        cursor.execute('''
            UPDATE ats_configurations 
            SET last_sync = ? 
            WHERE provider = ?
        ''', (datetime.now(), config.system.lower()))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "total": len(jobs), 
            "new": new_count,
            "updated": updated_count,
            "provider": config.system
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vacancies/sync-all")
async def sync_all_ats():
    """
    Sync vacancies from all connected ATS providers
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all active ATS configurations
        cursor.execute('''
            SELECT provider, subdomain, api_key, feed_url 
            FROM ats_configurations 
            WHERE is_active = 1
        ''')
        
        configs = cursor.fetchall()
        conn.close()
        
        results = []
        total_new = 0
        total_updated = 0
        
        for config_row in configs:
            config = ATSConfig(
                system=config_row[0],
                subdomain=config_row[1] or "",
                api_key=config_row[2],
                feed_url=config_row[3]
            )
            
            try:
                result = await sync_ats(config)
                results.append({
                    "provider": config.system,
                    "success": True,
                    "new": result["new"],
                    "updated": result["updated"]
                })
                total_new += result["new"]
                total_updated += result["updated"]
            except Exception as e:
                results.append({
                    "provider": config.system,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results,
            "total_new": total_new,
            "total_updated": total_updated
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vacancies")
async def get_vacancies(limit: int = 100, status: str = None):
    """
    Get all vacancies from database with matching talent count
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = '''SELECT id, title, company, location, department, status, url, source_provider, 
                   created_at, description FROM vacancies'''
        params = []
        
        if status:
            query += ' WHERE status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        vacancies = []
        for row in cursor.fetchall():
            # Get matching talent count for this vacancy
            cursor.execute('SELECT COUNT(*) FROM talent_matches WHERE vacancy_id = ?', (row[0],))
            match_count = cursor.fetchone()[0]
            
            vacancies.append({
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3] or 'Remote',
                "department": row[4] or 'General',
                "status": row[5],
                "url": row[6],
                "source": row[7],
                "posted": row[8],
                "description": row[9],
                "matchCount": match_count
            })
        
        conn.close()
        
        return vacancies
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vacancies/{vacancy_id}/matches")
async def get_vacancy_matches(vacancy_id: int, limit: int = 20):
    """
    Get matching talent for a specific vacancy
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get matches from talent_matches table
        cursor.execute('''
            SELECT tm.talent_id, tm.match_score, tm.signal_type, tp.name, tp.role, 
                   tp.current_company, tp.location, tp.photo, tp.email, tp.points
            FROM talent_matches tm
            JOIN talent_pool tp ON tm.talent_id = tp.id
            WHERE tm.vacancy_id = ?
            ORDER BY tm.match_score DESC
            LIMIT ?
        ''', (vacancy_id, limit))
        
        matches = [{
            "id": row[0],
            "matchScore": row[1],
            "signalType": row[2],
            "name": row[3],
            "role": row[4],
            "currentCompany": row[5],
            "location": row[6],
            "photo": row[7] or f"https://ui-avatars.com/api/?name={row[3]}&background=random",
            "email": row[8],
            "points": row[9] or row[1]
        } for row in cursor.fetchall()]
        
        conn.close()
        
        return matches
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/vacancies/{vacancy_id}")
async def delete_vacancy(vacancy_id: int):
    """
    Delete a vacancy
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM vacancies WHERE id = ?', (vacancy_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Vacancy deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Keep existing talent pool endpoints
@app.get("/api/talent-pool")
async def get_talent_pool(limit: int = 100):
    """
    Get talent pool data from database
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, email, role, current_company, location, sector, 
                   photo, points, signal_type, signal_description, background
            FROM talent_pool
            ORDER BY points DESC
            LIMIT ?
        ''', (limit,))
        
        talent = [{
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "currentCompany": row[4],
            "location": row[5],
            "sector": row[6],
            "photo": row[7] or f"https://ui-avatars.com/api/?name={row[1]}&background=random",
            "points": row[8],
            "signalType": row[9],
            "signalDescription": row[10],
            "background": row[11]
        } for row in cursor.fetchall()]
        
        conn.close()
        
        return talent
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "TalentDog ATS API is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
