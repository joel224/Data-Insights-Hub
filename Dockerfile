# Use a lightweight official Python 3 image
FROM python:3.11-slim

# Set the working directory for the python backend
WORKDIR /app/python-backend

# Copy just the requirements file to leverage Docker layer caching
COPY python-backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY python-backend/ .

# Define the command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
