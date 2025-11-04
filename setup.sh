#!/bin/bash
set -e  # stop script if any command fails

echo "🚀 Starting setup for Resume Parser API..."

# ----------------------------
# 1️⃣ Create and activate virtual environment
# ----------------------------
if [ ! -d "venv" ]; then
  echo "🧱 Creating virtual environment..."
  python3 -m venv venv
else
  echo "✅ Virtual environment already exists."
fi

source venv/bin/activate
echo "✅ Virtual environment activated."

# ----------------------------
# 2️⃣ Install dependencies
# ----------------------------
if [ -f "requirements.txt" ]; then
  echo "📦 Installing dependencies..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "⚠️ requirements.txt not found! Please ensure it's present."
  exit 1
fi

# ----------------------------
# 3️⃣ Setup PostgreSQL database
# ----------------------------
echo "🗄️ Setting up PostgreSQL database..."

DB_NAME="resume_parser_db"
DB_USER="${DB_USER:-postgres}"
DB_HOST="${DB_HOST:-localhost}"

# Create database if it doesn't exist
if ! psql -U "$DB_USER" -h "$DB_HOST" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
  echo "🧩 Creating database: $DB_NAME"
  createdb -U "$DB_USER" -h "$DB_HOST" "$DB_NAME"
else
  echo "✅ Database $DB_NAME already exists."
fi

# Apply schema migrations
echo "📜 Applying schema migrations..."
psql -U "$DB_USER" -h "$DB_HOST" -d "$DB_NAME" -f migrations/001_create_resume_schema.sql

# ----------------------------
# 4️⃣ Create uploads directory
# ----------------------------
mkdir -p uploads
echo "📂 Uploads folder ready."

# ----------------------------
# 5️⃣ Run the FastAPI app
# ----------------------------
echo "🚀 Setup complete! Starting FastAPI server..."
uvicorn src.main:app --reload
