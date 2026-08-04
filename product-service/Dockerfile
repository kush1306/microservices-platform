# ---- Base Image ----
FROM python:3.11-slim

# ---- Working Directory ----
WORKDIR /app

# ---- Install Dependencies ----
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- Copy Source Code ----
COPY . .

# ---- Expose Port ----
EXPOSE 8000

# ---- Start command ----
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
