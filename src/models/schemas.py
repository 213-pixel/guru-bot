from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserSchema(BaseModel):
    """Model untuk user Telegram"""
    user_id: int
    username: Optional[str] = None
    first_name: str
    last_name: Optional[str] = None
    registered_at: datetime = datetime.now()

class ChatHistorySchema(BaseModel):
    """Model untuk history chat"""
    user_id: int
    question: str
    answer: str
    timestamp: datetime = datetime.now()

class FAQSchema(BaseModel):
    """Model untuk FAQ"""
    question: str
    answer: str
    category: str = "general"
    updated_at: datetime = datetime.now()

class MessageResponse(BaseModel):
    """Response untuk API"""
    status: str
    message: str
    data: Optional[dict] = None