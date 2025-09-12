
import os
import json
from datetime import datetime, timedelta
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# import psycopg2 # Uncomment this line when you're ready to connect to PostgreSQL

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# --- Database Connection Setup (Example) ---
# DATABASE_URL = os.getenv("DATABASE_URL")

# def get_db_connection():
#     """Establishes a connection to the PostgreSQL database."""
#     conn = psycopg2.connect(DATABASE_URL)
#     return conn

# def store_in_postgres(connection, source, data_to_store):
#     """
#     Stores the fetched data in the PostgreSQL database.
#     This function is a placeholder and needs to be adapted to your database schema.
#     """
#     print(f"Storing {source} data in PostgreSQL...")
#     # try:
#     #     with connection.cursor() as cur:
#     #         # Example: Create a table if it doesn't exist (you might do this once, separately)
#     #         cur.execute("""
#     #             CREATE TABLE IF NOT EXISTS api_data (
#     #                 id SERIAL PRIMARY KEY,
#     #                 source VARCHAR(50),
#     #                 data JSONB,
#     #                 fetched_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
#     #             );
#     #         """)
#     #
#     #         # Insert the new data
#     #         query = "INSERT INTO api_data (source, data) VALUES (%s, %s)"
#     #         cur.execute(query, (source, json.dumps(data_to_store)))
#     #     connection.commit()
#     #     print("Data successfully stored.")
#     # except Exception as e:
#     #     print(f"Error storing data: {e}")
#     #     connection.rollback()
#     # finally:
#     #     connection.close()
#     pass # Remove this 'pass' when you implement the database logic


# --- CORS Middleware Setup ---
# This is crucial for allowing the Next.js frontend to communicate with the Python backend.
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

    # --- 1. Pull Data ---
    # This is where you would use an API client (e.g., openbb-sdk, plaid-python)
    # to fetch live data from the service's API.
    # You would use your API keys securely fetched from environment variables.
    # For example: api_key = os.getenv("OPENBB_API_KEY")

    data = {}
    if data_source == "plaid":
        print("Fetching data from Plaid...")
        # Placeholder for fetching Plaid data
        data = [
            { "id": "1", "date": "2024-07-22", "name": "Tech Startup Inc.", "amount": 5000, "category": "Income" },
            { "id": "2", "date": "2024-07-21", "name": "Coffee Beans Co.", "amount": -15.50, "category": "Food & Drink" },
            { "id": "3", "date": "2024-07-20", "name": "Cloud Services LLC", "amount": -150.00, "category": "Services" },
        ]
    elif data_source == "clearbit":
        print("Fetching data from Clearbit...")
        # Placeholder for fetching Clearbit data
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
    elif data_source == "openbb":
        print("Fetching rich data from OpenBB...")
        # --- Placeholder for fetching rich OpenBB data ---
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
        # --- End of Placeholder ---
        
    else:
        return {"error": "Invalid data source"}

    # --- 2. Store Data ---
    # Once you have your DATABASE_URL, you can uncomment these lines
    # to connect to your PostgreSQL database and store the fetched data.
    # print("Attempting to store data in PostgreSQL...")
    # db_conn = get_db_connection()
    # if db_conn:
    #     store_in_postgres(db_conn, data_source, data)


    # --- 3. Return Data to Frontend ---
    # The data is returned as a JSON response to the Next.js app.
    return data

@app.get("/")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}
