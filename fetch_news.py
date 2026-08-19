import os
import time
import requests
from dotenv import load_dotenv
from database import init_db, add_portfolio_columns, insert_article
from portfolio import PORTFOLIO

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news(company_name):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f'"{company_name}" India',
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def save_articles(ticker, company_name, data, portfolio_ticker, relationship):
    saved_count = 0
    skipped_count = 0
    for article in data["articles"]:
        success = insert_article(
            ticker=ticker,
            company_name=company_name,
            headline=article["title"],
            source=article["source"]["name"],
            url=article["url"],
            published_date=article["publishedAt"],
            portfolio_ticker=portfolio_ticker,
            relationship=relationship
        )
        if success:
            saved_count += 1
        else:
            skipped_count += 1
    return saved_count, skipped_count

def fetch_all_portfolio_news():
    init_db()
    add_portfolio_columns()

    for holding in PORTFOLIO:
        ticker = holding["ticker"]
        company_name = holding["company_name"]

        print(f"\nFetching direct news for {company_name} ({ticker})...")
        data = fetch_news(company_name)
        saved, skipped = save_articles(ticker, company_name, data, portfolio_ticker=ticker, relationship="direct")
        print(f"  Saved: {saved}, Skipped: {skipped}")
        time.sleep(1)

        for competitor in holding["competitors"]:
            comp_ticker = competitor["ticker"]
            comp_name = competitor["company_name"]
            print(f"Fetching competitor news for {comp_name} ({comp_ticker}), relevant to your {ticker} holding...")
            data = fetch_news(comp_name)
            saved, skipped = save_articles(comp_ticker, comp_name, data, portfolio_ticker=ticker, relationship="competitor")
            print(f"  Saved: {saved}, Skipped: {skipped}")
            time.sleep(1)

if __name__ == "__main__":
    fetch_all_portfolio_news()