import os
import psycopg2
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from openbb import obb # Import the OpenBB library

# Load environment variables from the .env file for local development
load_dotenv()

# --- Step 0: Database Setup ---
def setup_database():
    """Initializes the PostgreSQL database and tables if they don't exist."""
    conn = None
    cur = None
    try:
        # Use the public URL for local connections.
        # This is the correct way to connect from outside the Railway network.
        database_url = os.environ.get("DATABASE_PUBLIC_URL")
        
        if not database_url:
            raise ValueError(
                "DATABASE_PUBLIC_URL environment variable is not set. "
                "Please make sure your .env file is configured correctly."
            )

        conn = psycopg2.connect(database_url)
        conn.autocommit = False # Ensure we are in transaction mode
        cur = conn.cursor()
        
        # Drop tables to ensure a clean schema on each run
        cur.execute("DROP TABLE IF EXISTS recommendations;")
        cur.execute("DROP TABLE IF EXISTS api_data;")
        
        # Create tables for API data and LLM recommendations
        cur.execute("""
            CREATE TABLE api_data (
                id SERIAL PRIMARY KEY,
                api_name TEXT NOT NULL,
                data JSONB NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE recommendations (
                id SERIAL PRIMARY KEY,
                api_name TEXT NOT NULL,
                summary TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                timestamp TIMESTAMP WITH TIME ZONE NOT NULL
            );
        """)
        conn.commit()
        print("Database setup complete.")
        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while setting up the database: {error}")
        if cur:
            cur.close()
        if conn:
            conn.close()
        return None, None

# --- Step 1: Real API Data Fetching ---
def fetch_openbb_data():
    """Fetches real financial data from OpenBB's free provider (Yahoo Finance)."""
    print("Step 1: Pulling live data from OpenBB API...")
    try:
        # Get historical price data for a stock using a free provider
        # We will get data for NVIDIA (NVDA) for a recent period
        # The .to_df() method converts the output into a pandas DataFrame
        # The .to_json() method then converts it to a JSON string
        stock_data_json = obb.equity.price.historical(symbol="NVDA").to_df().to_json()
        return json.loads(stock_data_json)
    except Exception as e:
        print(f"Error fetching data from OpenBB: {e}")
        return None


# --- Step 2: Local Storage (PostgreSQL) ---
def store_data_locally(conn, cur, api_name, data):
    """Stores fetched data in the PostgreSQL database."""
    try:
        cur.execute("INSERT INTO api_data (api_name, data, timestamp) VALUES (%s, %s, %s)",
                    (api_name, json.dumps(data), datetime.now(timezone.utc)))
        conn.commit()
        print(f"Data for {api_name} stored successfully.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while storing data for {api_name} in PostgreSQL: {error}")

# --- Step 3: Local LLM Analysis Simulation ---
def analyze_openbb_data(data):
    """Simulates LLM analysis for OpenBB data."""
    print("Step 3: Sending openbb data to LLM for analysis...")
    summary = """
Summary: OpenBB's stock price over the period from August 12th to September 11th, 2025, shows moderate volatility with no clear upward or downward trend. The price fluctuated between approximately 146 and 152, exhibiting a relatively narrow trading range. While there were periods of slight increases and decreases, overall, the performance can be characterized as sideways trading with limited significant gains or losses. Further analysis, incorporating broader market trends and company-specific news, would be necessary for a more complete assessment.
"""
    recommendations = """
Recommendations:
- Conduct a thorough competitive analysis to identify potential areas for differentiation and improvement in OpenBB's product offerings or services. This should include an examination of pricing strategies, feature sets, and target market positioning.
- Investigate and implement strategies to enhance investor relations and communication. Proactive engagement with investors and analysts through regular updates, press releases, and presentations could improve market confidence and potentially lead to a more favorable stock valuation.
- Analyze the trading volume and identify potential correlations with price fluctuations. Understanding factors driving demand and supply could provide insights into opportunities to optimize trading strategies and improve liquidity, potentially leading to more stable price movements.
"""
    return summary, recommendations

# --- Step 4: Store Recommendations ---
def store_recommendations(conn, cur, api_name, summary, recommendations):
    """Stores LLM recommendations in the PostgreSQL database."""
    try:
        cur.execute("INSERT INTO recommendations (api_name, summary, recommendations, timestamp) VALUES (%s, %s, %s, %s)",
                    (api_name, summary, recommendations, datetime.now(timezone.utc)))
        conn.commit()
        print("Recommendations stored successfully.")
    except (Exception, psycopg2.Error) as error:
        print(f"Error while storing recommendations in PostgreSQL: {error}")

# --- Main Pipeline Execution ---
def main():
    """Runs the full pipeline."""
    # Step 0: Set up the database
    conn, cur = setup_database()
    if not conn or not cur:
        return

    try:
        # Step 1: Fetch live data
        raw_data = fetch_openbb_data()
        
        if raw_data:
            # Step 2: Store data
            store_data_locally(conn, cur, "OpenBB", raw_data)

            # Step 3: Analyze data (simulated)
            summary, recommendations = analyze_openbb_data(raw_data)
            
            # Step 4: Store recommendations
            store_recommendations(conn, cur, "OpenBB", summary, recommendations)
            
            # Print output to console
            print("\n--- LLM Analysis & Recommendations ---")
            print("Summary:")
            print(summary)
            print("Recommendations:")
            print(recommendations)
        else:
            print("Failed to fetch data from OpenBB. Skipping subsequent steps.")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
