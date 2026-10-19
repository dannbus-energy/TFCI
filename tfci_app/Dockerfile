FROM python:3.14-slim

WORKDIR /app

# Install system dependencies for psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY tfci_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (engine, data, api, etc.)
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "tfci_app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
