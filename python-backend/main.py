from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from datetime import date, timedelta
import random

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure CORS
# This allows the Next.js frontend (running on a different port)
# to make requests to this Python backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# --- Mock Data Functions (replace with your actual API calls) ---

def get_mock_plaid_data():
    """Mocks fetching Plaid transaction data."""
    # PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    # PLAID_SECRET = os.getenv("PLAID_SECRET")
    # Access and use your Plaid API keys here
    print("Fetching data from Plaid...")
    return [
        {"id": "1", "date": "2024-07-20", "name": "Coffee Shop", "amount": -5.75, "category": "Food and Drink"},
        {"id": "2", "date": "2024-07-20", "name": "Online Subscription", "amount": -14.99, "category": "Services"},
        {"id": "3", "date": "2024-07-19", "name": "Grocery Store", "amount": -85.4, "category": "Groceries"},
        {"id": "4", "date": "2024-07-18", "name": "Salary Deposit", "amount": 2500, "category": "Income"},
        {"id": "5", "date": "2024-07-18", "name": "Gas Station", "amount": -45.22, "category": "Travel"},
    ]

def get_mock_clearbit_data():
    """Mocks fetching Clearbit company data."""
    # CLEARBIT_API_KEY = os.getenv("CLEARBIT_API_KEY")
    # Access and use your Clearbit API key here
    print("Fetching data from Clearbit...")
    return {
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

def get_mock_openbb_data():
    """Mocks fetching OpenBB stock data."""
    # OPENBB_API_KEY = os.getenv("OPENBB_API_KEY")
    # Access and use your OpenBB API key here
    print("Fetching data from OpenBB...")
    data = []
    today = date.today()
    current_price = 150.0
    for i in range(30, -1, -1):
        d = today - timedelta(days=i)
        current_price += (random.random() - 0.5) * 5
        current_price = max(140.0, min(160.0, current_price))
        data.append({
            "date": d.strftime('%b %d'),
            "close": round(current_price, 2)
        })
    return data

# --- API Endpoints ---

@app.get("/api/data/{data_source}")
async def get_data(data_source: str):
    """
    Main endpoint to fetch data from different sources.
    The Next.js app calls this endpoint.
    
    In a real application, you would:
    1. Fetch data from the source (Plaid, Clearbit, OpenBB).
    2. Save the fetched data to your PostgreSQL database.
    3. Return the fresh data to the frontend.
    """
    print(f"Received request for {data_source}")
    if data_source == "plaid":
        # TODO: Replace with your actual Plaid data fetching logic
        data = get_mock_plaid_data()
    elif data_source == "clearbit":
        # TODO: Replace with your actual Clearbit data fetching logic
        data = get_mock_clearbit_data()
    elif data_source == "openbb":
        # TODO: Replace with your actual OpenBB data fetching logic
        data = get_mock_openbb_data()
    else:
        raise HTTPException(status_code=404, detail="Data source not found")

    # TODO: Add logic here to save the 'data' to your PostgreSQL database.
    
    return data

@app.get("/")
async def root():
    return {"message": "Data Insights Hub - Python Backend"}

# To run this server:
# 1. Make sure you are in the 'python-backend' directory.
# 2. Install dependencies: pip install -r requirements.txt
# 3. Start the server: uvicorn main:app --reload
#
# The server will be available at http://127.0.0.1:8000
