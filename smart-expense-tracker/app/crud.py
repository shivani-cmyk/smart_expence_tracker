from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed, full_name=user.full_name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_transaction(db: Session, user_id: int, tx: schemas.TransactionCreate):
    if tx.date is None:
        tx_date = datetime.date.today()
    else:
        tx_date = tx.date
    db_tx = models.Transaction(
        user_id=user_id,
        date=tx_date,
        amount=tx.amount,
        merchant=tx.merchant,
        category=tx.category,
        note=tx.note
    )
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    return db_tx

def get_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Transaction).filter(models.Transaction.user_id == user_id).order_by(models.Transaction.date.desc()).offset(skip).limit(limit).all()

def get_transaction_stats(db: Session, user_id: int):
    # returns simple aggregated data
    rows = db.query(models.Transaction.category, models.Transaction.amount).filter(models.Transaction.user_id == user_id).all()
    return rows

def delete_transaction(db: Session, tx_id: int, user_id: int):
    tx = db.query(models.Transaction).filter(models.Transaction.id==tx_id, models.Transaction.user_id==user_id).first()
    if tx:
        db.delete(tx)
        db.commit()
        return True
    return False

