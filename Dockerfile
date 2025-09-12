# Use a lightweight official Python 3 image
FROM python:3.11-slim

# Set the working directory to the python-backend folder
WORKDIR /app/python-backend

# Copy just the requirements file first to leverage Docker layer caching
COPY python-backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the python-backend application code
COPY python-backend/ .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application.
# This runs the 'app' instance from the 'main.py' file.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
