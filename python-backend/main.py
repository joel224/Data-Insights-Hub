from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import random
from datetime import date, timedelta

# Load environment variables from a .env file in the same directory
load_dotenv()

app = FastAPI()

# Configure CORS to allow the Next.js frontend to communicate with this backend.
# In a production environment, you would want to restrict this to your frontend's actual origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# --- Service-Specific Data Fetching Functions ---
# Replace the mock logic in these functions with your actual API calls.

def fetch_plaid_transactions():
    """
    Fetches financial transactions from the Plaid API.
    
    This is a mock implementation. In a real application, you would use the
    Plaid client library to fetch data.
    """
    # PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    # PLAID_SECRET = os.getenv("PLAID_SECRET")
    # ACCESS_TOKEN = os.getenv("PLAID_ACCESS_TOKEN") # You would get this from Plaid Link
    
    # Example using a hypothetical Plaid client:
    # try:
    #     client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, environment='development')
    #     response = client.Transactions.get(ACCESS_TOKEN, start_date='2024-01-01', end_date='2024-07-30')
    #     transactions = response['transactions']
    #     # You would then format 'transactions' to match the required structure below
    # except plaid.errors.PlaidError as e:
    #     raise HTTPException(status_code=500, detail=f"Plaid API error: {e}")

    print("Fetching mock data for Plaid...")
    return [
        {"id": "txn1", "date": "2024-07-22", "name": "TechCorp Subscription", "amount": -19.99, "category": "Software"},
        {"id": "txn2", "date": "2024-07-21", "name": "Lunch at The Cafe", "amount": -15.50, "category": "Food and Drink"},
        {"id": "txn3", "date": "2024-07-20", "name": "Freelance Payment", "amount": 1200.00, "category": "Income"},
        {"id": "txn4", "date": "2024-07-19", "name": "Office Supplies", "amount": -75.20, "category": "Business"},
        {"id": "txn5", "date": "2024-07-18", "name": "Gas Fill-up", "amount": -55.80, "category": "Travel"},
    ]

def fetch_clearbit_company_info():
    """
    Fetches company enrichment data from the Clearbit API.
    
    This is a mock implementation. You would use a library like 'requests'
    to call the Clearbit API.
    """
    # CLEARBIT_API_KEY = os.getenv("CLEARBIT_API_KEY")
    # COMPANY_DOMAIN = "google.com" # This could be a parameter
    
    # Example using requests:
    # headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
    # url = f"https://company.clearbit.com/v2/companies/find?domain={COMPANY_DOMAIN}"
    # try:
    #     response = requests.get(url, headers=headers)
    #     response.raise_for_status() # Raises an exception for bad status codes
    #     company_data = response.json()
    #     # Format 'company_data' to match the required structure below
    # except requests.exceptions.RequestException as e:
    #     raise HTTPException(status_code=500, detail=f"Clearbit API request failed: {e}")

    print("Fetching mock data for Clearbit...")
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

def fetch_openbb_stock_data():
    """
    Fetches stock market data from the OpenBB API.
    
    This is a mock implementation. In a real application, you would use the
    OpenBB SDK.
    """
    # OPENBB_API_KEY = os.getenv("OPENBB_API_KEY")
    # STOCK_TICKER = "AAPL" # This could be a parameter

    # Example using a hypothetical OpenBB SDK:
    # try:
    #     obb.account.login(pat=OPENBB_API_KEY)
    #     data = obb.equity.price.historical(
    #         STOCK_TICKER,
    #         start_date=(date.today() - timedelta(days=30)).strftime('%Y-%m-%d'),
    #         provider="fmp"
    #     ).to_df()
    #     # Format the 'data' DataFrame to match the required structure below
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"OpenBB SDK error: {e}")

    print("Fetching mock data for OpenBB...")
    data = []
    today = date.today()
    current_price = 150.0
    for i in range(30, -1, -1):
        d = today - timedelta(days=i)
        # Simulate price fluctuation
        current_price += (random.random() - 0.5) * 5
        current_price = max(140.0, min(160.0, current_price))
        data.append({
            "date": d.strftime('%b %d'), # Format date as 'Jul 22'
            "close": round(current_price, 2)
        })
    return data

# --- Main API Endpoint ---

@app.get("/api/data/{data_source}")
async def get_data(data_source: str):
    """
    The primary API endpoint for the Next.js frontend.
    It routes requests to the correct data fetching function based on the URL.
    
    In a real application, after fetching, you would save the data to your
    PostgreSQL database before returning it.
    """
    print(f"Received data request for source: {data_source}")
    
    if data_source == "plaid":
        data = fetch_plaid_transactions()
    elif data_source == "clearbit":
        data = fetch_clearbit_company_info()
    elif data_source == "openbb":
        data = fetch_openbb_stock_data()
    else:
        # If the data_source is not one of the above, return an error
        raise HTTPException(status_code=404, detail="Data source not found. Use 'plaid', 'clearbit', or 'openbb'.")

    # TODO: Add your database logic here.
    # For example, using psycopg2 or SQLAlchemy:
    # conn = get_db_connection()
    # save_data_to_postgres(conn, data_source, data)
    # conn.close()
    
    return data

@app.get("/")
async def root():
    """A simple root endpoint to confirm the server is running."""
    return {"message": "Data Insights Hub - Python Backend is running!"}

# --- How to Run This Server ---
# 1. Make sure you are in the 'python-backend' directory.
# 2. Create a '.env' file for your API keys.
# 3. Install dependencies: pip install -r requirements.txt
# 4. Start the server: uvicorn main:app --reload
#
# The server will be available at http://127.0.0.1:8000
# The frontend expects to communicate with this address.
