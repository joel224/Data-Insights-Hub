# --- Stage 1: Build the Next.js frontend ---
FROM node:20-slim AS build-stage
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy all source files
COPY . .

# Build the Next.js app
RUN npm run build

# --- Stage 2: Setup the Python backend and final image ---
FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies first
COPY python-backend/requirements.txt ./python-backend/requirements.txt
RUN pip install --no-cache-dir -r python-backend/requirements.txt

# Copy the Python backend code
COPY python-backend/ ./python-backend/

# Copy the Procfile for running multiple processes
COPY Procfile ./

# Copy built Next.js app from the build stage
COPY --from=build-stage /app/.next ./.next
COPY --from=build-stage /app/public ./public
COPY --from=build-stage /app/package.json ./package.json
COPY --from=build-stage /app/next.config.ts ./next.config.ts

# Define the command to run both services
CMD ["honcho", "start"]
