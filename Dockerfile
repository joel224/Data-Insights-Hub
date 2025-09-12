# Use a lightweight official Python 3 image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY python-backend/requirements.txt ./python-backend/
RUN pip install --no-cache-dir -r ./python-backend/requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port Uvicorn will listen on
EXPOSE 8000

# Define the command to run your application, explicitly using port 8000
CMD ["uvicorn", "python-backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
