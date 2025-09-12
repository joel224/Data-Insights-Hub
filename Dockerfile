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

# Install Node.js and npm into the Python image
# This is necessary to run the Next.js server
ENV NODE_VERSION=20.11.1
RUN apt-get update && \
    apt-get install -y curl && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash && \
    . ~/.nvm/nvm.sh && \
    nvm install ${NODE_VERSION} && \
    nvm use ${NODE_VERSION} && \
    nvm alias default ${NODE_VERSION} && \
    npm install -g npm@latest && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin:${PATH}"


# Set the PORT environment variable for Railway
# The `web` process in the Procfile will use this.
ENV PORT=3000

# Copy and install Python dependencies
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
COPY --from=build-stage /app/node_modules ./node_modules


# Define the command to run BOTH applications using honcho
# Honcho will read the Procfile and start the web and api services.
CMD ["honcho", "start"]
