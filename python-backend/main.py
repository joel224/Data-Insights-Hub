
import os
import json
from datetime import datetime, timedelta
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import psycopg2 # Use this to connect to PostgreSQL

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# --- Database Connection Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        # Pass the connection string directly to psycopg2.connect
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 Could not connect to the database: {e}")
        print("Please check if your DATABASE_URL is correct in the .env file and if the database is running.")
        return None
    except Exception as e:
        print(f"🔴 An unexpected error occurred during database connection: {e}")
        return None


def store_in_postgres(connection, source, data_to_store):
    """
    Stores the fetched data in the PostgreSQL database.
    This function creates a table if it doesn't exist and inserts the data.
    """
    if not connection:
        print("🔴 Cannot store data, no database connection.")
        return

    print(f"Storing {source} data in PostgreSQL...")
    try:
        with connection.cursor() as cur:
            # This SQL statement should match your existing table structure.
            # Using the schema you provided: (id, api_name, data, timestamp)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_data (
                    id SERIAL PRIMARY KEY,
                    api_name VARCHAR(50),
                    data JSONB,
                    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)

            # Use "api_name" to match your table schema.
            query = "INSERT INTO api_data (api_name, data) VALUES (%s, %s)"
            # The %s placeholders are automatically and safely handled by psycopg2
            cur.execute(query, (source, json.dumps(data_to_store)))
        
        # Commit the transaction to make the changes permanent
        connection.commit()
        print("🟢 Data successfully stored.")
    except Exception as e:
        print(f"🔴 Error storing data: {e}")
        # Rollback the transaction in case of an error
        connection.rollback()
    finally:
        # It's good practice to close the connection when you're done
        if connection:
            connection.close()


# --- CORS Middleware Setup ---
# This allows the Next.js frontend (running on a different port) to talk to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development. For production, restrict this.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# --- API Endpoints ---

@app.get("/api/data/{data_source}")
async def get_data(data_source: str):
    """
    This is the main endpoint the Next.js frontend will call.
    Based on the data_source parameter, it fetches data from the appropriate service,
    stores it, and then returns it to the frontend.
    """
    print(f"Received request for {data_source} data.")

    data = {}
    
    # --- 1. PULL DATA (The "What" and "From Where") ---
    # This block simulates fetching data from an external API.
    # In a real app, you would use an API client (e.g., openbb-sdk, plaid-python)
    # to fetch live data from the service's API using API keys from your .env file.
    
    if data_source == "plaid":
        print("Fetching data from Plaid...")
        # --- In a real app, replace this with your actual Plaid client ---
        # client = plaid.ApiClient(...)
        # response = client.transactions_get(...)
        # data = response.to_dict()
        data = [
            { "id": "1", "date": "2024-07-22", "name": "Tech Startup Inc.", "amount": 5000, "category": "Income" },
            { "id": "2", "date": "2024-07-21", "name": "Coffee Beans Co.", "amount": -15.50, "category": "Food & Drink" },
            { "id": "3", "date": "2024-07-20", "name": "Cloud Services LLC", "amount": -150.00, "category": "Services" },
        ]
        # --- End of Simulation ---
        
    elif data_source == "clearbit":
        print("Fetching data from Clearbit...")
        # --- In a real app, replace this with your actual Clearbit client ---
        # clearbit.key = os.getenv("CLEARBIT_API_KEY")
        # company = clearbit.Company.find(domain='innovateinc.com', stream=True)
        # data = format_clearbit_data(company)
        data = {
            "companyName": "Innovate Inc.",
            "domain": "innovateinc.com",
            "description": "Innovate Inc. is a leading provider of cutting-edge technology solutions, specializing in AI-driven analytics and cloud computing services.",
            "logo": "https://picsum.photos/seed/innovate/100/100",
            "location": "San Francisco, CA",
            "metrics": {
                "employees": 1200,
                "marketCap": "$15B",
                "annualRevenue": "$2.5B",
                "raised": "$500M",
            },
        }
        # --- End of Simulation ---

    elif data_source == "openbb":
        print("Fetching rich data from OpenBB...")
        # --- This simulates fetching rich OpenBB data ---
        today = datetime.now()
        chart_data = []
        price = 150
        for i in range(30):
            date = today - timedelta(days=i)
            price += random.uniform(-2.5, 2.5)
            sma = price * random.uniform(0.95, 1.05) # simulate sma
            rsi = random.uniform(30, 70)
            chart_data.append({
                "date": date.strftime("%b %d"),
                "close": round(price, 2),
                "sma": round(sma, 2),
                "rsi": round(rsi, 2)
            })
        chart_data.reverse() # Order from past to present
        
        data = {
          "chartData": chart_data,
          "news": [
            {"id": "1", "title": "Tech Stocks Rally on Positive Economic News", "url": "#", "source": "MarketWatch", "published": "2h ago"},
            {"id": "2", "title": "AI Chipmaker Announces Record Quarterly Earnings", "url": "#", "source": "Reuters", "published": "5h ago"},
            {"id": "3", "title": "Federal Reserve Signals Potential Rate Cuts Later This Year", "url": "#", "source": "Bloomberg", "published": "1d ago"},
          ],
          "performance": {
            "volatility": "15.2%",
            "sharpeRatio": "1.8",
            "annualReturn": "25.4%"
          }
        }
        # --- End of Simulation ---
        
    else:
        return {"error": "Invalid data source"}

    # --- 2. STORE DATA (The "Secure Vault") ---
    # After fetching the data, store it in your PostgreSQL database.
    print("Attempting to store data in PostgreSQL...")
    db_conn = get_db_connection()
    if db_conn:
        # The 'source' parameter here will be used as the 'api_name' in the database.
        store_in_postgres(db_conn, data_source, data)
    else:
        print("🔴 Skipping database storage because connection failed.")


    # --- 3. RETURN DATA TO FRONTEND ---
    # The fresh data is returned as a JSON response to the Next.js app,
    # which will then send it to the LLM for analysis.
    return data

@app.get("/")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}



    