
import os
import json
from datetime import datetime, timedelta
import random
import psycopg2
import sys
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

import os
import psycopg2

# --- Configuration ---
IS_DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    print("⚙️  [DB] Attempting to connect to the database...")
    
    # Use os.getenv() to read the environment variable set by Railway
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Check if the DATABASE_URL environment variable is present
    if not DATABASE_URL:
        print("🔴 [DB] DATABASE_URL environment variable is not set. Please ensure it's configured in Railway.")
        return None
    try:
        # Use the variable to connect
        conn = psycopg2.connect(DATABASE_URL)
        print("🟢 [DB] Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 [DB] Could not connect to the database: {e}")
        return None
    except Exception as e:
        print(f"🔴 [DB] An unexpected error occurred during database connection: {e}")
        return None


def calculate_metrics(eod_data):
    """Calculates SMA, RSI, and Performance Metrics from EOD data."""
    if not eod_data:
        if IS_DEBUG: print("  [Calc] No EOD data to calculate metrics.")
        return eod_data, None

    if IS_DEBUG: print(f"  [Calc] Calculating metrics for {len(eod_data)} data points...")
    prices = [item['price'] for item in eod_data]
    sma_period = 5
    rsi_period = 5

    # SMA Calculation
    for i in range(len(eod_data)):
        if i >= sma_period - 1:
            eod_data[i]['sma'] = round(sum(p['price'] for p in eod_data[i-sma_period+1:i+1]) / sma_period, 2)
        else:
            eod_data[i]['sma'] = None

    # RSI Calculation
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    avg_gain = sum(gains[:rsi_period]) / rsi_period if len(gains) >= rsi_period else 0
    avg_loss = sum(losses[:rsi_period]) / rsi_period if len(losses) >= rsi_period else 0

    for i in range(len(eod_data)):
        if i < rsi_period:
            eod_data[i]['rsi'] = None
            continue
        if i > rsi_period:
            avg_gain = (avg_gain * (rsi_period - 1) + (gains[i-1] if i-1 < len(gains) else 0)) / rsi_period
            avg_loss = (avg_loss * (rsi_period - 1) + (losses[i-1] if i-1 < len(losses) else 0)) / rsi_period
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        eod_data[i]['rsi'] = round(rsi, 2)

    # Performance Metrics
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    avg_return = sum(returns) / len(returns) if returns else 0
    std_dev = (sum([(r - avg_return)**2 for r in returns]) / len(returns))**0.5 if returns else 0
    annual_return = ((1 + avg_return)**252 - 1) * 100 if avg_return is not None else 0
    volatility = std_dev * (252**0.5) * 100 if std_dev is not None else 0
    sharpe_ratio = (annual_return / 100) / (volatility / 100) if volatility else 0

    performance = {
        "volatility": f"{volatility:.2f}%",
        "sharpeRatio": f"{sharpe_ratio:.2f}",
        "annualReturn": f"{annual_return:.2f}%"
    }
    if IS_DEBUG: print(f"  [Calc] Calculated performance: {performance}")
    
    first_valid_index = max(sma_period - 1, rsi_period)
    
    if IS_DEBUG: print(f"  [Calc] Metrics calculation complete. Trimming to first valid index: {first_valid_index}")
    return eod_data[first_valid_index:], performance


def fetch_marketstack_eod():
    """Fetches end-of-day stock data from MarketStack API."""
    MARKETSTACK_API_KEY = os.getenv("MARKETSTACK_API_KEY")
    if not MARKETSTACK_API_KEY:
        print("🟡 [MarketStack] MARKETSTACK_API_KEY not set. Using mocked data.")
        return {"eod": [], "symbol": "AAPL", "performance": {}}

    try:
        print("📡 [MarketStack] Fetching EOD data for AAPL from marketstack.com...")
        url = f"http://api.marketstack.com/v1/eod?access_key={MARKETSTACK_API_KEY}&symbols=AAPL&limit=20"
        response = requests.get(url)
        response.raise_for_status()
        eod_json = response.json()
        
        eod_raw = sorted(eod_json.get("data", []), key=lambda x: datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%S%z'))
        eod_data = [{"date": item['date'][:10], "price": round(item['close'], 2)} for item in eod_raw]

        eod_data_with_metrics, performance = calculate_metrics(eod_data)
        
        print(f"🟢 [MarketStack] Successfully fetched and processed {len(eod_data_with_metrics)} EOD data points for AAPL.")
        return {"eod": eod_data_with_metrics, "symbol": "AAPL", "performance": performance}

    except requests.exceptions.RequestException as e:
        print(f"🔴 [MarketStack] Error fetching live EOD data: {e}")
        return {"eod": [], "symbol": "AAPL", "performance": {}}


def fetch_newsdata_io_news():
    """Fetches live general business news from NewsData.io."""
    NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
    if not NEWSDATA_API_KEY:
        print("🟡 [NewsData.io] NEWSDATA_API_KEY not set. Skipping fetch.")
        return []

    try:
        print("📡 [NewsData.io] Fetching data from newsdata.io...")
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&category=business&language=en&size=10"
        response = requests.get(url)
        response.raise_for_status()
        articles_json = response.json()

        if IS_DEBUG:
            print("  [NewsData.io] Raw Response:")
            print(json.dumps(articles_json, indent=2))

        articles = articles_json.get("results", [])
        news_data = []
        for i, article in enumerate(articles):
            published_at_str = article.get('pubDate')
            published = "some time ago"
            if published_at_str:
                published_at = datetime.strptime(published_at_str, '%Y-%m-%d %H:%M:%S')
                now = datetime.utcnow()
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
                "url": article["link"],
                "source": article.get("source_id", "Unknown"),
                "published": published
            })
        print(f"🟢 [NewsData.io] Successfully fetched and formatted {len(news_data)} articles.")
        return news_data
    except requests.exceptions.RequestException as e:
        print(f"🔴 [NewsData.io] Error fetching live news: {e}")
        return []


def fetch_and_store_data(source):
    """Fetches data for the specified source and stores it in the database."""
    print(f"\n--- ▶️  [Pipeline] Starting data fetch for: {source} ---")

    data = {}
    if source == 'plaid':
        if IS_DEBUG: print("  [Pipeline] Fetching data for 'plaid' using fetch_marketstack_eod()")
        data = fetch_marketstack_eod()
    elif source in ['clearbit', 'openbb']:
        if IS_DEBUG: print(f"  [Pipeline] Fetching data for '{source}' using fetch_newsdata_io_news()")
        data = {"news": fetch_newsdata_io_news()}

    if not data or (isinstance(data, dict) and not data.get('eod') and not data.get('news')):
        print(f"🟡 [Pipeline] No data fetched for {source}. Skipping database storage.")
        return

    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 [DB] Aborting storage for {source}. Failed to get database connection.")
        return

    try:
        with db_conn.cursor() as cur:
            print(f"  [DB] Storing data for '{source}'...")
            query = """
                INSERT INTO api_data (api_name, data, timestamp)
                VALUES (%s, %s, NOW() AT TIME ZONE 'utc')
                ON CONFLICT (api_name) DO UPDATE SET
                    data = EXCLUDED.data,
                    timestamp = EXCLUDED.timestamp;
            """
            cur.execute(query, (source, json.dumps(data)))
        db_conn.commit()
        print(f"🟢 [DB] Data for {source} successfully stored.")
    except Exception as e:
        print(f"🔴 [DB] Error storing data for {source}: {e}")
        db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
            if IS_DEBUG: print("  [DB] Connection closed.")
    print(f"--- ✅ [Pipeline] Data fetch finished for: {source} ---")


def generate_and_store_insights(source):
    """Generates insights using Gemini for a given data source and stores them."""
    print(f"\n--- ▶️  [AI] Starting insight generation for: {source} ---")
    db_conn = get_db_connection()
    if not db_conn:
        print(f"🔴 [DB] Aborting insight generation for {source}. Failed to get database connection.")
        return

    try:
        # 1. Fetch the latest raw data
        raw_data = None
        with db_conn.cursor() as cur:
            print(f"  [DB] Fetching latest raw data for '{source}' to generate insights...")
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
        if not GEMINI_API_KEY:
            print("🔴 [AI] GEMINI_API_KEY not found. Skipping insight generation.")
            return

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        today_date = datetime.now().strftime("%Y-%m-%d")

        analyst_type, focus, data_description = "general", "performance", "data"
        if source == 'plaid':
            analyst_type, focus, data_description = "financial analyst", "financial indicators", "end-of-day stock data and recent news"
        elif source == 'clearbit':
            analyst_type, focus, data_description = "marketing analyst", "market sentiment", "recent business news articles"
        elif source == 'openbb':
            analyst_type, focus, data_description = "stock market analyst", "investment opportunities", "recent financial news articles"

        prompt = f"""You are a {analyst_type}. Based on the following {data_description} for {today_date}, provide a short summary and 3 actionable recommendations to improve performance related to {focus}. Keep it concise. Data:\n\n{json.dumps(raw_data, indent=2)}"""
        if IS_DEBUG:
            print(f"  [AI] Prompt for {source}:\n{prompt[:300]}...")

        print(f"🧠 [AI] Generating insights for {source}... (This may take a moment)")
        response = model.generate_content(prompt)
        insights = response.text
        print(f"💡 [AI] Insights successfully generated for {source}.")
        if IS_DEBUG:
            print(f"  [AI] Generated Insights:\n{insights}")

        # 3. Store the generated insights
        with db_conn.cursor() as cur:
            print(f"  [DB] Storing AI insights for '{source}'...")
            query = """
                INSERT INTO daily_recommendations (data_source, insights, timestamp)
                VALUES (%s, %s, NOW() AT TIME ZONE 'utc')
                ON CONFLICT (data_source) DO UPDATE SET
                    insights = EXCLUDED.insights,
                    timestamp = EXCLUDED.timestamp;
            """
            cur.execute(query, (source, insights))
        db_conn.commit()
        print(f"🟢 [DB] AI insights for {source} successfully stored.")

    except Exception as e:
        print(f"🔴 [AI] Error during insight generation/storage for {source}: {e}")
        if db_conn: db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
            if IS_DEBUG: print("  [DB] Connection closed.")
    print(f"--- ✅ [AI] Insight generation finished for: {source} ---")


def create_schema(connection):
    """Creates the necessary tables if they don't exist."""
    if not connection:
        print("🔴 [DB] Cannot create schema, no database connection.")
        return
    try:
        with connection.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS api_data (id SERIAL PRIMARY KEY, api_name VARCHAR(50) NOT NULL UNIQUE, data JSONB, timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'));")
            cur.execute("CREATE TABLE IF NOT EXISTS daily_recommendations (id SERIAL PRIMARY KEY, data_source VARCHAR(50) NOT NULL UNIQUE, insights TEXT, timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc'));")
        connection.commit()
        print("🟢 [DB] Schema checked/created successfully in scheduler.")
    except Exception as e:
        print(f"🔴 [DB] Error creating schema in scheduler: {e}")
        connection.rollback()


if __name__ == "__main__":
    print("\n🚀 Starting scheduled data job...")
    start_time = datetime.now()

    print("🔍 [Pre-flight] Checking for required API keys...")
    required_keys = ["NEWSDATA_API_KEY", "GEMINI_API_KEY", "MARKETSTACK_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        print(f"🔴 [FATAL] The following required API keys are missing: {', '.join(missing_keys)}")
        sys.exit(1)
    else:
        print("🟢 [Pre-flight] All required API keys are present.")

    db_conn = get_db_connection()
    if db_conn:
        create_schema(db_conn)
        db_conn.close()
    else:
        print("🔴 [FATAL] Database connection failed. Cannot verify schema or run jobs.")
        sys.exit(1)

    data_sources_to_run = ["plaid", "clearbit", "openbb"]
    for source in data_sources_to_run:
        fetch_and_store_data(source)
        generate_and_store_insights(source)
    
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n✅ Scheduled data job finished successfully in {duration.total_seconds():.2f} seconds.")

    

    