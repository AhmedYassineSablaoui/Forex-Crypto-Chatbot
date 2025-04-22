# database/check_missing_faqs.py
from pathlib import Path
import sqlite3
import pandas as pd

# Set base directory to the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Define file paths
CSV_PATH = BASE_DIR / "backend" / "faq_data_cleaned.csv"
DB_PATH = BASE_DIR / "database" / "chatbot.db"

# Load CSV and normalize FAQ queries (label == 1)
faq_df = pd.read_csv(CSV_PATH, encoding="utf-8")
faq_df = faq_df[faq_df["label"] == 1]
faq_df["normalized_query"] = faq_df["text"].str.lower().str.strip()

# Connect to the DB and fetch existing queries
with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT query FROM faqs")
    existing_queries = {row[0].lower().strip() for row in cursor.fetchall()}

# Identify missing queries
missing_faqs = faq_df[~faq_df["normalized_query"].isin(existing_queries)]["text"].tolist()

# Print missing ones
print(f"Found {len(missing_faqs)} FAQ queries missing from the database:")
for query in missing_faqs:
    print(f"- {query}")
