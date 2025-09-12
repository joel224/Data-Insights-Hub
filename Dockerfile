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

# Set the PORT environment variable for Railway
ENV PORT=8000

# Copy and install Python dependencies from the python-backend directory
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python backend code
COPY python-backend/ ./python-backend/

# Copy the built Next.js static site from the build stage
COPY --from=build-stage /app/out ./out

# Copy the Genkit flow to be accessible by the python backend
COPY src/ai/flows/generate-data-insights.ts ./src/ai/flows/generate-data-insights.ts
COPY src/ai/genkit.ts ./src/ai/genkit.ts

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the FastAPI application
CMD ["uvicorn", "python-backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
