# backend/chatbot.py
import logging
import os
from predict import predict_query
from faq_responses import get_faq_response
from config import FAQ_CONFIDENCE_THRESHOLD
import sqlite3
from datetime import datetime
import os



response_cache = {}


def get_previous_context(user_id) : 
    """ 
    Fetch the most recent query and response for the user from the conversations table .

    Args: 
    user_id (str) : the user identifier . 

    Returns: 
    tuple: (previous_query, previous_response) or (None , None) if no context exists. 
    """
    try : 
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(BASE_DIR, "database", "chatbot.db")
        #print("Using DB at:", db_path)
        conn = sqlite3.connect(db_path) 
        cursor = conn.cursor()
        cursor.execute(
            "SELECT query, response FROM conversations WHERE user_id= ? ORDER BY timestamp DESC LIMIT 1 ",
            (user_id, )

        )
        result = cursor.fetchone()
        conn.close()
        if result: 
            return result[0], result[1]
        return None, None
    except sqlite3.Error as e : 
        print(f"Database error in get_previous_context: {str(e)}")
        return None, None


def resolve_context(query, previous_query, previous_response) : 
    """
    Resolve contextual references in the query (e.g., replace 'it' with the subject of the previous query).
    
    Args:
        query (str): The current user query.
        previous_query (str): The previous query from the conversation history.
        previous_response (str): The previous response from the conversation history.
    
    Returns:
        str: The resolved query with contextual references replaced.
    """
    if not previous_query or not previous_response:
        return query

    query_lower = query.lower().strip()
    previous_query_lower = previous_query.lower().strip()

    # Define subjects to look for
    subjects = ["bitcoin", "ethereum", "forex", "crypto", "staking", "nft"]

    # Handle "Tell me more" or "Explain more"
    if query_lower in ["tell me more", "explain more", "more info"]:
        # Return the previous query to get a more detailed response
        for subject in subjects:
            if subject in previous_query_lower:
                return f"Explain {subject} in more detail"

    # Handle "Why is that?" or "How does that work?"
    if query_lower in ["why is that", "how does that work"]:
        for subject in subjects:
            if subject in previous_query_lower:
                return f"Explain why {subject} works that way"

    # Simple context resolution: look for pronouns like "it" or "that"
    if " it " in query_lower or "it " in query_lower or query_lower.startswith("it "):
        # Extract the main subject from the previous query
        previous_query_lower = previous_query.lower()
        subjects = ["bitcoin", "ethereum", "forex", "crypto", "staking", "nft"]
        for subject in subjects:
            if subject in previous_query_lower:
                # Replace "it" with the subject
                resolved_query = query_lower.replace(" it ", f" {subject} ").replace("it ", f"{subject} ")
                return resolved_query.capitalize()
    return query


def get_response(query, user_id="default_user"):
    """
    Generate a response for a user query based on the model's classification, with context awareness.
    
    Args:
        query (str): The user query.
        user_id (str): The user identifier.
    
    Returns:
        tuple: (response, label, confidence) where response is the chatbot's reply,
               label is "FAQ" or "Non-FAQ", and confidence is a float.
    """
    cache_key = f"{user_id}:{query}"

    if cache_key in response_cache:
        return response_cache[cache_key]
    
    # Get previous context
    previous_query, previous_response = get_previous_context(user_id)
    # Resolve contextual references in the query
    resolved_query = resolve_context(query, previous_query, previous_response)


    
    label, confidence = predict_query(resolved_query)

    if label == "FAQ" and confidence >= FAQ_CONFIDENCE_THRESHOLD:
        response = get_faq_response(resolved_query)
    else:
        response = "I’m sorry, I can only answer questions about Forex and Crypto. Please ask something related to trading!"
        label = "Non-FAQ"
    
    # log the interactions to the database
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(BASE_DIR, "database", "chatbot.db")
        print("Using DB at:", db_path)
        conn = sqlite3.connect(db_path) 
        cursor = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO logs (timestamp, query, label, confidence, response, feedback) VALUES (?, ?, ?, ?, ?, ?)",
            (timestamp, resolved_query, label, confidence, response, None)
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error in get_response: {str(e)}")
    
    response_cache[cache_key] = (response, label, confidence)
    return response, label, confidence

# Test the chatbot logic
if __name__ == "__main__":
    test_queries = [
        "What is the difference between Bitcoin and Ethereum?",
        "What is the capital of France?",
        "How do I yeet my money into Bitcoin?"
    ]
    for query in test_queries:
        response, label, confidence = get_response(query)
        print(f"Query: {query}")
        print(f"Response: {response}")
        print(f"Label: {label}, Confidence: {confidence:.4f}\n")