# --- Stage 1: Build the Next.js frontend ---
FROM node:20-slim AS build-stage
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

# --- Stage 2: Setup the final production image ---
FROM python:3.11-slim
WORKDIR /app
COPY --from=build-stage /app/out ./out
COPY python-backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY python-backend/ ./python-backend/

# Copy the .env file to the final image
COPY .env ./.env

CMD ["uvicorn", "python-backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
