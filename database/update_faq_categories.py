# database/update_faq_categories.py
import sqlite3

# Connect to the database
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Update categories based on keywords
# Forex-related FAQs
cursor.execute("""
    UPDATE faqs
    SET category = 'Forex'
    WHERE LOWER(query) LIKE '%forex%'
       OR LOWER(query) LIKE '%leverage forex%'
       OR LOWER(query) LIKE '%tnd to usd%'
       OR LOWER(query) LIKE '%tunisian festival%'
       OR LOWER(query) LIKE '%eur/usd%'
""")

# Crypto-related FAQs
cursor.execute("""
    UPDATE faqs
    SET category = 'Crypto'
    WHERE LOWER(query) LIKE '%bitcoin%'
       OR LOWER(query) LIKE '%ethereum%'
       OR LOWER(query) LIKE '%crypto%'
       OR LOWER(query) LIKE '%staking%'
       OR LOWER(query) LIKE '%nft%'
       OR LOWER(query) LIKE '%metaverse%'
       OR LOWER(query) LIKE '%stablecoins%'
       OR LOWER(query) LIKE '%quantum computing%'
""")

# General category (already set as default, but ensure others are not overwritten)
cursor.execute("""
    UPDATE faqs
    SET category = 'General'
    WHERE category = 'General'
      AND id NOT IN (
          SELECT id FROM faqs WHERE category IN ('Forex', 'Crypto')
      )
""")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Updated FAQ categories in the database.")