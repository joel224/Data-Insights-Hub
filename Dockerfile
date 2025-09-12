# Stage 1: Build the Next.js application
FROM node:20-slim as build-stage
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# Stage 2: Create the final production image
FROM python:3.11-slim
WORKDIR /app

# Install Node.js
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built Next.js app from the build stage
COPY --from=build-stage /app/.next ./.next
COPY --from=build-stage /app/public ./public

# Expose the default Next.js port and the API port
EXPOSE 3000 8000 3400

# Use honcho to run the Procfile
# honcho is installed via requirements.txt
CMD ["honcho", "start"]
