FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source and config
COPY src/ /app/src/
COPY config/ /app/config/

# Create directory for uploads
RUN mkdir -p /app/uploads

# Environment
ENV PYTHONPATH=/app
ENV UPLOAD_FOLDER=/app/uploads

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]