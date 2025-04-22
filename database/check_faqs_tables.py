# backend/check_faq_table.py
import sqlite3
import pandas as pd
from pathlib import Path

# Set base directory to the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Define file paths

DB_PATH = BASE_DIR / "database" / "chatbot.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM faqs", conn)
conn.close()
print(f"Total FAQs in the database: {len(df)}")
print(df[["query", "response"]].head())