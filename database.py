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

def add_relevance_columns():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN relevance_score INTEGER")
    except sqlite3.OperationalError:
        pass  # column already exists
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN category TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE articles ADD COLUMN reasoning TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def get_unanalyzed_articles():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, ticker, company_name, headline, source
        FROM articles
        WHERE relevance_score IS NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def save_analysis(article_id, relevance_score, category, reasoning):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE articles
        SET relevance_score = ?, category = ?, reasoning = ?
        WHERE id = ?
    """, (relevance_score, category, reasoning, article_id))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")