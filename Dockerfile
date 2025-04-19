# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Run the Django app (update if using different entry point)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
