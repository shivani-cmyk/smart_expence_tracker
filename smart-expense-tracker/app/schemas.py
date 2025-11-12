from pydantic import BaseModel, EmailStr
from typing import Optional, List
import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TransactionCreate(BaseModel):
    date: Optional[datetime.date] = None
    amount: float
    merchant: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None

class TransactionOut(BaseModel):
    id: int
    date: datetime.date
    amount: float
    merchant: Optional[str]
    category: Optional[str]
    note: Optional[str]
    class Config:
        orm_mode = True

class TransactionsList(BaseModel):
    transactions: List[TransactionOut]
