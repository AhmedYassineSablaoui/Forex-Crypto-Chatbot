# backend/check_faq_table.py
import sqlite3
import pandas as pd

conn = sqlite3.connect("chatbot.db")
df = pd.read_sql_query("SELECT * FROM faqs ORDER BY id DESC LIMIT 5", conn)
conn.close()
print(df)