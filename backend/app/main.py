from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, stripe
from app.db.session import engine, Base
from app.services.worker import check_lfc_site
import logging

# Create tables on startup (simplification for dev)
import asyncio

app = FastAPI(title="LFC Monitor API")

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://vigilant-halibut-pw9xxprxg46399w4-5173.app.github.dev", "http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

async def run_worker_loop():
    while True:
        try:
            logger.info("Starting scheduled scrape job...")
            await check_lfc_site()
            logger.info("Scrape job finished. Sleeping for 1 hour.")
        except Exception as e:
            logger.error(f"Worker crashed: {e}")
        
        await asyncio.sleep(3600) # Run every hour

@app.on_event("startup")
async def startup():
    # Database Init
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start Worker
    asyncio.create_task(run_worker_loop())

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(stripe.router, prefix="/stripe", tags=["Payments"])

@app.get("/")
def read_root():
    return {"message": "LFC Monitor API is running"}
