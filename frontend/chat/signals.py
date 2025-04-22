# frontend/chat/signals.py
import sqlite3
import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from datetime import datetime

@receiver(post_save, sender=User)
def create_chatbot_user(sender, instance, created, **kwargs):
    """
    Create a corresponding entry in the chatbot.db users table when a new Django user is created.
    """
    if created:
        try:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'chatbot.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, username, preferred_language, created_at) VALUES (?, ?, ?, ?)",
                (str(instance.id), instance.username, 'en', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error in create_chatbot_user: {str(e)}")