import sqlite3

DB_NAME = "portfolio_news.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            company_name TEXT,
            headline TEXT,
            source TEXT,
            url TEXT UNIQUE,
            published_date TEXT,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            company_name TEXT,
            current_price REAL,
            market_cap INTEGER,
            sector TEXT,
            fetched_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_article(ticker, company_name, headline, source, url, published_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO articles (ticker, company_name, headline, source, url, published_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ticker, company_name, headline, source, url, published_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # duplicate URL, skipped
    finally:
        conn.close()

def insert_market_data(ticker, company_name, current_price, market_cap, sector):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO market_data (ticker, company_name, current_price, market_cap, sector)
        VALUES (?, ?, ?, ?, ?)
    """, (ticker, company_name, current_price, market_cap, sector))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")