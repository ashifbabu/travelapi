# Use lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (including the app/ folder)
COPY . .

# Expose the port
EXPOSE 8000

# Run Gunicorn with Uvicorn workers and increased timeout
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "300"]
