# database/add_new_faqs.py
import sqlite3
import pandas as pd

# Path to the new FAQs CSV file
NEW_FAQS_PATH = "new_faqs.csv"

# Connect to the database
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Load the new FAQs from the CSV file
try:
    df = pd.read_csv(NEW_FAQS_PATH, encoding="utf-8")
    if not all(col in df.columns for col in ["query", "response", "category"]):
        raise ValueError("new_faqs.csv must contain 'query', 'response', and 'category' columns")
except FileNotFoundError:
    print(f"Error: {NEW_FAQS_PATH} not found.")
    exit(1)
except Exception as e:
    print(f"Error loading {NEW_FAQS_PATH}: {str(e)}")
    exit(1)

# Insert new FAQs into the database
for _, row in df.iterrows():
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO faqs (query, response, category) VALUES (?, ?, ?)",
            (row["query"], row["response"], row["category"])
        )
    except sqlite3.Error as e:
        print(f"Error inserting FAQ '{row['query']}': {str(e)}")

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Added {len(df)} new FAQs to the database.")