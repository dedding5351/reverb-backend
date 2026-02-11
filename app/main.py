from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import posts, companies, auth, personalization, recommendations
from app.database import engine, Base
from sqlalchemy import text
from contextlib import asynccontextmanager
from app.services.scheduler import SchedulerService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB tables exist
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    
    # Start Scheduler
    scheduler = SchedulerService()
    scheduler.start()
    
    # Trigger immediate run for testing (fire and forget)
    import asyncio
    asyncio.create_task(scheduler.run_daily_ingestion())
    
    yield
    # Shutdown

app = FastAPI(title="Reverb", lifespan=lifespan)

from app.config import settings

# Configure CORS
origins = settings.CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers (x-user-id, etc.)
)

app.include_router(posts.router)
app.include_router(companies.router)
app.include_router(auth.router)
app.include_router(personalization.router)
app.include_router(recommendations.router)

@app.get("/")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
