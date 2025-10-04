FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Create working dir
WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Use eventlet for SocketIO (important for async)
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "-b", "0.0.0.0:8000", "run:app", "--keyfile", "/app/certs/key.pem", "--certfile", "/app/certs/cert.pem"]
