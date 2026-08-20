from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from portfolio import PORTFOLIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "portfolio_news.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/api/portfolio")
def get_portfolio():
    return PORTFOLIO

@app.get("/api/digest")
def get_digest(ticker: str = None, category: str = None, relationship: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM articles WHERE relevance_score IS NOT NULL"
    params = []

    if ticker:
        query += " AND portfolio_ticker = ?"
        params.append(ticker)
    if category:
        query += " AND category = ?"
        params.append(category)
    if relationship:
        query += " AND relationship = ?"
        params.append(relationship)

    query += " ORDER BY relevance_score DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    results = [dict(row) for row in rows]
    for r in results:
        r["headline"] = fix_encoding(r["headline"])
        r["reasoning"] = fix_encoding(r["reasoning"])
    return results

def fix_encoding(text):
    if not text:
        return text
    try:
        return text.encode("cp1252").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return text