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


# --- Stage 2: Setup the final production image with both Python and Node.js ---
FROM python:3.11-slim
WORKDIR /app

# Install Node.js and npm
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python backend code
COPY python-backend/ ./python-backend/

# Copy the Procfile for honcho
COPY Procfile ./Procfile

# Copy the built Next.js application and its dependencies from the build stage
COPY --from=build-stage /app/.next ./.next
COPY --from=build-stage /app/package.json ./package.json
COPY --from=build-stage /app/next.config.ts ./next.config.ts
COPY --from=build-stage /app/node_modules ./node_modules

# Define the command to run BOTH applications using honcho
# Honcho will read the Procfile and start the web and api services.
CMD ["honcho", "start"]
