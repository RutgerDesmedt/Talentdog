# Gebruik Python slim image
FROM python:3.11-slim

# Werkdirectory
WORKDIR /app

# Installeer dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer backend code
COPY . .

# Zorg dat de database map bestaat
RUN mkdir -p /home/claude/talentdog/database

# EXPOSE poort die FastAPI gebruikt
EXPOSE 8000

# Start FastAPI via uvicorn (dit is cruciaal)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
