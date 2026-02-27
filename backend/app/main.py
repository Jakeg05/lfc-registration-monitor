from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, stripe
from app.db.session import engine, Base

# Create tables on startup (simplification for dev)
import asyncio

app = FastAPI(title="LFC Monitor API")

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod strict restrict origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(stripe.router, prefix="/stripe", tags=["Payments"])

@app.get("/")
def read_root():
    return {"message": "LFC Monitor API is running"}
