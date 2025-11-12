from typing import Optional
import pandas as pd
from io import StringIO, BytesIO
import datetime

# Simple rule-based categorizer
CATEGORIZATION_RULES = {
    "Grocery": ["supermarket","mart","grocery","wholefoods","aldi","zomato"],
    "Transport": ["uber","ola","taxi","metro","bus","rail","flight"],
    "Dining": ["restaurant","cafe","starbucks","dominos","mcdonald"],
    "Rent": ["rent","landlord"],
    "Utilities": ["electricity","water","internet","phone","bill"],
    "Shopping": ["amazon","flipkart","myntra","mall","store"]
}

def categorize_merchant(merchant: Optional[str]) -> str:
    if not merchant:
        return "Uncategorized"
    text = merchant.lower()
    for cat, keywords in CATEGORIZATION_RULES.items():
        for k in keywords:
            if k in text:
                return cat
    return "Uncategorized"

def parse_csv_bytes(csv_bytes: bytes):
    # Accepts uploaded CSV (bytes) and returns DataFrame with standardized columns:
    # expected columns: date, amount, merchant, category, note (category optional)
    s = csv_bytes.decode('utf-8', errors='ignore')
    df = pd.read_csv(StringIO(s))
    # Normalize column names
    lower_cols = {c: c.strip().lower() for c in df.columns}
    df.rename(columns=lower_cols, inplace=True)
    # Try to map common names
    mapping = {}
    if 'amount' in df.columns:
        mapping['amount'] = 'amount'
    else:
        for col in df.columns:
            if 'amt' in col:
                mapping[col] = 'amount'
    if 'date' not in df.columns:
        # try some options or create today's date
        df['date'] = datetime.date.today()
    else:
        df['date'] = pd.to_datetime(df['date']).dt.date
    if 'merchant' not in df.columns:
        # try description
        if 'description' in df.columns:
            df.rename(columns={'description':'merchant'}, inplace=True)
        else:
            df['merchant'] = None
    # category optional - fill via merchant
    if 'category' not in df.columns:
        df['category'] = df['merchant'].apply(categorize_merchant)
    else:
        df['category'] = df['category'].fillna(df['merchant'].apply(categorize_merchant))

    # Ensure amount numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0.0)
    df['note'] = df.get('note', None)
    # Keep only expected columns
    df = df[['date','amount','merchant','category','note']]
    return df

def summary_from_transactions(transactions):
    # transactions: list of ORM objects or dict-like
    import pandas as pd
    rows = []
    for t in transactions:
        rows.append({
            "date": t.date,
            "amount": t.amount,
            "merchant": t.merchant or "",
            "category": t.category or "Uncategorized"
        })
    if not rows:
        return {"by_category": {}, "monthly": {}}
    df = pd.DataFrame(rows)
    df['month'] = pd.to_datetime(df['date']).dt.to_period('M').astype(str)
    by_cat = df.groupby('category').amount.sum().to_dict()
    monthly = df.groupby('month').amount.sum().to_dict()
    return {"by_category": by_cat, "monthly": monthly}
