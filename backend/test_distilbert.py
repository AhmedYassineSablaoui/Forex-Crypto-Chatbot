from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# Load the fine-tuned model and tokenizer
model_path = "./models/forex_distilbert"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

# Move to GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
model.eval()

# Function to classify a query
def classify_query(query):
    # Tokenize the input
    inputs = tokenizer(query, truncation=True, padding='max_length', max_length=64, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    # Make prediction
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
        confidence = probabilities[0][predicted_class].item()

    # Map class to label
    label = "FAQ" if predicted_class == 1 else "Non-FAQ"
    return label, confidence
# Expanded list of test queries
queries = [
    # Straightforward FAQs (from previous test)
    "What is the difference between Bitcoin and Ethereum?",
    "How do I start trading Forex with a small budget?",
    "What are the risks of using leverage in Crypto trading?",
    "Explain the concept of staking in Crypto.",
    
    # Straightforward Non-FAQs (from previous test)
    "What is the capital of France?",
    "How do I bake a chocolate cake?",
    "Tell me about the Roman Empire.",
    "What’s the best way to grow tomatoes?",
    
    # Ambiguous Queries (from previous test)
    "How does the weather in Tunisia affect Forex trading?",
    "What is the history of Bitcoin mining in France?",
    "Can the price of Ethereum influence the stock market?",
    "Does the Roman Empire have any connection to modern Forex markets?",
    
    # More Ambiguous Queries
    "How does the Tunisian election impact the price of Bitcoin?",
    "What is the relationship between olive oil prices and Forex markets?",
    "Can the history of Carthage predict Crypto trends?",
    "Does the Eurovision song contest affect Forex volatility?",
    
    # Edge Cases (from previous test)
    "Forex?",  # Very short query
    "Wht is Cryto tradng?",  # Typos
    "Tell me everything you know about the blockchain technology in a very detailed way.",  # Long and detailed
    "leverage forex how???",  # Unusual phrasing
    
    # New Topics (from previous test)
    "What is the impact of quantum computing on Crypto security?",
    "How does the metaverse affect NFT trading?",
    "What are the latest regulations on stablecoins in the EU?",
    "Can AI predict Forex market trends accurately?",
    
    # Queries in Different Languages
    # French (common in Tunisia)
    "Qu'est-ce que le trading Forex ?",  # "What is Forex trading?"
    "Parlez-moi de l'histoire de Tunis.",  # "Tell me about the history of Tunis."
    "Comment fonctionne le staking en Crypto ?",  # "How does staking work in Crypto?"
    "Quel temps fait-il aujourd'hui ?",  # "What’s the weather like today?"
    
    # Arabic (Tunisian context)
    "ما هو تداول الفوركس؟",  # "What is Forex trading?"
    "كيف كانت الحضارة القرطاجية؟",  # "What was the Carthaginian civilization like?"
    "ما هي مخاطر الرافعة المالية في تداول العملات الرقمية؟",  # "What are the risks of leverage in Crypto trading?"
    "كيف يمكنني زراعة الطماطم؟",  # "How can I grow tomatoes?"
    
    # Spanish (for broader reach)
    "¿Qué es el trading de Forex?",  # "What is Forex trading?"
    "¿Cómo fue la historia de España?",  # "What was the history of Spain like?"
    "¿Qué es el staking en Cripto?",  # "What is staking in Crypto?"
    "¿Cómo está el clima hoy?",  # "What’s the weather like today?"
    
    # Other Challenging Cases
    # Slang/Informal Language
    "Yo, how do I make mad cash with Forex, fam?",
    "Crypto staking, what’s the vibe on that?",
    "Gimme the tea on Tunisian history, bro.",
    "How do I yeet my money into Bitcoin?",
    
    # Mixed Topics
    "Can I use Forex profits to buy NFTs in the metaverse?",
    "What’s the difference between Forex leverage and Crypto staking?",
    "How does Bitcoin mining affect Forex exchange rates?",
    "Should I trade Forex or Crypto during a Tunisian festival?",
    
    # Numerical Data/Symbols
    "What’s the exchange rate of 1 TND to USD on April 10, 2025?",
    "Is a 50% leverage safe for Forex trading?",
    "How much is 0.001 BTC worth in EUR?",
    "What’s the 200-day moving average for EUR/USD?"
]

for query in queries:
    label, confidence = classify_query(query)
    print(f"Query: {query}")
    print(f"Predicted: {label} (Confidence: {confidence:.4f})")
    print()