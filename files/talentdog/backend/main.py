from fastapi import FastAPI
import sqlite3

app = FastAPI(title="TalentDog API", version="2.0")

# Database setup
def init_database():
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
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

# Healthcheck endpoint
@app.get("/")
async def root():
    return {"status": "online", "version": "2.0"}

# Start server (voor lokale testen)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
