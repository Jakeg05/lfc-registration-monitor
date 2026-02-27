import os
import stripe
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db, User

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/checkout-session")
async def create_checkout_session(payload: dict):
    user_email = payload.get("email")
    # In real app verify user identity via token/session
    
    try:
        session = stripe.checkout.Session.create(
            customer_email=user_email,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {'name': 'LFC Monitor Subscription'},
                    'unit_amount': 200, # £2.00
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:5173?success=true',
            cancel_url='http://localhost:5173?canceled=true',
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
