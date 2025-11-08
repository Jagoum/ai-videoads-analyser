FROM python:3.9-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY src/ ./src/
COPY config/ ./config/

# Create directory for uploads
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONPATH=/app
ENV UPLOAD_FOLDER=/app/uploads

# Expose backend port
EXPOSE 8000

# Start backend service
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend build stage
FROM node:16 as frontend-build

WORKDIR /app

# Copy frontend dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend code
COPY frontend/ ./

# Build frontend
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy frontend build
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose frontend port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]