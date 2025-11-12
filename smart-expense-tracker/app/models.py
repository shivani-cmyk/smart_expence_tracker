from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="user", cascade="all,delete-orphan")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date = Column(Date, default=datetime.date.today, index=True)
    amount = Column(Float, nullable=False)
    merchant = Column(String, nullable=True)
    category = Column(String, nullable=True, index=True)
    note = Column(Text, nullable=True)

    user = relationship("User", back_populates="transactions")

