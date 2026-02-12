# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependencies installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code kopiëren
COPY . .

# Database folder aanmaken
RUN mkdir -p /home/claude/talentdog/database

# Expose poort 8000
EXPOSE 8000

# Start de FastAPI app met Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
