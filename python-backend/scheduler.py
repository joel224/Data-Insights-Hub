
import os
import json
from datetime import datetime, timedelta
import random
import psycopg2
import sys

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"DEBUG: DATABASE_URL from scheduler.py: {DATABASE_URL}") # Debug print

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
            # You can add other table creations here if needed
            # cur.execute("""
            #     CREATE TABLE IF NOT EXISTS recommendations ( ... );
            # """)
        connection.commit()
        print("🟢 Schema checked/created successfully.")
    except Exception as e:
        print(f"🔴 Error creating schema: {e}")
        connection.rollback()


def fetch_and_store_data(source):
    """
    Fetches data from the specified source, simulates real API calls,
    and stores it in the PostgreSQL database.
    """
    print(f"--- Running pipeline for: {source} ---")
    
    data = {}
    
    # --- 1. PULL DATA (Simulation) ---
    if source == "plaid":
        print("Fetching data from Plaid...")
        data = [
            { "id": "1", "date": "2024-07-22", "name": "Tech Startup Inc.", "amount": 5000, "category": "Income" },
            { "id": "2", "date": "2024-07-21", "name": "Coffee Beans Co.", "amount": -15.50, "category": "Food & Drink" },
            { "id": "3", "date": "2024-07-20", "name": "Cloud Services LLC", "amount": -150.00, "category": "Services" },
        ]
    elif source == "clearbit":
        print("Fetching data from Clearbit...")
        data = {
            "companyName": "Innovate Inc.", "domain": "innovateinc.com", "description": "Innovate Inc. is a leading provider of cutting-edge technology solutions.",
            "logo": "https://picsum.photos/seed/innovate/100/100", "location": "San Francisco, CA",
            "metrics": { "employees": 1200, "marketCap": "$15B", "annualRevenue": "$2.5B", "raised": "$500M" },
        }
    elif source == "openbb":
        print("Fetching rich data from OpenBB...")
        today = datetime.now()
        chart_data = []
        price = 150
        for i in range(30):
            date = today - timedelta(days=i)
            price += random.uniform(-2.5, 2.5)
            sma = price * random.uniform(0.95, 1.05)
            rsi = random.uniform(30, 70)
            chart_data.append({
                "date": date.strftime("%b %d"), "close": round(price, 2), "sma": round(sma, 2), "rsi": round(rsi, 2)
            })
        chart_data.reverse()
        data = {
          "chartData": chart_data,
          "news": [
            {"id": "1", "title": "Tech Stocks Rally on Positive News", "url": "#", "source": "MarketWatch", "published": "2h ago"},
            {"id": "2", "title": "AI Chipmaker Announces Record Earnings", "url": "#", "source": "Reuters", "published": "5h ago"},
          ],
          "performance": { "volatility": "15.2%", "sharpeRatio": "1.8", "annualReturn": "25.4%" }
        }
    else:
        print(f"🔴 Invalid data source specified: {source}")
        return

    # --- 2. STORE DATA ---
    db_conn = get_db_connection()
    if not db_conn:
        print("🔴 Aborting scheduler. Failed to get database connection.")
        # This will now cause the scheduler to stop running if the DB is not configured.
        sys.exit(1)

    try:
        with db_conn.cursor() as cur:
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

    # Ensure the database schema is ready
    conn = get_db_connection()
    if conn:
        create_schema(conn)
        conn.close()
    else:
        print("🔴 Cannot proceed without a database connection. Exiting scheduler.")
        sys.exit(1) # Exit with an error code

    # List of data sources to fetch
    # You can add 'plaid' and 'clearbit' here as well.
    data_sources_to_run = ["openbb", "plaid", "clearbit"]

    for source in data_sources_to_run:
        fetch_and_store_data(source)
    
    print("✅ Scheduled data fetch job finished successfully.")
    # The script will automatically exit after this line.
