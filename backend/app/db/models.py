from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    subscription_status = Column(String, default="inactive") # active, inactive
    stripe_customer_id = Column(String, nullable=True)
    # Store token securely in prod! Ideally separate table or encrypted
    google_refresh_token = Column(String, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    event_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
