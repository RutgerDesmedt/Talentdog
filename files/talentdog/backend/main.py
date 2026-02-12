from fastapi import FastAPI
import sqlite3
import os

app = FastAPI(title="TalentDog API", version="2.0")

# Database path configureren
DB_PATH = os.getenv("DB_PATH", "/home/claude/talentdog/database/talentdog.db")

def init_database():
    # Zorg dat de directory bestaat
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS talent_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup_event():
    init_database()
    print("✅ TalentDog API is online!")

@app.get("/")
async def root():
    return {"status": "online", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
