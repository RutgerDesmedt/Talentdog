from fastapi import FastAPI

app = FastAPI(title="TalentDog API", version="2.0")

@app.get("/")
async def healthcheck():
    return {"status": "online", "version": "2.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
