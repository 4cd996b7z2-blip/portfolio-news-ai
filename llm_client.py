import os
import json
import time
from portfolio import PORTFOLIO
from google import genai
from dotenv import load_dotenv
from database import init_db, add_relevance_columns, get_unanalyzed_articles, save_analysis

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_article(ticker, company_name, headline, source, portfolio_ticker, portfolio_company, relationship):
    if relationship == "direct":
        prompt = f"""You are a financial analyst assistant. A user holds shares of {portfolio_company} ({portfolio_ticker}).

Analyze this news headline about {company_name} and explain why it matters to someone holding this stock.

Headline: "{headline}"
Source: {source}

Respond with ONLY a valid JSON object (no markdown formatting, no code blocks) in this exact structure:
{{
    "relevance_score": <integer 1-10, where 10 is extremely important and 1 is barely relevant>,
    "category": "<one of: earnings, legal, macro, competitor, product, management, market_sentiment, other>",
    "reasoning": "<one sentence explaining specifically why this matters to someone holding {portfolio_ticker}>"
}}"""
    else:
        prompt = f"""You are a financial analyst assistant. A user holds shares of {portfolio_company} ({portfolio_ticker}).

This headline is about {company_name} ({ticker}), a competitor of {portfolio_company}. Analyze whether and how this news could affect {portfolio_company}'s competitive position — market share, pricing power, investor sentiment relative to competitors, etc.

Headline: "{headline}"
Source: {source}

Respond with ONLY a valid JSON object (no markdown formatting, no code blocks) in this exact structure:
{{
    "relevance_score": <integer 1-10, where 10 is a major competitive threat/opportunity and 1 is negligible competitive relevance>,
    "category": "competitor",
    "reasoning": "<one sentence explaining the specific competitive implication for {portfolio_ticker}, e.g. 'this could shift market share toward/away from {portfolio_company}'>"
}}"""

    response = client.models.generate_content(
        model="gemini-flash-lite-latest",
        contents=prompt
    )

    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    raw_text = raw_text.strip()

    return json.loads(raw_text)
def process_all_unanalyzed(limit=None):
    init_db()
    add_relevance_columns()

    articles = get_unanalyzed_articles(limit=limit)
    print(f"Found {len(articles)} unanalyzed articles.")
    # Build a quick lookup for portfolio company names
    portfolio_names = {h["ticker"]: h["company_name"] for h in PORTFOLIO}

    processed_count = 0
    for article_id, ticker, company_name, headline, source, portfolio_ticker, relationship in articles:
        portfolio_company = portfolio_names.get(portfolio_ticker, portfolio_ticker)
        try:
            result = analyze_article(ticker, company_name, headline, source, portfolio_ticker, portfolio_company, relationship)
            save_analysis(
                article_id,
                result["relevance_score"],
                result["category"],
                result["reasoning"]
            )
            print(f"[{result['relevance_score']}/10] ({relationship}) {headline[:55]}...")
            processed_count += 1
        except Exception as e:
            error_str = str(e)
            if "RESOURCE_EXHAUSTED" in error_str and "PerDay" in error_str:
                print(f"\nDaily quota reached after processing {processed_count} articles.")
                print("Stopping here — run this script again later to continue.")
                break
            else:
                print(f"Failed on article {article_id}: {e}")

        time.sleep(4.5)

    print(f"\nSession complete. Processed {processed_count} articles this run.")
if __name__ == "__main__":
    process_all_unanalyzed()