
import os
import json
from datetime import datetime, timedelta
import random
import psycopg2
import sys
import requests
import google.generativeai as genai

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"DEBUG: Attempting to connect with DATABASE_URL from scheduler.py")

    if not DATABASE_URL:
        print("🔴 DATABASE_URL is not set. Please check your environment variables in Railway.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 Could not connect to the database: {e}")
        return None
    except Exception as e:
        print(f"🔴 An unexpected error occurred during database connection: {e}")
        return None


def create_schema(connection):
    """Creates the necessary tables if they don't exist."""
    if not connection:
        print("🔴 Cannot create schema, no database connection.")
        return
    
    try:
        with connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_data (
                    id SERIAL PRIMARY KEY,
                    api_name VARCHAR(50) NOT NULL UNIQUE,
                    data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS daily_recommendations (
                    id SERIAL PRIMARY KEY,
                    data_source VARCHAR(50) NOT NULL UNIQUE,
                    insights TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)
        connection.commit()
        print("🟢 Schema checked/created successfully.")
    except Exception as e:
        print(f"🔴 Error creating schema: {e}")
        connection.rollback()


def fetch_live_news():
    """Fetches live financial news from NewsAPI.org."""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        print("🟡 NEWS_API_KEY not set. Skipping live news fetch.")
        return [{"id": "1", "title": "Live News Fetching Disabled: NEWS_API_KEY is not set.", "url": "#", "source": "System", "published": "Now"}]

    try:
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
        print(f"🟢 Successfully fetched {len(news_data)} news articles.")
        return news_data
    except requests.exceptions.RequestException as e:
        print(f"🔴 Error fetching live news: {e}")
        return [{"id": "1", "title": "Failed to fetch live news.", "url": "#", "source": "System Error", "published": "Now"}]


def fetch_and_store_data(source):
    """
    Fetches data for the specified source and stores it in the PostgreSQL database.
    """
    print(f"--- Running data fetch pipeline for: {source} ---")
    
    data = {"news": fetch_live_news()}
    
    if not data or not data.get("news"):
        print(f"🟡 No data fetched for {source}. Skipping database storage.")
        return

    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 Aborting storage for {source}. Failed to get database connection.")
        return

    try:
        with db_conn.cursor() as cur:
            query = """
                INSERT INTO api_data (api_name, data, timestamp)
                VALUES (%s, %s, NOW() AT TIME ZONE 'utc')
                ON CONFLICT (api_name) DO UPDATE SET
                    data = EXCLUDED.data,
                    timestamp = EXCLUDED.timestamp;
            """
            cur.execute(query, (source, json.dumps(data)))
        db_conn.commit()
        print(f"🟢 Data for {source} successfully stored in PostgreSQL.")
    except Exception as e:
        print(f"🔴 Error storing data for {source}: {e}")
        db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
    
    print(f"--- Data fetch pipeline finished for: {source} ---")


def generate_and_store_insights(source):
    """
    Generates insights using Gemini for a given data source and stores them.
    """
    print(f"--- Running insight generation pipeline for: {source} ---")
    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 Aborting insight generation for {source}. Failed to get database connection.")
        return

    try:
        # 1. Fetch the latest raw data
        raw_data = None
        with db_conn.cursor() as cur:
            cur.execute("SELECT data FROM api_data WHERE api_name = %s ORDER BY timestamp DESC LIMIT 1", (source,))
            result = cur.fetchone()
            if result:
                raw_data = result[0]
        
        if not raw_data:
            print(f"🟡 No raw data found for {source}. Skipping insight generation.")
            return

        # 2. Generate insights with Gemini
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            print("🔴 GEMINI_API_KEY not set. Cannot generate insights.")
            return

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        today_date = datetime.now().strftime("%Y-%m-%d")
        prompt = f"You are a fintech analyst. Based on the following performance data for {today_date}, provide a short summary and 3 actionable recommendations to improve performance. Data:\n\n{json.dumps(raw_data, indent=2)}"
        
        response = model.generate_content(prompt)
        insights = response.text

        # 3. Store the generated insights
        with db_conn.cursor() as cur:
            query = """
                INSERT INTO daily_recommendations (data_source, insights, timestamp)
                VALUES (%s, %s, NOW() AT TIME ZONE 'utc')
                ON CONFLICT (data_source) DO UPDATE SET
                    insights = EXCLUDED.insights,
                    timestamp = EXCLUDED.timestamp;
            """
            cur.execute(query, (source, insights))
        db_conn.commit()
        print(f"🟢 AI insights for {source} successfully generated and stored.")

    except Exception as e:
        print(f"🔴 Error during insight generation/storage for {source}: {e}")
        db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
    
    print(f"--- Insight generation pipeline finished for: {source} ---")


if __name__ == "__main__":
    print("🚀 Starting scheduled data job...")

    conn = get_db_connection()
    if conn:
        create_schema(conn)
        conn.close()
    else:
        print("🔴 Cannot proceed without a database connection. Exiting scheduler.")
        sys.exit(1)

    data_sources_to_run = ["openbb", "plaid", "clearbit"]

    for source in data_sources_to_run:
        fetch_and_store_data(source)
        generate_and_store_insights(source)
    
    print("✅ Scheduled data job finished successfully.")

    