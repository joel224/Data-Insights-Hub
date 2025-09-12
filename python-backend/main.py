
import os
import json
from datetime import datetime, timedelta
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# --- CORS Middleware Setup ---
# This is crucial for allowing the Next.js frontend (running on a different port)
# to communicate with the Python backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
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
    # TODO: Add logic here to securely get your API keys from environment variables
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
        # In a real scenario, you would use the openbb-sdk to get this data.
        # e.g., chart_data = openbb.economy.cpi(start_date="2023-01-01")
        # For now, we'll generate realistic mock data.
        today = datetime.now()
        chart_data = []
        news_data = []
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
    # Here, you would connect to your PostgreSQL database and insert the
    # data you just fetched. This creates a historical record.
    # TODO: Add your database logic here. For example:
    # with get_db_connection() as conn:
    #     store_in_postgres(conn, data_source, data)
    print(f"Data for {data_source} fetched. You would now store this in your PostgreSQL database.")


    # --- 3. Return Data to Frontend ---
    # The data is returned as a JSON response to the Next.js app.
    # The Next.js app will then send this data to the AI for analysis.
    return data

@app.get("/")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# Example of a helper function for database interaction
# def store_in_postgres(connection, source, data_to_store):
#     # Implement your database insertion logic here
#     print(f"Storing {source} data in PostgreSQL...")
#     # cursor = connection.cursor()
#     # query = "INSERT INTO your_table (source, data, timestamp) VALUES (%s, %s, %s)"
#     # cursor.execute(query, (source, json.dumps(data_to_store), datetime.now()))
#     # connection.commit()
#     # cursor.close()
#     pass
