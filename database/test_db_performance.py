# backend/test_db_performance.py
import sqlite3
import time

# Connect to the database
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Test FAQ lookup
start_time = time.time()
cursor.execute("SELECT response FROM faqs WHERE LOWER(query) = ?", ("what is the difference between bitcoin and ethereum?",))
result = cursor.fetchone()
end_time = time.time()
print(f"FAQ lookup time: {(end_time - start_time) * 1000:.2f} ms")
print(f"Result: {result[0] if result else 'Not found'}")

# Test log retrieval by timestamp
start_time = time.time()
cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 5")
rows = cursor.fetchall()
end_time = time.time()
print(f"Log retrieval time (by timestamp): {(end_time - start_time) * 1000:.2f} ms")
print(f"Retrieved {len(rows)} log entries")

# Test log update by query
start_time = time.time()
cursor.execute(
    "UPDATE logs SET feedback = ? WHERE query = ?",
    ("yes", "what is Forex?")
)
conn.commit()
end_time = time.time()
print(f"Log update time (by query): {(end_time - start_time) * 1000:.2f} ms")

# Close the connection
conn.close()