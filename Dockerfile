# Use a lightweight official Python 3 image
FROM python:3.11-slim

# Set the working directory inside the container to where the app lives
WORKDIR /usr/src/app/python-backend

# Copy the requirements file and install dependencies
# This caches the dependency installation step
COPY python-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the working directory
COPY python-backend/ .

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Define the command to run your application from the WORKDIR
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
