FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/app.py .
COPY backend_files/ ./backend_files/
EXPOSE 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "app:superkart_api"]
