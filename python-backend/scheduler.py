
import os
import json
from datetime import datetime, timedelta
import random
import psycopg2
import sys
import requests

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
                    api_name VARCHAR(50) NOT NULL,
                    data JSONB,
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
        # Return an empty list or a message if the key is not set
        return [{"id": "1", "title": "Live News Fetching Disabled: NEWS_API_KEY is not set.", "url": "#", "source": "System", "published": "Now"}]

    try:
        # Fetching top business headlines from the US
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
    Fetches data from the specified source and stores it in the PostgreSQL database.
    This function now only contains real API calls or placeholders for them.
    """
    print(f"--- Running pipeline for: {source} ---")
    
    data = {}
    
    # --- 1. PULL DATA ---
    if source == "plaid":
        print("Fetching data from Plaid...")
        # To implement this, you would need to use the Plaid Python client.
        # This requires PLAID_CLIENT_ID, PLAID_SECRET, and an ACCESS_TOKEN.
        # Example:
        # plaid_client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, environment='sandbox')
        # response = plaid_client.Transactions.get(access_token=ACCESS_TOKEN, start_date='2024-01-01', end_date='2024-02-01')
        # data = response['transactions']
        print("🟡 Plaid data fetching is not implemented. Requires API keys.")
        data = [] # Store empty data if not implemented

    elif source == "clearbit":
        print("Fetching data from Clearbit...")
        # To implement this, you would use the Clearbit API.
        # This requires a CLEARBIT_API_KEY.
        # Example:
        # headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
        # response = requests.get('https://company.clearbit.com/v2/companies/find?domain=google.com', headers=headers)
        # data = response.json()
        print("🟡 Clearbit data fetching is not implemented. Requires API keys.")
        data = {} # Store empty data if not implemented

    elif source == "openbb":
        print("Fetching real news for OpenBB...")
        # This uses the NewsAPI as a proxy for financial news.
        live_news = fetch_live_news()
        data = {"news": live_news} # The data now only contains real news

    else:
        print(f"🔴 Invalid data source specified: {source}")
        return

    # --- 2. STORE DATA ---
    if not data:
        print(f"🟡 No data fetched for {source}. Skipping database storage.")
        return

    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 Aborting storage for {source}. Failed to get database connection.")
        return

    try:
        with db_conn.cursor() as cur:
            # Check if data for this source already exists and delete it to store the new data
            cur.execute("DELETE FROM api_data WHERE api_name = %s", (source,))
            query = "INSERT INTO api_data (api_name, data) VALUES (%s, %s)"
            cur.execute(query, (source, json.dumps(data)))
        db_conn.commit()
        print(f"🟢 Data for {source} successfully stored in PostgreSQL.")
    except Exception as e:
        print(f"🔴 Error storing data for {source}: {e}")
        db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
    
    print(f"--- Pipeline finished for: {source} ---")


if __name__ == "__main__":
    print("🚀 Starting scheduled data fetch job...")

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
    
    print("✅ Scheduled data fetch job finished successfully.")
