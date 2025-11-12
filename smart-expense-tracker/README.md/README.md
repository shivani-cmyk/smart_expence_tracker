# Smart Expense Tracker (minimal)

## Setup (local)
1. python -m venv .venv
2. source .venv/bin/activate  (Windows: .venv\Scripts\activate)
3. pip install -r requirements.txt
4. uvicorn app.main:app --reload

DB: SQLite file `expenses.db` created automatically.

## Endpoints
- POST /auth/register  (UserCreate JSON)
- POST /auth/token     (form-data: username, password) -> token
- POST /transactions/  (bearer token) create tx
- GET /transactions/   (bearer token) list tx
- POST /transactions/upload-csv (file upload)
- GET /transactions/dashboard (requires bearer token) -> HTML dashboard

## Notes
- This is a minimal reference implementation for learning and resume projects.
- Swap SQLite for Postgres and store SECRET_KEY in env for production.

