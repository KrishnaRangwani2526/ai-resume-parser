# ----------------------------
# 🐍 Base Image
# ----------------------------
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ----------------------------
# 📦 Install dependencies
# ----------------------------
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# (Optional) Download SpaCy model
RUN python -m spacy download en_core_web_sm || true

# ----------------------------
# 🧠 Copy source code
# ----------------------------
COPY . .

# ----------------------------
# ⚙️ Environment Variables
# ----------------------------
ENV PYTHONUNBUFFERED=1

# ----------------------------
# 🚀 Run FastAPI app
# ----------------------------
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
