# --- Stage 1: Build the Next.js frontend ---
FROM node:20-slim as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# --- Stage 2: Setup the final production image ---
FROM python:3.11-slim
WORKDIR /app

# Copy built frontend from the build stage
COPY --from=build-stage /app/out ./out

# Install Python dependencies
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend code
COPY python-backend/ ./python-backend/

# Expose the port the app runs on
EXPOSE 8000

# Start the application using a shell
CMD exec uvicorn python-backend.main:app --host 0.0.0.0 --port 8000
