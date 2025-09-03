import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env file
load_dotenv()

# Read DATABASE_URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

engine = create_engine(DATABASE_URL, echo=True)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        print("✅ Database connection works, result:", result)
except Exception as e:
    print("❌ Database connection failed:", e)

