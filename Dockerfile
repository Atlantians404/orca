FROM python:3.12-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Make Python output appear immediately in Render logs
ENV PYTHONUNBUFFERED=1

# Application directory
WORKDIR /app

# Copy requirements first for Docker layer caching
COPY backend/requirements.txt ./backend/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy the entire project
COPY . .

# Make project modules importable
ENV PYTHONPATH=/app

# Render provides the PORT environment variable
EXPOSE 10000

# Start FastAPI
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}"]