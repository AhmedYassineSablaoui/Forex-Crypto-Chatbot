import sqlite3
import pandas as pd 



# Connect to SQLite database (creates a new database if it not exist )

conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Optimize SQLite performance with pragmas
cursor.execute("PRAGMA journal_mode=WAL")  # Use Write-Ahead Logging for better concurrency
cursor.execute("PRAGMA synchronous=NORMAL")  # Balance speed and safety
cursor.execute("PRAGMA cache_size=-20000")  # Increase cache size (20,000 pages)

# Create FAQs table 

cursor.execute( """
    CREATE TABLE IF NOT EXISTS faqs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL UNIQUE,
        response TEXT NOT NULL
        )
""")

#Create logs table for user interactions and feedbacks 

cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        query TEXT NOT NULL,
        label TEXT NOT NULL,
        confidence REAL NOT NULL,
        response TEXT NOT NULL,
        feedback TEXT
    )
""")

# Create an index on LOWER(query) for faster case-insensitive lookups
cursor.execute("CREATE INDEX IF NOT EXISTS idx_query ON faqs (LOWER(query))")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs (timestamp)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_query ON logs (query)")

# Populate the FAQs table with data from faq_responses.py

faq_data = [
    ("What is the difference between Bitcoin and Ethereum?", "Bitcoin is primarily a store of value and digital currency, while Ethereum is a platform for smart contracts and decentralized applications (dApps). Ethereum also uses Ether as its native cryptocurrency."),
    ("How do I start trading Forex with a small budget?", "You can start trading Forex with a small budget by choosing a broker with low minimum deposits, using a demo account to practice, and starting with micro-lots to minimize risk."),
    ("What are the risks of using leverage in Crypto trading?", "Using leverage in Crypto trading can amplify both gains and losses. Risks include high volatility, margin calls, and potential liquidation of your position if the market moves against you."),
    ("Explain the concept of staking in Crypto.", "Staking in Crypto involves locking up your coins in a wallet to support the network's operations, such as validating transactions. In return, you earn rewards, typically in the form of additional coins."),
    ("Can the price of Ethereum influence the stock market?", "Yes, the price of Ethereum can influence the stock market indirectly, especially for companies involved in blockchain technology or those heavily invested in cryptocurrencies."),
    ("What is the relationship between olive oil prices and Forex markets?", "Olive oil prices can affect Forex markets by influencing the economies of major olive oil-producing countries (e.g., Spain, Italy). Changes in these economies can impact their currencies' exchange rates."),
    ("Forex?", "Forex, or foreign exchange, refers to the global marketplace for trading national currencies against one another. It's the largest financial market in the world, used for trading, hedging, and speculation."),
    ("leverage forex how???", "Leverage in Forex allows you to control a larger position with a smaller amount of capital. For example, with 50:1 leverage, you can control $50,000 with just $1,000. However, it increases both potential profits and risks."),
    ("What is the impact of quantum computing on Crypto security?", "Quantum computing could potentially break current cryptographic algorithms used in Crypto, such as SHA-256 or ECDSA, making some blockchains vulnerable. However, quantum-resistant algorithms are being developed to mitigate this risk."),
    ("How does the metaverse affect NFT trading?", "The metaverse increases demand for NFTs by enabling virtual ownership of digital assets like land, avatars, and art, which can be traded in virtual worlds, driving up NFT trading activity."),
    ("What are the latest regulations on stablecoins in the EU?", "As of 2025, the EU has implemented the Markets in Crypto-Assets (MiCA) regulation, which requires stablecoin issuers to maintain reserves, ensure transparency, and comply with anti-money laundering rules."),
    ("Can AI predict Forex market trends accurately?", "AI can predict Forex market trends with some accuracy by analyzing historical data, news, and market sentiment. However, it's not foolproof due to the market's volatility and unpredictable events."),
    ("Qu'est-ce que le trading Forex ?", "Le trading Forex consiste à acheter et vendre des devises sur le marché des changes pour profiter des variations de taux de change. C'est le plus grand marché financier au monde."),
    ("Comment fonctionne le staking en Crypto ?", "Le staking en Crypto consiste à verrouiller vos pièces dans un portefeuille pour soutenir les opérations du réseau, comme la validation des transactions. En retour, vous recevez des récompenses sous forme de pièces supplémentaires."),
    ("ما هي مخاطر الرافعة المالية في تداول العملات الرقمية؟", "استخدام الرافعة المالية في تداول العملات الرقمية يمكن أن يزيد من الأرباح والخسائر على حد سواء. المخاطر تشمل التقلبات العالية، وطلبات الهامش، والتصفية المحتملة لمركزك إذا تحرك السوق ضدك."),
    ("ما هو تداول الفوركس؟", "تداول الفوركس هو شراء وبيع العملات الأجنبية في سوق الصرف الأجنبي للاستفادة من تقلبات أسعار الصرف. إنه أكبر سوق مالي في العالم."),
    ("Wht is Cryto tradng?", "Crypto trading involves buying and selling cryptocurrencies like Bitcoin and Ethereum on exchanges to profit from price movements. It can be highly volatile but offers opportunities for gains."),
    ("¿Qué es el trading de Forex?", "El trading de Forex consiste en comprar y vender divisas en el mercado de cambios para aprovechar las variaciones en los tipos de cambio. Es el mercado financiero más grande del mundo."),
    ("¿Qué es el staking en Cripto?", "El staking en criptomonedas implica bloquear tus monedas en una billetera para apoyar las operaciones de la red, como validar transacciones. A cambio, recibes recompensas en forma de monedas adicionales."),
    ("Yo, how do I make mad cash with Forex, fam?", "To make money with Forex, start by learning the basics, choose a reliable broker, practice with a demo account, and use risk management strategies like stop-loss orders. It takes time and discipline!"),
    ("How do I yeet my money into Bitcoin?", "To invest in Bitcoin, set up a crypto wallet, sign up on an exchange like Binance or Coinbase, deposit funds, and buy Bitcoin. Be cautious of market volatility and only invest what you can afford to lose."),
    ("Can I use Forex profits to buy NFTs in the metaverse?", "Yes, you can use Forex profits to buy NFTs in the metaverse! Convert your profits to a cryptocurrency like Ethereum, set up a wallet, and purchase NFTs on platforms like OpenSea."),
    ("What's the difference between Forex leverage and Crypto staking?", "Forex leverage lets you control a larger position with less capital, increasing both potential profits and risks. Crypto staking involves locking up coins to support a blockchain network and earn rewards, with lower risk but slower returns."),
    ("How does Bitcoin mining affect Forex exchange rates?", "Bitcoin mining can indirectly affect Forex exchange rates by influencing the supply of Bitcoin, which impacts its price. A rising Bitcoin price can affect investor sentiment and capital flows, influencing currency values."),
    ("Should I trade Forex or Crypto during a Tunisian festival?", "Trading during a Tunisian festival depends on market conditions. Festivals can affect local economic activity, which might influence the Tunisian Dinar (TND) in Forex markets. Crypto markets are less likely to be directly affected."),
    ("What's the exchange rate of 1 TND to USD on April 10, 2025?", "I'm sorry, I don't have access to real-time exchange rates for April 10, 2025. You can check a reliable Forex platform like XE.com or OANDA for the latest rates."),
    ("Is a 50% leverage safe for Forex trading?", "A 50% leverage (e.g., 2:1) is relatively safe for Forex trading as it limits risk compared to higher leverage like 50:1. However, safety depends on your risk management, market conditions, and trading strategy."),
    ("How much is 0.001 BTC worth in EUR?", "I don't have real-time data for April 2025, but you can calculate the value of 0.001 BTC in EUR by checking the current BTC/EUR rate on an exchange like Binance or Kraken and multiplying by 0.001."),
    ("What's the 200-day moving average for EUR/USD?", "I don't have access to real-time market data for April 2025. You can find the 200-day moving average for EUR/USD on trading platforms like TradingView or MetaTrader.")
]

# Insert FAQs into the database
cursor.executemany("INSERT OR IGNORE INTO faqs (query, response) VALUES (?, ?)", faq_data)




# Commit changes and close the connection
conn.commit()
conn.close()

print("Database setup complete. FAQs and logs tables created and populated.")