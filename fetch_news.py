import os
import requests
from dotenv import load_dotenv
from database import init_db, insert_article

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news(ticker, company_name):
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

def save_articles(ticker, company_name, data):
    saved_count = 0
    skipped_count = 0
    for article in data["articles"]:
        success = insert_article(
            ticker=ticker,
            company_name=company_name,
            headline=article["title"],
            source=article["source"]["name"],
            url=article["url"],
            published_date=article["publishedAt"]
        )
        if success:
            saved_count += 1
        else:
            skipped_count += 1
    return saved_count, skipped_count

if __name__ == "__main__":
    init_db()
    ticker = "RELIANCE.NS"
    company_name = "Reliance Industries"

    data = fetch_news(ticker, company_name)
    print(f"Total results from API: {data['totalResults']}")

    saved, skipped = save_articles(ticker, company_name, data)
    print(f"Saved: {saved} new articles")
    print(f"Skipped: {skipped} duplicates")