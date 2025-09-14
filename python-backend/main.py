
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
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
IS_DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# --- Database Connection and Schema Setup ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        if IS_DEBUG:
            print("🔴 [DB] DATABASE_URL environment variable is not set.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        if IS_DEBUG:
            print("🟢 [DB] Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        if IS_DEBUG:
            print(f"🔴 [DB] Could not connect to the database: {e}")
        return None
    except Exception as e:
        if IS_DEBUG:
            print(f"🔴 [DB] An unexpected error occurred during database connection: {e}")
        return None


def create_schema(connection):
    """Creates the necessary tables if they don't exist."""
    if not connection:
        if IS_DEBUG: print("🔴 [DB] Cannot create schema, no database connection.")
        return
    
    try:
        with connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_data (
                    id SERIAL PRIMARY KEY,
                    api_name VARCHAR(50) NOT NULL UNIQUE,
                    data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS daily_recommendations (
                    id SERIAL PRIMARY KEY,
                    data_source VARCHAR(50) NOT NULL UNIQUE,
                    insights TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)
        connection.commit()
        if IS_DEBUG: print("🟢 [DB] Schema checked/created successfully.")
    except Exception as e:
        if IS_DEBUG: print(f"🔴 [DB] Error creating schema: {e}")
        connection.rollback()


# --- FastAPI App Lifespan (for startup events) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    if IS_DEBUG: print("🚀 [FastAPI] Application starting up...")
    db_conn = get_db_connection()
    if db_conn:
        create_schema(db_conn)
        db_conn.close()
        if IS_DEBUG: print("🟢 [FastAPI] Startup complete.")
    else:
        if IS_DEBUG: print("🔴 [FastAPI] Database connection failed on startup. Schema not created.")
    yield
    # On shutdown
    if IS_DEBUG: print("👋 [FastAPI] Application shutting down...")


# --- CORS Middleware Setup ---
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    This endpoint fetches the most recent data and pre-generated insights
    for a given data source from the PostgreSQL database.
    """
    if data_source not in ["plaid", "clearbit", "openbb"]:
        raise HTTPException(status_code=400, detail="Invalid data source")

    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection not configured. Please ensure DATABASE_URL is set in Railway.")

    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Fetch raw data
            cur.execute("""
                SELECT data, timestamp
                FROM api_data
                WHERE api_name = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            data_result = cur.fetchone()

            # Fetch insights
            cur.execute("""
                SELECT insights, timestamp
                FROM daily_recommendations
                WHERE data_source = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            insights_result = cur.fetchone()

            if not data_result or not data_result.get('data'):
                 raise HTTPException(status_code=404, detail=f"No data or insights found for {data_source}. Run the scheduler to populate data.")

            response_data = {
                "data": data_result['data'],
                "insights": insights_result['insights'] if insights_result else "No insights were generated for this data source. Please check the scheduler logs."
            }
            
            # For Plaid, the frontend expects news data. We will fetch this from the 'openbb' source.
            if data_source == 'plaid':
                cur.execute("""
                    SELECT data
                    FROM api_data
                    WHERE api_name = 'openbb'
                    ORDER BY timestamp DESC
                    LIMIT 1;
                """)
                news_data_result = cur.fetchone()
                if news_data_result and news_data_result.get('data'):
                    response_data['data']['news'] = news_data_result['data'].get('news', [])

            return response_data

    except HTTPException as http_exc:
        # Re-raise HTTPException to let FastAPI handle it
        raise http_exc
    except Exception as e:
        error_detail = f"An error occurred while fetching data: {e}"
        raise HTTPException(status_code=500, detail=error_detail)
    finally:
        if db_conn:
            db_conn.close()


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# --- Static Files Mounting ---

# Determine the correct path to the 'out' directory.
# This logic handles running from the root vs. from the python-backend directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, "..", "out") # Go up one level from python-backend to the root

if not os.path.isdir(static_files_dir):
    # Fallback for if the script is run from the project root
    static_files_dir = os.path.join(current_dir, "out")

if os.path.isdir(static_files_dir):
    app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
    if IS_DEBUG: print(f"🟢 [FastAPI] Serving static files from: {static_files_dir}")
else:
    if IS_DEBUG: print(f"🟡 [FastAPI] Warning: Static files directory not found. The frontend will not be served.")

    