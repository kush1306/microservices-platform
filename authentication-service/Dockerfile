# ---- Base Image ----
FROM python:3.11-slim

# ---- Working directory ----
WORKDIR /app

# ---- Install Python dependencies first (better layer caching) ----
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---- Copy code ----
COPY . .

# ---- Expose Streamlit's default port ----
EXPOSE 8000

# ---- Start command ----
# Update "app.py" if your main Streamlit file has a different name
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
