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

# --- Service-Specific Data Fetching & Storing Logic ---

# In a real application, you would replace these mock functions with actual API calls
# and database interactions.

# --- Plaid ---
def pull_plaid_data_from_api():
    """
    Pulls financial transactions from the Plaid API.
    This is a mock implementation. Replace with your actual Plaid client logic.
    """
    # PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
    # PLAID_SECRET = os.getenv("PLAID_SECRET")
    # ACCESS_TOKEN = os.getenv("PLAID_ACCESS_TOKEN")
    print("Step 1: Pulling data from Plaid API...")
    # try:
    #     client = plaid.Client(client_id=PLAID_CLIENT_ID, secret=PLAID_SECRET, environment='development')
    #     response = client.Transactions.get(ACCESS_TOKEN, start_date='2024-01-01', end_date='2024-07-30')
    #     return response['transactions'] # Or format as needed
    # except plaid.errors.PlaidError as e:
    #     raise HTTPException(status_code=500, detail=f"Plaid API error: {e}")
    return [
        {"id": "txn1", "date": "2024-07-22", "name": "TechCorp Subscription", "amount": -19.99, "category": "Software"},
        {"id": "txn2", "date": "2024-07-21", "name": "Lunch at The Cafe", "amount": -15.50, "category": "Food and Drink"},
        {"id": "txn3", "date": "2024-07-20", "name": "Freelance Payment", "amount": 1200.00, "category": "Income"},
    ]

def store_plaid_data_in_db(data):
    """Saves the fetched Plaid data into the PostgreSQL database."""
    print("Step 2: Storing Plaid data in PostgreSQL...")
    # Example using psycopg2:
    # conn = get_db_connection()
    # cur = conn.cursor()
    # for transaction in data:
    #     cur.execute("INSERT INTO plaid_transactions (id, date, name, amount, category) VALUES (%s, %s, %s, %s, %s)",
    #                 (transaction['id'], transaction['date'], transaction['name'], transaction['amount'], transaction['category']))
    # conn.commit()
    # cur.close()
    # conn.close()
    pass # Placeholder

# --- Clearbit ---
def pull_clearbit_data_from_api():
    """
    Pulls company enrichment data from the Clearbit API.
    This is a mock implementation. Replace with your actual Clearbit API call.
    """
    # CLEARBIT_API_KEY = os.getenv("CLEARBIT_API_KEY")
    print("Step 1: Pulling data from Clearbit API...")
    # headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
    # url = f"https://company.clearbit.com/v2/companies/find?domain=google.com"
    # response = requests.get(url, headers=headers)
    # return response.json()
    return {
        "companyName": "Innovate Inc.", "domain": "innovateinc.com",
        "description": "A leading provider of cutting-edge technology solutions.",
        "logo": "https://picsum.photos/seed/innovate/100/100", "location": "San Francisco, CA",
        "metrics": {"employees": 1200, "marketCap": "$15B", "annualRevenue": "$2.5B", "raised": "$500M"},
    }

def store_clearbit_data_in_db(data):
    """Saves the fetched Clearbit data into the PostgreSQL database."""
    print("Step 2: Storing Clearbit data in PostgreSQL...")
    pass # Placeholder

# --- OpenBB ---
def pull_openbb_data_from_api():
    """
    Pulls stock market data from the OpenBB SDK.
    This is a mock implementation. Replace with your actual OpenBB SDK logic.
    """
    # OPENBB_API_KEY = os.getenv("OPENBB_API_KEY")
    print("Step 1: Pulling data from OpenBB API...")
    # obb.account.login(pat=OPENBB_API_KEY)
    # data = obb.equity.price.historical("AAPL", provider="fmp").to_df()
    # return formatted_data
    data = []
    today = date.today()
    current_price = 150.0
    for i in range(30, -1, -1):
        d = today - timedelta(days=i)
        current_price += (random.random() - 0.5) * 5
        data.append({"date": d.strftime('%b %d'), "close": round(current_price, 2)})
    return data

def store_openbb_data_in_db(data):
    """Saves the fetched OpenBB data into the PostgreSQL database."""
    print("Step 2: Storing OpenBB data in PostgreSQL...")
    pass # Placeholder


# --- Main API Endpoint ---

@app.get("/api/data/{data_source}")
async def get_data_and_store(data_source: str):
    """
    This endpoint orchestrates the entire backend process:
    1. Pulls data from the specified external API.
    2. Stores that data in the PostgreSQL database.
    3. Returns the fresh data to the Next.js frontend for AI analysis.
    """
    print(f"\nReceived data request for source: {data_source}")
    
    if data_source == "plaid":
        fresh_data = pull_plaid_data_from_api()
        store_plaid_data_in_db(fresh_data)
    elif data_source == "clearbit":
        fresh_data = pull_clearbit_data_from_api()
        store_clearbit_data_in_db(fresh_data)
    elif data_source == "openbb":
        fresh_data = pull_openbb_data_from_api()
        store_openbb_data_in_db(fresh_data)
    else:
        raise HTTPException(status_code=404, detail="Data source not found.")

    print("Step 3: Returning fresh data to frontend for analysis.")
    return fresh_data

@app.get("/")
async def root():
    return {"message": "Data Insights Hub - Python Backend is running!"}
