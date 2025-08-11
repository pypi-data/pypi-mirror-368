FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy NovaLang source code
COPY . .

# Create non-root user
RUN useradd -m -u 1001 novalang
RUN chown -R novalang:novalang /app
USER novalang

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py", "--file", "src/main/nova/Application.nova"]
