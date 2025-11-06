# Use Python official image as base
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy the Python script
COPY app.py .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the script when container starts
CMD ["python", "app.py"]