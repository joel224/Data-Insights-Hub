
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
            cur.execute("""
                SELECT data
                FROM api_data
                WHERE api_name = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            data_result = cur.fetchone()

            # Fetch insights
            cur.execute("""
                SELECT insights
                FROM daily_recommendations
                WHERE data_source = %s
                ORDER BY timestamp DESC
                LIMIT 1;
            """, (data_source,))
            insights_result = cur.fetchone()

            if not data_result or not insights_result:
                raise HTTPException(status_code=404, detail=f"No data or insights found for {data_source}. Run the scheduler to populate data.")

            return {
                "data": data_result['data'],
                "insights": insights_result['insights']
            }

    except Exception as e:
        print(f"🔴 Error fetching data from database: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching data: {str(e)}")
    finally:
        if db_conn:
            db_conn.close()


@app.get("/api")
def read_root():
    return {"message": "Data Insights Hub Python backend is running."}

app.mount("/", StaticFiles(directory="out", html=True), name="static")

    