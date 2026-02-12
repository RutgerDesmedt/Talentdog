from fastapi import FastAPI

app = FastAPI(title="TalentDog API", version="2.0")

@app.get("/")
async def healthcheck():
    """Healthcheck voor Railway"""
    return {"status": "ok"}

# --- Voeg hier je bestaande FastAPI endpoints toe ---
# Kopieer alle andere functies zoals get_talent_pool, add_talent, etc.
# Let op: houd alles in dezelfde app, maar zorg dat "/" route bovenaan staat

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, ho
