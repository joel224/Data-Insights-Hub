# Stage 1: Build the Next.js frontend
FROM node:20-slim AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# Stage 2: Setup the Python environment
FROM python:3.11-slim
WORKDIR /app

# Copy built frontend from build-stage
COPY --from=build-stage /app/out ./out
COPY --from=build-stage /app/node_modules ./node_modules
COPY --from=build-stage /app/package*.json ./
COPY --from=build-stage /app/.next ./.next
COPY --from=build-stage /app/public ./public
COPY --from=build-stage /app/src/ai ./src/ai

# Install Python dependencies
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy Python backend code
COPY python-backend/ ./python-backend/

# Copy other necessary files
COPY Procfile .
COPY next.config.ts .

EXPOSE 8080 8000 3400

# Use honcho to run multiple processes from the Procfile
RUN pip install honcho
CMD ["honcho", "start"]
