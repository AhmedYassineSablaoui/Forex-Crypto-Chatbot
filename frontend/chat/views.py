# frontend/chat/views.py
import sys
import os
import sqlite3
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

# Add the backend directory to the Python path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
sys.path.append(backend_path)

# Import the backend chatbot function
from chatbot import get_response

def register_view(request) : 
    """
    Handle user registration 

    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate input  
        if not username or not email or not password or not confirm_password : 
            messages.error(request, "All fields are required")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "email is already in use")
            return redirect('register')

        # Create the user
        try:
            user = User.objects.create_user(username=username,email=email,  password=password)
            user.save()

            # Log the user in
            login(request, user)
            messages.success(request, "Registration successful! You are now logged in.")
            return redirect('chat')
        except Exception as e:
            messages.error(request, f"Error during registration: {str(e)}")
            return redirect('register')
    return render(request, 'register.html')

def login_view(request):
    """
    Handle user login.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('chat')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'login.html')

def logout_view(request) : 
    """ 
    Handle user login """

    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required



def chat_view(request):
    """
    Render the chat interface with conversation history.
    """
    # For simplicity, use a default user_id (in production, use authentication)
    user_id = str(request.user.id) #use the authentificated user's ID 


    # Fetch conversation history from the database
    try:
        conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'chatbot.db'))
        cursor = conn.cursor()
        cursor.execute("SELECT query, response, timestamp FROM conversations WHERE user_id = ? ORDER BY timestamp DESC LIMIT 10", (user_id,))
        conversations = cursor.fetchall()
        cursor.close()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error in chat_view: {str(e)}")
        conversations = []

    return render(request, 'chat.html', {'conversations': conversations, 'username': request.user.username})

@csrf_exempt  # Temporarily disable CSRF for simplicity; in production, handle CSRF properly
@login_required

def chatbot_response(request):
    """
    Handle AJAX requests from the frontend to get chatbot responses and feedback.
    """
    if request.method == 'POST':
        query = request.POST.get('query', '')
        feedback = request.POST.get('feedback', None)

        # For simplicity, use a default user_id (in production, use authentication)
        user_id = str(request.user.id)

        if not query:
            return JsonResponse({'error': 'No query provided'}, status=400)

        if feedback:
            # Handle feedback submission (already handled in backend/chatbot.py)
            return JsonResponse({'status': 'Feedback recorded'})

        # Get response from the backend with context
        try:
            response, label, confidence = get_response(query, user_id)

            # Store in conversations table
            conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'chatbot.db'))
            cursor = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO conversations (user_id, query, response, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, query, response, timestamp)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return JsonResponse({
                'response': response,
                'label': label,
                'confidence': confidence
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)