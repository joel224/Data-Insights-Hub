
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
    This endpoint generates AI insights by calling the Genkit flow endpoint.
    """
    print(f"Received request to generate real insights for '{request.dataSource}'.")
    genkit_flow_url = "http://localhost:3400/flows/generateDataInsightsFlow"
    
    payload = {
        "input": {
            "dataSource": request.dataSource,
            "data": request.data
        }
    }

    try:
        response = requests.post(genkit_flow_url, json=payload, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        
        flow_result = response.json()
        if "output" in flow_result:
            return flow_result["output"]
        else:
            raise HTTPException(status_code=500, detail="Genkit flow did not return the expected output format.")

    except requests.exceptions.RequestException as e:
        print(f"🔴 Error calling Genkit flow: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during insight generation: {str(e)}")
    except Exception as e:
        print(f"🔴 Error processing Genkit response: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred after insight generation: {str(e)}")


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

app.mount("/", StaticFiles(directory="out", html=True), name="static")
