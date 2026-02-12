FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory
RUN mkdir -p /home/claude/talentdog/database

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "main.py"]
