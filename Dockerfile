FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for oracledb
RUN apt-get update && apt-get install -y \
    libaio1t64 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure wallet directory has correct permissions
RUN chmod -R 755 /app/wallet

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
