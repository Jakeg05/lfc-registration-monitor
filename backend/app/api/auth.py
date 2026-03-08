import os
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User
from app.core.config import settings
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
SCOPES = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/calendar.events"]

# In prod this should match your registered redirect URI exactly
REDIRECT_URI = settings.REDIRECT_URI

@router.get("/login")
def login():
    flow = Flow.from_client_config({
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    url, _ = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return {"url": url}

@router.post("/callback")
async def callback(payload: dict, db: AsyncSession = Depends(get_db)):
    code = payload.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    
    try:
        flow = Flow.from_client_config({
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }, scopes=SCOPES)
        flow.redirect_uri = REDIRECT_URI
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        id_info = id_token.verify_oauth2_token(credentials.id_token, requests.Request(), GOOGLE_CLIENT_ID)
        email = id_info.get("email")
        
        # Upsert User
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user:
            user = User(email=email, google_refresh_token=credentials.refresh_token)
            db.add(user)
        elif credentials.refresh_token:
            user.google_refresh_token = credentials.refresh_token
            
        await db.commit()
        await db.refresh(user)
        
        return {"user": user.email, "status": user.subscription_status, "id": user.id}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
