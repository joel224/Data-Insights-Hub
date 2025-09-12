
import os
import json
from datetime import datetime, timedelta
import random
import psycopg2
import sys
import requests
import google.generativeai as genai
from openbb import obb

# --- Configuration ---
IS_DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print("⚙️ [DB] Attempting to connect to the database...")

    if not DATABASE_URL:
        print("🔴 [DB] DATABASE_URL is not set. Please check your environment variables in Railway.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("🟢 [DB] Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 [DB] Could not connect to the database: {e}")
        return None
    except Exception as e:
        print(f"🔴 [DB] An unexpected error occurred during database connection: {e}")
        return None


def fetch_newsapi_news():
    """Fetches live general business news from NewsAPI.org."""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    print("🔍 [NewsAPI] Checking for NEWS_API_KEY...")
    if not NEWS_API_KEY:
        print("🟡 [NewsAPI] NEWS_API_KEY not set. Skipping fetch.")
        return [{"id": "1", "title": "Live News Fetching Disabled: NEWS_API_KEY is not set.", "url": "#", "source": "System", "published": "Now"}]

    try:
        print("📡 [NewsAPI] Fetching data from newsapi.org...")
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}&pageSize=10"
        response = requests.get(url)
        response.raise_for_status() 
        articles = response.json().get("articles", [])
        
        news_data = []
        for i, article in enumerate(articles):
            published_at_str = article.get('publishedAt')
            if not published_at_str:
                published = "some time ago"
            else:
                published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                now = datetime.now(published_at.tzinfo)
                time_diff = now - published_at
                
                if time_diff.total_seconds() < 3600:
                    published = f"{int(time_diff.total_seconds() / 60)}m ago"
                elif time_diff.total_seconds() < 86400:
                    published = f"{int(time_diff.total_seconds() / 3600)}h ago"
                else:
                    published = f"{int(time_diff.total_seconds() / 86400)}d ago"

            news_data.append({
                "id": str(i + 1),
                "title": article["title"],
                "url": article["url"],
                "source": article.get("source", {}).get("name", "Unknown"),
                "published": published
            })
        print(f"🟢 [NewsAPI] Successfully fetched {len(news_data)} articles.")
        return news_data
    except requests.exceptions.RequestException as e:
        print(f"🔴 [NewsAPI] Error fetching live news: {e}")
        return [{"id": "1", "title": "Failed to fetch live news from NewsAPI.", "url": "#", "source": "System Error", "published": "Now"}]

def fetch_openbb_news():
    """Fetches financial news using the OpenBB SDK."""
    OPENBB_API_KEY = os.getenv("OPENBB_API_KEY")
    print("🔍 [OpenBB] Checking for OPENBB_API_KEY...")
    if not OPENBB_API_KEY:
        print("🟡 [OpenBB] OPENBB_API_KEY not set. Skipping fetch.")
        return [{"id": "1", "title": "OpenBB News Fetching Disabled: OPENBB_API_KEY is not set.", "url": "#", "source": "System", "published": "Now"}]
    
    try:
        print("🔐 [OpenBB] Authenticating with OpenBB PAT...")
        obb.account.login(pat=OPENBB_API_KEY)
        print("🟢 [OpenBB] Successfully authenticated with OpenBB.")
        print("📡 [OpenBB] Fetching world news...")
        res = obb.news.world(limit=10)
        articles = res.to_dicts()

        news_data = []
        for i, article in enumerate(articles):
            published_at = article.get('published_at')
            if not published_at:
                published = "some time ago"
            else:
                now = datetime.now(published_at.tzinfo)
                time_diff = now - published_at

                if time_diff.total_seconds() < 3600:
                    published = f"{int(time_diff.total_seconds() / 60)}m ago"
                elif time_diff.total_seconds() < 86400:
                    published = f"{int(time_diff.total_seconds() / 3600)}h ago"
                else:
                    published = f"{int(time_diff.total_seconds() / 86400)}d ago"
            
            news_data.append({
                "id": article.get("id", str(i + 1)),
                "title": article.get("title", "No title available"),
                "url": article.get("url", "#"),
                "source": article.get("publisher", {}).get("name", "Unknown"),
                "published": published
            })
        print(f"🟢 [OpenBB] Successfully fetched {len(news_data)} news articles.")
        return news_data
    except Exception as e:
        print(f"🔴 [OpenBB] Error fetching news: {e}")
        return [{"id": "1", "title": "Failed to fetch live news from OpenBB.", "url": "#", "source": "System Error", "published": "Now"}]


def fetch_and_store_data(source):
    """
    Fetches data for the specified source and stores it in the PostgreSQL database.
    """
    print(f"--- ⏯️ [Pipeline] Starting data fetch for: {source} ---")
    
    data = {}
    if source == 'openbb':
        data = {"news": fetch_openbb_news()}
    elif source in ['plaid', 'clearbit']:
        data = {"news": fetch_newsapi_news()}
    
    if not data or not data.get("news"):
        print(f"🟡 [Pipeline] No data fetched for {source}. Skipping database storage.")
        return

    if IS_DEBUG:
        print(f"📋 [DEBUG] Fetched data for {source}:")
        print(json.dumps(data, indent=2))

    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 [DB] Aborting storage for {source}. Failed to get database connection.")
        return

    try:
        with db_conn.cursor() as cur:
            print(f"💾 [DB] Storing data for '{source}'...")
            query = """
                INSERT INTO api_data (api_name, data, timestamp)
                VALUES (%s, %s, NOW() AT TIME ZONE 'utc')
                ON CONFLICT (api_name) DO UPDATE SET
                    data = EXCLUDED.data,
                    timestamp = EXCLUDED.timestamp;
            """
            cur.execute(query, (source, json.dumps(data)))
        db_conn.commit()
        print(f"🟢 [DB] Data for {source} successfully stored in PostgreSQL.")
    except Exception as e:
        print(f"🔴 [DB] Error storing data for {source}: {e}")
        db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
    
    print(f"--- ✅ [Pipeline] Data fetch finished for: {source} ---")


def generate_and_store_insights(source):
    """
    Generates insights using Gemini for a given data source and stores them.
    """
    print(f"--- ⏯️ [AI] Starting insight generation for: {source} ---")
    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 [DB] Aborting insight generation for {source}. Failed to get database connection.")
        return

    try:
        # 1. Fetch the latest raw data
        raw_data = None
        with db_conn.cursor() as cur:
            print(f"🔍 [DB] Fetching latest raw data for '{source}' to generate insights...")
            cur.execute("SELECT data FROM api_data WHERE api_name = %s ORDER BY timestamp DESC LIMIT 1", (source,))
            result = cur.fetchone()
            if result:
                raw_data = result[0]
                print(f"🟢 [DB] Found raw data for '{source}'.")
        
        if not raw_data:
            print(f"🟡 [AI] No raw data found for {source}. Skipping insight generation.")
            return

        # 2. Generate insights with Gemini
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        print("🔍 [AI] Checking for GEMINI_API_KEY...")
        if not GEMINI_API_KEY:
            print("🔴 [AI] GEMINI_API_KEY not set. Cannot generate insights.")
            return
        print("🟢 [AI] GEMINI_API_KEY found.")

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        today_date = datetime.now().strftime("%Y-%m-%d")
        prompt = f"You are a fintech analyst. Based on the following performance data for {today_date}, provide a short summary and 3 actionable recommendations to improve performance. Data:\n\n{json.dumps(raw_data, indent=2)}"
        
        if IS_DEBUG:
            print(f"🤖 [DEBUG] Sending this prompt to Gemini for {source}:")
            print(prompt)

        print(f"🧠 [AI] Generating insights for {source}... (This may take a moment)")
        response = model.generate_content(prompt)
        insights = response.text
        print(f"💡 [AI] Insights generated for {source}.")

        if IS_DEBUG:
            print(f"🤖 [DEBUG] Received insights for {source}:")
            print(insights)

        # 3. Store the generated insights
        with db_conn.cursor() as cur:
            print(f"💾 [DB] Storing AI insights for '{source}'...")
            query = """
                INSERT INTO daily_recommendations (data_source, insights, timestamp)
                VALUES (%s, %s, NOW() AT TIME ZONE 'utc')
                ON CONFLICT (data_source) DO UPDATE SET
                    insights = EXCLUDED.insights,
                    timestamp = EXCLUDED.timestamp;
            """
            cur.execute(query, (source, insights))
        db_conn.commit()
        print(f"🟢 [DB] AI insights for {source} successfully generated and stored.")

    except Exception as e:
        print(f"🔴 [AI] Error during insight generation/storage for {source}: {e}")
        db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
    
    print(f"--- ✅ [AI] Insight generation finished for: {source} ---")


if __name__ == "__main__":
    print("🚀 Starting scheduled data job...")

    conn = get_db_connection()
    if not conn:
        print("🔴 Cannot proceed without a database connection. Exiting scheduler.")
        sys.exit(1)
    conn.close()


    data_sources_to_run = ["openbb", "plaid", "clearbit"]

    for source in data_sources_to_run:
        fetch_and_store_data(source)
        generate_and_store_insights(source)
    
    print("✅ Scheduled data job finished successfully.")

    