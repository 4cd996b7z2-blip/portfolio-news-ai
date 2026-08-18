import os
import json
import time
from google import genai
from dotenv import load_dotenv
from database import init_db, add_relevance_columns, get_unanalyzed_articles, save_analysis

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def analyze_article(ticker, company_name, headline, source):
    prompt = f"""You are a financial analyst assistant. A user holds shares of {company_name} ({ticker}).

Analyze this news headline and explain why it matters to someone holding this stock.

Headline: "{headline}"
Source: {source}

Respond with ONLY a valid JSON object (no markdown formatting, no code blocks) in this exact structure:
{{
    "relevance_score": <integer 1-10, where 10 is extremely important and 1 is barely relevant>,
    "category": "<one of: earnings, legal, macro, competitor, product, management, market_sentiment, other>",
    "reasoning": "<one sentence explaining specifically why this matters to someone holding {ticker}>"
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

def process_all_unanalyzed():
    init_db()
    add_relevance_columns()

    articles = get_unanalyzed_articles()
    print(f"Found {len(articles)} unanalyzed articles.")

    for article_id, ticker, company_name, headline, source in articles:
        try:
            result = analyze_article(ticker, company_name, headline, source)
            save_analysis(
                article_id,
                result["relevance_score"],
                result["category"],
                result["reasoning"]
            )
            print(f"[{result['relevance_score']}/10] {headline[:60]}...")
        except Exception as e:
            print(f"Failed on article {article_id}: {e}")

        time.sleep(4.5)  # small delay to avoid hitting rate limits

if __name__ == "__main__":
    process_all_unanalyzed()