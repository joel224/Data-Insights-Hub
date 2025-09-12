# Use an official lightweight Python image.
FROM python:3.11-slim

# Set the working directory in the container.
WORKDIR /app

# Set the PYTHONPATH to ensure modules are found correctly.
ENV PYTHONPATH=/app

# Copy only the Python backend code and its requirements.
COPY ./python-backend/requirements.txt /app/python-backend/requirements.txt
COPY ./python-backend /app/python-backend

# Install the Python dependencies.
RUN pip install --no-cache-dir -r /app/python-backend/requirements.txt

# Expose the port the app runs on.
EXPOSE 8000

# Define the command to run the application.
# This tells uvicorn to look for the 'app' object in the 'main.py' file
# inside the 'python-backend' directory.
CMD ["uvicorn", "python-backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
