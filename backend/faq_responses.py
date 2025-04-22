# backend/faq_responses.py
import requests
import sqlite3
import os


def get_dynamic_response(query):
    if "exchange rate" in query.lower():
        try:
            api_key = "381f3877bbe977b29dec8d16"
            url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/TND"
            #print(f"Attempting to fetch exchange rate from: {url}")
            response = requests.get(url)
            #print(f"API Response Status Code: {response.status_code}")
            #print(f"API Response Text: {response.text}")
            data = response.json()
            #print(f"Parsed JSON Data: {data}")
            if data["result"] == "success":
                rate = data["conversion_rates"]["USD"]
                print(f"Exchange Rate (TND to USD): {rate}")
                return f"The exchange rate of 1 TND to USD is {rate}.", True
            else:
                #print(f"API Error: {data.get('error-type', 'Unknown error')}")
                return "I couldn't fetch the exchange rate right now. Please try again later.", False
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return "I couldn't fetch the exchange rate right now. Please try again later.", False
    return None, False

def get_faq_response(query):
    """
    Fetch a predefined response for an FAQ query, with case-insensitive matching.
    
    Args:
        query (str): The user query.
    
    Returns:
        str: The predefined response, or a default message if not found.
    """
    # Try dynamic response first
    dynamic_response, success = get_dynamic_response(query)
    print(f"Dynamic Response: {dynamic_response}, Success: {success}")
    if success:
        return dynamic_response
    
    # Connect to the database
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
        print("the Base Directory:",BASE_DIR) # goes up to project root
        db_path = os.path.join(BASE_DIR, "database", "chatbot.db")
        conn = sqlite3.connect(db_path)
        print("Using DB at : ", db_path)
        print("Absolute Path : ", os.path.abspath(db_path))
        if not os.path.exists(db_path):

            raise FileNotFoundError(f"Database file does not exist at: {db_path}")

        cursor = conn.cursor()
        query_lower = query.lower().strip()
        cursor.execute("SELECT response FROM faqs WHERE LOWER(query) = ?", (query_lower,))
        result = cursor.fetchone()
        # close the connection 
        conn.close()

        if result:
            return result[0]
   
    
        return "This is a Forex/Crypto FAQ! I'll fetch the answer for you soon."
    except sqlite3.Error as e:
        print(f"Database error in get_faq_response: {str(e)}")
        return "Sorry, I'm having trouble accessing the FAQ database right now. Please try again later."