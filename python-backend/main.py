
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

# --- Database Connection and Schema Setup ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    DATABASE_URL = os.getenv("DATABASE_URL")
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

def create_schema(connection):
    """Creates the necessary tables if they don't exist."""
    if not connection:
        print("🔴 Cannot create schema, no database connection.")
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
        print("🟢 Schema checked/created successfully.")
    except Exception as e:
        print(f"🔴 Error creating schema: {e}")
        connection.rollback()


# --- FastAPI App Lifespan (for startup events) ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    print("🚀 Application starting up...")
    db_conn = get_db_connection()
    if db_conn:
        create_schema(db_conn)
        db_conn.close()
    else:
        print("🔴 Database connection failed on startup. Schema not created.")
    yield
    # On shutdown
    print("👋 Application shutting down...")


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
    print(f"Received request for latest '{data_source}' data and insights.")
    
    if data_source not in ["plaid", "clearbit", "openbb"]:
        raise HTTPException(status_code=400, detail="Invalid data source")

    db_conn = get_db_connection()
    if not db_conn:
        raise HTTPException(status_code=500, detail="Database connection not configured. Please ensure DATABASE_URL is set in Railway.")

    try:
        with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Fetch raw data
            print(f"🔍 [DB] Fetching raw data for '{data_source}'...")
            cur.execute("""
                SELECT data
                FROM api_data
                WHERE api_name = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            data_result = cur.fetchone()
            print(f"✅ [DB] Raw data result: {'Found' if data_result else 'Not Found'}")


            # Fetch insights
            print(f"🔍 [DB] Fetching insights for '{data_source}'...")
            cur.execute("""
                SELECT insights
                FROM daily_recommendations
                WHERE data_source = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            insights_result = cur.fetchone()
            print(f"✅ [DB] Insights result: {'Found' if insights_result else 'Not Found'}")

            # If no data and no insights are found, then we have a problem.
            if not data_result and not insights_result:
                raise HTTPException(status_code=404, detail=f"No data or insights found for {data_source}. Run the scheduler to populate data.")

            # Build a flexible response.
            response_data = {
                "data": data_result['data'] if data_result else None,
                "insights": insights_result['insights'] if insights_result else None
            }

            print(f"📦 [API] Sending response for '{data_source}'.")
            return response_data

    except Exception as e:
        print(f"🔴 Error fetching data from database: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching data: {str(e)}")
    finally:
        if db_conn:
            db_conn.close()


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

# --- Static Files Mounting ---

# Determine the correct path to the 'out' directory.
# When running locally from `python-backend`, it's one level up.
# In the Docker container, it's in the same directory.
current_dir = os.path.dirname(os.path.abspath(__file__))
static_files_dir = os.path.join(current_dir, "out")

# If 'out' is not in the current directory, check the parent directory.
if not os.path.isdir(static_files_dir):
    static_files_dir = os.path.join(os.path.dirname(current_dir), "out")

# Check if the directory exists before mounting.
if os.path.isdir(static_files_dir):
    app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
    print(f"🟢 Serving static files from: {static_files_dir}")
else:
    print(f"🟡 Warning: Static files directory not found at '{static_files_dir}'. The frontend will not be served.")
