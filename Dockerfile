FROM python:3.9-slim

WORKDIR /app

# Copy req and install dependencies 
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PERFECT_CLOUD_ENVIRONMENT=true

# Expose the application port
EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]