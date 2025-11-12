from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Request, Form
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud, database, utils
from .auth import get_current_user, get_db
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/", response_model=schemas.TransactionOut)
def create_transaction(tx: schemas.TransactionCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    # If category not provided, categorize
    if not tx.category:
        tx.category = utils.categorize_merchant(tx.merchant)
    created = crud.create_transaction(db, current_user.id, tx)
    return created

@router.get("/", response_model=schemas.TransactionsList)
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    txs = crud.get_transactions(db, current_user.id, skip, limit)
    return {"transactions": txs}

@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    contents = await file.read()
    df = utils.parse_csv_bytes(contents)
    created = []
    for _, row in df.iterrows():
        tx = schemas.TransactionCreate(
            date=row['date'],
            amount=float(row['amount']),
            merchant=row['merchant'],
            category=row['category'],
            note=row.get('note', None)
        )
        created_tx = crud.create_transaction(db, current_user.id, tx)
        created.append(created_tx)
    return {"created": len(created)}

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    txs = crud.get_transactions(db, current_user.id, 0, 1000)
    summary = utils.summary_from_transactions(txs)
    # Build simple Plotly chart data (we'll embed JSON into template)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "by_category": summary['by_category'],
        "monthly": summary['monthly']
    })

@router.delete("/{tx_id}")
def delete_tx(tx_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    ok = crud.delete_transaction(db, tx_id, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"detail": "deleted"}
