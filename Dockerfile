# Use an official Node.js runtime as a parent image
FROM node:20-slim as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# Use a Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the built Next.js app from the build stage
COPY --from=build-stage /app/out ./out

# Copy Python backend files
COPY python-backend/ ./

# Install system dependencies needed for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the FastAPI backend
EXPOSE 8000

# Run the backend server
CMD ["honcho", "start"]
