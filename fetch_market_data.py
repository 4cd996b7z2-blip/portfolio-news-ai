import yfinance as yf
from database import init_db, insert_market_data

def fetch_market_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info

if __name__ == "__main__":
    init_db()
    ticker = "RELIANCE.NS"
    info = fetch_market_data(ticker)

    company_name = info.get("longName", "N/A")
    current_price = info.get("currentPrice")
    market_cap = info.get("marketCap")
    sector = info.get("sector")

    print(f"Company: {company_name}")
    print(f"Current Price: {current_price}")
    print(f"Market Cap: {market_cap}")
    print(f"Sector: {sector}")

    insert_market_data(ticker, company_name, current_price, market_cap, sector)
    print("\nSaved to database.")