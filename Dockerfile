# Simple Dockerfile for Render deployment
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend code
COPY backend/ ./backend/

# Install dependencies
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE $PORT

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
