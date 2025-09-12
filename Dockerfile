# --- Stage 1: Build the Next.js frontend ---
FROM node:20-slim AS build-stage
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
RUN npm run build

# --- Stage 2: Build the FastAPI backend ---
FROM python:3.11-slim
WORKDIR /app

# Copy python requirements and install
COPY python-backend/requirements.txt ./python-backend/requirements.txt
RUN pip install --no-cache-dir -r python-backend/requirements.txt

# Copy python backend code
COPY python-backend/ ./python-backend/

# Copy the built Next.js frontend from the build stage
COPY --from=build-stage /app/out ./out

WORKDIR /app/python-backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
