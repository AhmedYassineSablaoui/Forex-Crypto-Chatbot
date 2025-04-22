# database/check_faq_categories.py
import sqlite3
import pandas as pd

conn = sqlite3.connect("chatbot.db")
df = pd.read_sql_query("SELECT query, category FROM faqs", conn)
conn.close()
print(df)