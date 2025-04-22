# backend/main.py
from chatbot import get_response
import sqlite3
from datetime import datetime
import logging
import os

def run_chatbot():
    print("Welcome to the Forex-Crypto Chatbot! Type 'exit' to quit.")
    while True:
        query = input("You: ")
        if query.lower() == "exit":
            print("Goodbye!")
            break
        response, label, confidence = get_response(query)
        print(f"Bot: {response}")
        print(f"(Label: {label}, Confidence: {confidence:.4f})")
        feedback = input("Was this response helpful? (yes/no): ")

        #update the most recent log entry with feedback 
        try:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(BASE_DIR, "database", "chatbot.db")
            print("USING DB at  : ", db_path)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE logs
                SET feedback = ?
                WHERE id = (SELECT id FROM logs WHERE query = ? ORDER BY timestamp DESC LIMIT 1)
                """,
                (feedback, query)
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error in run_chatbot: {str(e)}")
            print("Feedback could not be logged due to a database issue.")


if __name__ == "__main__":
    run_chatbot()