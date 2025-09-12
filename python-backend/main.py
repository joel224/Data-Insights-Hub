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
# This is important for allowing the Next.js app to talk to the Python API
# when running in development or as separate services.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you might want to restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# --- Serve Static Files ---
# This must be the last mount
app.mount("/", StaticFiles(directory="out", html=True), name="static")

@app.exception_handler(404)
async def custom_404_handler(_, __):
    return FileResponse('out/index.html')
