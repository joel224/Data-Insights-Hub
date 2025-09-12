# --- Stage 1: Build the Next.js frontend ---
FROM node:20-slim AS build-stage
WORKDIR /app

# Copy package manager files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy the rest of the Next.js app source code
COPY . .

# Build the Next.js app
RUN npm run build


# --- Stage 2: Setup the final production image ---
FROM python:3.11-slim
WORKDIR /app

# Set the PORT environment variable for Railway
# The `web` process in the Procfile will use this.
ENV PORT=3000

# Copy and install Python dependencies from the python-backend directory
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python backend code
COPY python-backend/ ./python-backend/

# Copy the Procfile for honcho
COPY Procfile ./Procfile

# Copy the built Next.js application from the build stage
COPY --from=build-stage /app/.next ./.next
COPY --from=build-stage /app/package.json ./package.json
COPY --from=build-stage /app/next.config.ts ./next.config.ts

# Create an empty public directory and then copy into it.
# This prevents the build from failing if the source /app/public doesn't exist.
RUN mkdir -p ./public
COPY --from=build-stage --chown=nonroot:nonroot /app/public ./public

# Define the command to run BOTH applications using honcho
# Honcho will read the Procfile and start the web and api services.
CMD ["honcho", "start"]
