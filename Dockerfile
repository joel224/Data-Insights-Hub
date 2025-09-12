# Use a lightweight official Python 3 image
FROM python:3.11-slim

# Set the working directory to the Python app's folder
WORKDIR /usr/src/app

# Copy the requirements file first to leverage Docker layer caching
COPY ./python-backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python backend code into the working directory
COPY ./python-backend/ .

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Define the command to run the application from the working directory
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
