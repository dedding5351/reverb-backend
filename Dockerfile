FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run sets PORT env var, default 8080)
ENV PORT=8080

# Run the application
# We use shell form to allow variable expansion for $PORT
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
