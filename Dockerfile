# --- Stage 1: Build the Next.js frontend ---
FROM node:20-slim AS build-stage
WORKDIR /app

# Copy package manager files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy the rest of the Next.js app source code
COPY . .

# Build the Next.js app for static export
RUN npm run build

# --- Stage 2: Build the FastAPI backend ---
FROM python:3.11-slim
WORKDIR /app

# Copy and install Python dependencies
COPY python-backend/requirements.txt ./python-backend/requirements.txt
RUN pip install --no-cache-dir -r ./python-backend/requirements.txt

# Copy the FastAPI backend code
COPY python-backend/ ./python-backend/

# Copy the built Next.js frontend from the build stage
COPY --from=build-stage /app/out ./out

# Set the working directory for the python app
WORKDIR /app/python-backend

# Define the command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
