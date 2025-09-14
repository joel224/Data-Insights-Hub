
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
IS_DEBUG = True

# --- Database Connection and Schema Setup ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = "postgresql://postgres:LmGJalVzyaEimCvkJGLCvwEibHeDrhTI@maglev.proxy.rlwy.net:15976/railway"
    if not DATABASE_URL:
        print("🔴 [DB] DATABASE_URL is not set. Please check your environment variables in Railway.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        if IS_DEBUG:
            print("🟢 [DB] Database connection successful.")
        return conn
    except psycopg2.OperationalError as e:
        print(f"🔴 [DB] Could not connect to the database: {e}")
        return None
    except Exception as e:
        print(f"🔴 [DB] An unexpected error occurred during database connection: {e}")
        return None

def create_schema(connection):
    """Creates the necessary tables if they don't exist."""
    if not connection:
        print("🔴 [DB] Cannot create schema, no database connection.")
        return
    
    try:
        with connection.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS api_data (
                    id SERIAL PRIMARY KEY,
                    api_name VARCHAR(50) NOT NULL UNIQUE,
                    data JSONB,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS daily_recommendations (
                    id SERIAL PRIMARY KEY,
                    data_source VARCHAR(50) NOT NULL UNIQUE,
                    insights TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
                );
            """)
        connection.commit()
        print("🟢 [DB] Schema checked/created successfully.")
    except Exception as e:
        print(f"🔴 [DB] Error creating schema: {e}")
        connection.rollback()


# --- FastAPI App Lifespan (for startup events) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("🚀 [FastAPI] Application starting up...")
    db_conn = get_db_connection()
    if db_conn:
        create_schema(db_conn)
        db_conn.close()
        print("🟢 [FastAPI] Startup complete.")
    else:
        print("🔴 [FastAPI] Database connection failed on startup. Schema not created.")
    yield
    # On shutdown
    print("👋 [FastAPI] Application shutting down...")


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
    if IS_DEBUG:
        print(f"\n--- 🕵️  [API] Received request for latest '{data_source}' data ---")
    
    if data_source not in ["plaid", "clearbit", "openbb"]:
        if IS_DEBUG:
            print(f"❌ [API] Invalid data source '{data_source}' requested.")
        raise HTTPException(status_code=400, detail="Invalid data source")

    db_conn = get_db_connection()
    if not db_conn:
        if IS_DEBUG:
            print(f"❌ [API] Could not establish DB connection for '{data_source}' request.")
        raise HTTPException(status_code=500, detail="Database connection not configured. Please ensure DATABASE_URL is set in Railway.")

    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Fetch raw data
            if IS_DEBUG:
                print(f"  [DB] Fetching raw data for '{data_source}' from 'api_data' table...")
            cur.execute("""
                SELECT data, timestamp
                FROM api_data
                WHERE api_name = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            data_result = cur.fetchone()
            if IS_DEBUG:
                if data_result:
                    print(f"  [DB] Raw data found for '{data_source}'. Timestamp: {data_result['timestamp']}")
                else:
                    print(f"  [DB] No raw data found for '{data_source}' in 'api_data' table.")


            # Fetch insights
            if IS_DEBUG:
                print(f"  [DB] Fetching insights for '{data_source}' from 'daily_recommendations' table...")
            cur.execute("""
                SELECT insights, timestamp
                FROM daily_recommendations
                WHERE data_source = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            insights_result = cur.fetchone()
            if IS_DEBUG:
                if insights_result:
                    print(f"  [DB] Insights found for '{data_source}'. Timestamp: {insights_result['timestamp']}")
                else:
                     print(f"  [DB] No insights found for '{data_source}' in 'daily_recommendations' table.")


            if not data_result or not data_result.get('data'):
                 if IS_DEBUG:
                     print(f"  [API] Condition failed: 'not data_result or not data_result.get('data')'. Raising 404.")
                 raise HTTPException(status_code=404, detail=f"No data or insights found for {data_source}. Run the scheduler to populate data.")

            response_data = {
                "data": data_result['data'],
                "insights": insights_result['insights'] if insights_result else "No insights were generated for this data source. Please check the scheduler logs."
            }
            
            # For Plaid, the frontend expects news data. We will fetch this from the 'openbb' source.
            if data_source == 'plaid':
                if IS_DEBUG:
                    print(f"  [API] Plaid requested. Fetching supplementary news data from 'openbb' source...")
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
                    if IS_DEBUG:
                        print("  [API] Successfully merged news data into Plaid response.")
                else:
                    if IS_DEBUG:
                        print("  [API] No news data found for 'openbb' to supplement Plaid response.")


            if IS_DEBUG:
                print(f"--- ✅ [API] Sending successful response for '{data_source}' ---")
            return response_data

    except Exception as e:
        if IS_DEBUG:
            print(f"--- ❌ [API] An unexpected error occurred: {e} ---")
        print(f"🔴 [DB] Error fetching data from database: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching data: {str(e)}")
    finally:
        if db_conn:
            db_conn.close()
            if IS_DEBUG:
                print("🔒 [DB] Database connection closed.")


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# --- Static Files Mounting ---

# Determine the correct path to the 'out' directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, "out")
if not os.path.isdir(static_files_dir):
    static_files_dir = os.path.join(os.path.dirname(current_dir), "out")

if os.path.isdir(static_files_dir):
    app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
    print(f"🟢 [FastAPI] Serving static files from: {static_files_dir}")
else:
    print(f"🟡 [FastAPI] Warning: Static files directory not found at '{static_files_dir}'. The frontend will not be served.")
