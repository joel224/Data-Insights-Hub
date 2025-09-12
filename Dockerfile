# Stage 1: Build the Next.js frontend
FROM node:20-slim AS build-stage
WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy the rest of the application
COPY . .

# Build the Next.js application
RUN npm run build

# Stage 2: Create the final Python image
FROM python:3.11-slim
WORKDIR /app

# Copy the built Next.js app from the build stage
COPY --from=build-stage /app/out ./out

# Copy Python backend files
COPY python-backend/ ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 for the FastAPI backend
EXPOSE 8000

# Set the command to run the Python backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
