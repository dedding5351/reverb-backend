from fastapi import FastAPI
from app.routers import posts, companies

app = FastAPI(title="Reverb")

app.include_router(posts.router)
app.include_router(companies.router)

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
