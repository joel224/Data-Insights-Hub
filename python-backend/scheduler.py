
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

# --- Configuration ---
IS_DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_URL = "postgresql://postgres:LmGJalVzyaEimCvkJGLCvwEibHeDrhTI@maglev.proxy.rlwy.net:15976/railway"

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    print("⚙️ [DB] Attempting to connect to the database...")

    if not DATABASE_URL:
        print("🔴 [DB] DATABASE_URL is not set. This should be hardcoded.")
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

def fetch_marketstack_eod(symbol='AAPL', limit=30):
    """Fetches End-of-Day stock data from MarketStack for a given symbol."""
    MARKETSTACK_API_KEY = os.getenv("MARKETSTACK_API_KEY")
    if not MARKETSTACK_API_KEY:
        print("🟡 [MarketStack] MARKETSTACK_API_KEY not set. Skipping fetch.")
        return {}
    
    print(f"📡 [MarketStack] Fetching EOD data for {symbol} from marketstack.com...")
    try:
        url = f"http://api.marketstack.com/v1/eod?access_key={MARKETSTACK_API_KEY}&symbols={symbol}&limit={limit}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if IS_DEBUG:
            print("🤖 [DEBUG] RAW MARKETSTACK EOD RESPONSE:")
            print(json.dumps(data, indent=2))
        
        # Check for errors in the response
        if 'error' in data:
            print(f"🔴 [MarketStack] API Error: {data['error']['message']}")
            return {}

        eod_data = data.get('data', [])
        
        # Add calculations for SMA and RSI
        prices = [d['close'] for d in reversed(eod_data)] # Reverse to have oldest first
        
        def calculate_sma(data, window):
            if len(data) < window: return []
            return [sum(data[i-window:i]) / window for i in range(window, len(data) + 1)]

        def calculate_rsi(data, window=14):
            if len(data) < window: return []
            deltas = [data[i] - data[i-1] for i in range(1, len(data))]
            gains = [d if d > 0 else 0 for d in deltas]
            losses = [-d if d < 0 else 0 for d in deltas]

            avg_gain = sum(gains[:window]) / window
            avg_loss = sum(losses[:window]) / window

            rsi_values = []
            for i in range(window, len(data)):
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
                
                # Wilder's smoothing
                gain = gains[i-1] if i-1 < len(gains) else 0
                loss = losses[i-1] if i-1 < len(losses) else 0
                avg_gain = (avg_gain * (window - 1) + gain) / window
                avg_loss = (avg_loss * (window - 1) + loss) / window

            return rsi_values

        sma_20 = calculate_sma(prices, 20)
        rsi_14 = calculate_rsi(prices)

        # Align data points
        final_data = []
        # Start from the point where we have all data (SMA, RSI, price)
        start_index = 20 # Corresponds to SMA 20 window
        sma_offset = start_index - len(sma_20)
        rsi_offset = start_index - (len(prices) - len(rsi_14))
        
        for i in range(start_index, len(prices)):
            data_point = eod_data[len(prices) - 1 - i] # eod_data is newest first
            
            # Format date to be more readable
            date_obj = datetime.fromisoformat(data_point['date'].replace('Z', '+00:00'))

            final_data.append({
                "date": date_obj.strftime('%b %d'),
                "price": data_point['close'],
                "sma": sma_20[i - sma_offset - (len(prices) - len(sma_20))] if i >= start_index else None,
                "rsi": rsi_14[i - rsi_offset - (len(prices)-len(rsi_14))] if i >= start_index and (i - rsi_offset - (len(prices)-len(rsi_14))) < len(rsi_14) else None
            })
        
        # --- Performance Metrics Calculation ---
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Volatility (Annualized Standard Deviation of Returns)
        volatility = (sum([(r - (sum(returns) / len(returns)))**2 for r in returns]) / (len(returns) - 1))**0.5 * (252**0.5)
        
        # Annual Return
        annual_return = ((prices[-1] / prices[0]) ** (252 / len(prices))) - 1
        
        # Sharpe Ratio (assuming risk-free rate of 0)
        sharpe_ratio = (sum(returns) / len(returns)) / ((sum([(r - (sum(returns) / len(returns)))**2 for r in returns]) / (len(returns) - 1))**0.5) * (252**0.5)

        performance = {
            "volatility": f"{volatility:.1%}",
            "sharpeRatio": f"{sharpe_ratio:.1f}",
            "annualReturn": f"{annual_return:.1%}"
        }

        print(f"🟢 [MarketStack] Successfully fetched and processed {len(final_data)} EOD data points for {symbol}.")
        return {"eod": final_data, "symbol": symbol, "performance": performance}
        
    except requests.exceptions.RequestException as e:
        print(f"🔴 [MarketStack] Error fetching EOD data: {e}")
        return {}


def fetch_newsapi_news():
    """Fetches live general business news from NewsAPI.org."""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    if not NEWS_API_KEY:
        print("🟡 [NewsAPI] NEWS_API_KEY not set. Skipping fetch.")
        return []

    try:
        print("📡 [NewsAPI] Fetching data from newsapi.org...")
        url = f"https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey={NEWS_API_KEY}&pageSize=10"
        response = requests.get(url)
        response.raise_for_status() 
        articles_json = response.json()
        
        if IS_DEBUG:
            print("🤖 [DEBUG] RAW NEWSAPI.ORG RESPONSE:")
            print(json.dumps(articles_json, indent=2))
        
        articles = articles_json.get("articles", [])
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


def fetch_and_store_data(source):
    """
    Fetches data for the specified source and stores it in the PostgreSQL database.
    """
    print(f"--- ⏯️ [Pipeline] Starting data fetch for: {source} ---")
    
    data = {}
    if source == 'plaid':
        print("🤖 [DEBUG] Fetching data for 'plaid' using fetch_marketstack_eod()")
        data = fetch_marketstack_eod()
    elif source == 'clearbit':
        print("🤖 [DEBUG] Fetching data for 'clearbit' using fetch_newsapi_news()")
        data = {"news": fetch_newsapi_news()}
    elif source == 'openbb':
        print("🤖 [DEBUG] Fetching data for 'openbb' using fetch_newsapi_news()")
        data = {"news": fetch_newsapi_news()}

    if not data:
        print(f"🟡 [Pipeline] No data fetched for {source}. Skipping database storage.")
        return

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
        if not GEMINI_API_KEY:
            print("🟡 [AI] GEMINI_API_KEY not found. Skipping insight generation.")
            return
            
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # --- Source-Specific Prompts ---
        analyst_type = "fintech analyst"
        data_description = "performance data"
        
        if source == 'plaid':
            analyst_type = "financial analyst"
            data_description = "end-of-day stock data"
        elif source == 'clearbit':
            analyst_type = "marketing analyst"
            data_description = "the latest business news"
        elif source == 'openbb':
            analyst_type = "stock market analyst"
            data_description = "the latest market news"

        prompt = f"""You are a {analyst_type}. Based on the following {data_description} for {today_date}, provide a short summary and 3 actionable recommendations. Keep it concise. Data:\n\n{json.dumps(raw_data, indent=2)}"""
        
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
        if db_conn:
            db_conn.rollback()
    finally:
        if db_conn:
            db_conn.close()
    
    print(f"--- ✅ [AI] Insight generation finished for: {source} ---")


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
        print("🟢 Schema checked/created successfully in scheduler.")
    except Exception as e:
        print(f"🔴 Error creating schema in scheduler: {e}")
        connection.rollback()


if __name__ == "__main__":
    print("🚀 Starting scheduled data job...")

    # --- Upfront API Key Check ---
    print("🔍 [Pre-flight] Checking for required API keys...")
    required_keys = ["NEWS_API_KEY", "GEMINI_API_KEY", "MARKETSTACK_API_KEY"]
    missing_keys = [key for key in required_keys if not os.getenv(key)]

    if missing_keys:
        print(f"🔴 [FATAL] The following required API keys are missing in your .env file or environment: {', '.join(missing_keys)}")
        print("Please add them and try again.")
        sys.exit(1)
    else:
        print("🟢 [Pre-flight] All required API keys are present.")

    # --- Schema Check ---
    db_conn = get_db_connection()
    if db_conn:
        create_schema(db_conn)
        db_conn.close()
    else:
        print("🔴 [Scheduler] Database connection failed. Cannot verify schema or run jobs.")
        sys.exit(1)

    # --- Run Data Pipelines ---
    data_sources_to_run = ["plaid", "clearbit", "openbb"]

    for source in data_sources_to_run:
        fetch_and_store_data(source)
        generate_and_store_insights(source)
    
    print("✅ Scheduled data job finished successfully.")





    