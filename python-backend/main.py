import os
import json
from datetime import datetime
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
import sys

# Add the parent directory to the path to allow imports from src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.ai.flows import generate_data_insights

# Load environment variables from a .env file
load_dotenv()

app = FastAPI()

# --- Database Connection Setup ---
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 Could not connect to the database: {e}")
        return None
    except Exception as e:
        print(f"🔴 An unexpected error occurred during database connection: {e}")
        return None

# --- CORS Middleware Setup ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Models ---
class InsightsRequest(BaseModel):
    dataSource: str
    data: str

# --- API Endpoints ---

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
        raise HTTPException(status_code=500, detail="Failed to connect to the database.")

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
                raise HTTPException(status_code=404, detail=f"No data found for data source: {data_source}")

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
    This endpoint generates AI insights based on the provided data.
    It acts as a wrapper around the Genkit flow.
    """
    print(f"Received request to generate insights for '{request.dataSource}'.")
    try:
        # The Genkit flow is now a TypeScript module, we cannot call it directly from Python.
        # For the purpose of this architecture, we will simulate the insight generation.
        # In a real microservices architecture, you might call a separate Genkit service here.
        
        insights_result = await generate_data_insights.generateDataInsights({
            "dataSource": request.dataSource,
            "data": request.data
        })
        return insights_result

    except Exception as e:
        print(f"🔴 Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during insight generation: {str(e)}")


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# --- Static Files Serving ---
# This must be the last part of the file
# It serves the static Next.js app from the 'out' directory
app.mount("/", StaticFiles(directory="out", html=True), name="static")
