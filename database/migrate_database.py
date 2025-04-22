# database/migrate_database.py
import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Step 4: Reapply performance pragmas
cursor.execute("PRAGMA journal_mode=WAL")
cursor.execute("PRAGMA synchronous=NORMAL")
cursor.execute("PRAGMA cache_size=-20000")


# Step 1: Migrate the faqs table to add a category column
# Create a new faqs table with the additional column
cursor.execute("""
    CREATE TABLE IF NOT EXISTS faqs_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL UNIQUE,
        response TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'General'
    )
""")

# Copy data from the old faqs table to the new one
cursor.execute("""
    INSERT OR IGNORE INTO faqs_new (id, query, response, category)
    SELECT id, query, response, 'General' AS category
    FROM faqs
""")

# Drop the old faqs table and rename the new one
cursor.execute("DROP TABLE faqs")
cursor.execute("ALTER TABLE faqs_new RENAME TO faqs")

# Recreate the index on the new faqs table
cursor.execute("CREATE INDEX IF NOT EXISTS idx_query ON faqs (LOWER(query))")

# Step 2: Create a users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        preferred_language TEXT DEFAULT 'en',
        created_at TEXT NOT NULL
    )
""")

# Step 3: Create a conversations table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        query TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
""")

# Create indexes for the new tables
cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users (user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations (user_id)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations (timestamp)")


# Commit changes and close the connection
conn.commit()
conn.close()

print("Database migration complete. Added category column to faqs, created users and conversations tables, and set indexes.")