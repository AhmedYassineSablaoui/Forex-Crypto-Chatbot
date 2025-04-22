# database/add_missing_faqs.py
import sqlite3
from pathlib import *
import os



# Set base directory to the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Define file paths

DB_PATH = BASE_DIR / "database" / "chatbot.db"

# Define responses for the missing FAQs
# Replace these with the actual responses you want to use
new_faqs = [
    (
        "What’s the dealio with Crypto staking, fam?",
        "Crypto staking is when you lock up your coins in a wallet to help secure a blockchain network, like for validating transactions. In return, you earn rewards—kinda like interest, fam! It’s a way to make passive income, but you gotta pick a solid coin and watch out for risks like price drops."
    ),
    (
        "How do I flex my cash on Ethereum, yo?",
        "To invest in Ethereum, you can buy Ether (ETH) on an exchange like Binance or Coinbase—set up a wallet first, deposit some cash, and trade for ETH. You can also flex by getting into Ethereum-based projects like NFTs or DeFi apps, but yo, always watch out for gas fees and market volatility!"
    ),
    (
        "Bro, how do I get into Forex trading without getting rekt?",
        "To start Forex trading without getting rekt, bro, learn the basics first—stuff like pips, leverage, and spreads. Use a demo account to practice, pick a legit broker with low fees, and start with small trades. Risk management is key: don’t over-leverage, set stop-loss orders, and never trade with money you can’t afford to lose!"
    ),
    # Add more FAQs and responses as needed based on the output of check_missing_faqs.py
]

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Insert the new FAQs into the database
for query, response in new_faqs:
    cursor.execute(
        "INSERT OR IGNORE INTO faqs (query, response) VALUES (?, ?)",
        (query, response)
    )

# Commit changes and close the connection
conn.commit()
conn.close()

print(f"Added {len(new_faqs)} new FAQs to the database.")