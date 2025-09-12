
import os
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# --- CORS Middleware Setup ---
# This is crucial for allowing the Next.js frontend (running on a different port)
# to communicate with the Python backend.
# We are allowing all origins, methods, and headers for local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
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

    # TODO: Add logic here to securely get your API keys from environment variables
    # For example: api_key = os.getenv("PLAID_API_KEY")

    # --- 1. Pull Data ---
    # In a real application, you would use an API client (e.g., plaid-python)
    # to fetch live data from the service's API.
    data = {}
    if data_source == "plaid":
        # Placeholder for fetching Plaid data
        print("Fetching data from Plaid...")
        data = [
            { "id": "1", "date": "2024-07-22", "name": "Tech Startup Inc.", "amount": 5000, "category": "Income" },
            { "id": "2", "date": "2024-07-21", "name": "Coffee Beans Co.", "amount": -15.50, "category": "Food & Drink" },
            { "id": "3", "date": "2024-07-20", "name": "Cloud Services LLC", "amount": -150.00, "category": "Services" },
        ]
    elif data_source == "clearbit":
        # Placeholder for fetching Clearbit data
        print("Fetching data from Clearbit...")
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
        # Placeholder for fetching OpenBB data
        print("Fetching data from OpenBB...")
        data = [
            {"date": "Jul 20", "close": 152.8},
            {"date": "Jul 21", "close": 155.2},
            {"date": "Jul 22", "close": 154.5},
        ]
    else:
        return {"error": "Invalid data source"}

    # --- 2. Store Data ---
    # Here, you would connect to your PostgreSQL database and insert the
    # data you just fetched. This creates a historical record.
    # Example (you would need to implement the database connection):
    # store_in_postgres(data_source, data)
    print(f"Data for {data_source} fetched. Next, you would store this in your database.")


    # --- 3. Return Data to Frontend ---
    # The data is returned as a JSON response to the Next.js app.
    # The Next.js app will then send this data to the AI for analysis.
    return data

@app.get("/")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# Example of a helper function for storing data
# def store_in_postgres(source, data_to_store):
#     # TODO: Implement your database connection and insertion logic here
#     print(f"Storing {source} data in PostgreSQL...")
#     pass

    