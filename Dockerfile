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

# --- Stage 2: Setup the final production image ---
FROM python:3.11-slim
WORKDIR /app

# Copy and install Python dependencies
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python backend code
COPY python-backend/ ./python-backend/

# Copy the statically built Next.js application from the build stage
COPY --from=build-stage /app/out ./out

# Expose the port Uvicorn will listen on
# Railway's $PORT variable will be used automatically.
EXPOSE 8000

# Define the command to run the Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "python-backend"]
