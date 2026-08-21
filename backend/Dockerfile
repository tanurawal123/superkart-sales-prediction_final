# ------------------------------------------------------------------------------
# Flask backend image
# Build from the REPO ROOT so this Dockerfile can see backend_files/, e.g.:
#   docker build -t superkart-backend -f backend/Dockerfile .
# ------------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and the serialized model
COPY backend/app.py .
COPY backend_files/ ./backend_files/

EXPOSE 7860

CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "app:superkart_api"]
