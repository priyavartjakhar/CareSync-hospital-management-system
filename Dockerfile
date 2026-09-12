FROM python:3.10-slim

# Install system dependencies (Node.js & npm for building Vue frontend)
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install frontend dependencies and build SPA
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install

COPY . .
RUN cd frontend && npm run build && mkdir -p dist && cp -r frontend/dist/* dist/

# Expose production port
EXPOSE 7860

# Run Flask WSGI server with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "backend.app:create_app()"]
