from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
print("DB_URL:", DB_URL)

try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("Connection successful:", result.scalar())
except Exception as e:
    print("Connection failed:", e)