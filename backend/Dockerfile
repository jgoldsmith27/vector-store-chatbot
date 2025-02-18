# Use a Python base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt first to install dependencies
COPY src/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend app files into the container
COPY src/ .

# Expose the port that the Python app will run on (e.g., 8080)
EXPOSE 8080

# Start the Python app using FastAPI
CMD ["python", "src/main.py"]
