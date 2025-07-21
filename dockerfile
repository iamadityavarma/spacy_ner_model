
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (if needed for spacy)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY app/ app/
COPY models/ models/
COPY app/customCorpus.pkl app/customCorpus.pkl

# Expose the port Flask runs on
EXPOSE 5000

# Set the entrypoint
CMD ["python", "app/main.py"]

