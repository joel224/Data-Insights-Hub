
import os
import json
from datetime import datetime
import random
import sys
import requests
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from starlette.staticfiles import StaticFiles
import google.generativeai as genai

# --- CORS Middleware Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Connection Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"DEBUG: Attempting to connect with DATABASE_URL: {DATABASE_URL}")

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

# --- Gemini AI Setup ---
def generate_insights_from_gemini(data_source: str, data: str):
    """Generates insights by calling the Gemini API."""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        print("🔴 GEMINI_API_KEY is not set. Please check your environment variables in Railway.")
        raise HTTPException(status_code=500, detail="AI API key is not configured.")

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Base prompt structure
        prompt_template = f"You are a fintech analyst. Based on the following performance data for {today_date}, provide a short summary and 3 actionable recommendations to improve performance. Data:\n\n{data}"
        
        # Specific prompts for each data source
        if data_source == "plaid":
            prompt = f"You are a fintech analyst specializing in personal finance. Based on the following financial transaction data, provide a short summary and 3 actionable recommendations to improve the user's financial performance. Data:\n\n{data}"
        elif data_source == "clearbit":
             prompt = f"You are a business strategy analyst. Based on the following company performance data, provide a short summary and 3 actionable recommendations to improve the company's business performance and market position. Data:\n\n{data}"
        elif data_source == "openbb":
             prompt = f"You are a stock market analyst. Based on the following stock market performance data (including chart data, news, and performance metrics), provide a short summary and 3 actionable investment recommendations for a potential investor. Data:\n\n{data}"
        else:
            prompt = prompt_template

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"🔴 Error calling Gemini API: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during insight generation: {str(e)}")


# --- API Models ---
class InsightsRequest(BaseModel):
    dataSource: str
    data: str

# --- API Endpoints ---

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """
    Handles browser requests for the site favicon.
    Returns a 204 No Content response to prevent 404/502 errors.
    """
    return Response(content=None, status_code=204)

@app.get("/api/get-latest-data/{data_source}")
async def get_latest_data(data_source: str):
    """
    This endpoint fetches the most recent data for a given data source
    from the PostgreSQL database.
    """
    print(f"Received request for latest '{data_source}' data from the database.")
    
    if data_source not in ["plaid", "clearbit", "openbb"]:
        raise HTTPException(status_code=400, detail="Invalid data source")

    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=404, detail="Database connection not configured. Please ensure DATABASE_URL is set in Railway.")

    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT data
                FROM api_data
                WHERE api_name = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            
            result = cur.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail=f"No data found for data source: {data_source}. Run the scheduler to populate data.")

            return result['data']

    except Exception as e:
        print(f"🔴 Error fetching data from database: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching data: {str(e)}")
    finally:
        if db_conn:
            db_conn.close()

@app.post("/api/generate-insights")
async def get_insights(request: InsightsRequest):
    """
    This endpoint generates AI insights by calling the Gemini API directly from Python.
    """
    print(f"Received request to generate REAL insights for '{request.dataSource}' using Gemini.")
    
    try:
        insights = generate_insights_from_gemini(request.dataSource, request.data)
        return {"insights": insights}
    except HTTPException as e:
        # Re-raise HTTPExceptions to return proper status codes to the client
        raise e
    except Exception as e:
        print(f"🔴 Error in get_insights endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

app.mount("/", StaticFiles(directory="out", html=True), name="static")
