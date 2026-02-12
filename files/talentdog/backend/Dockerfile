# Start vanaf lichtgewicht Python image
FROM python:3.11-slim

WORKDIR /app

# Installeer dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopieer alle backend bestanden
COPY . .

# Zorg dat database map bestaat
RUN mkdir -p /home/claude/talentdog/database

# Expose poort 8000 zodat Railway weet waar het op luistert
EXPOSE 8000

# Healthcheck zodat Railway weet wanneer container klaar is
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s \
  CMD curl -f http://localhost:8000/ || exit 1

# Start FastAPI met uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
