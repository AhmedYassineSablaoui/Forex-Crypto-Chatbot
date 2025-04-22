// frontend/static/js/scripts.js
let lastQuery = '';

function sendMessage() {
    const input = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const feedbackContainer = document.getElementById('feedback-container');

    const query = input.value.trim();
    if (!query) return;

    // Display user message
    const userMessage = document.createElement('div');
    userMessage.className = 'message user-message';
    userMessage.innerHTML = `
        <div class="d-flex justify-content-end">
            <span class="badge bg-primary text-white p-2 rounded">${query}</span>
        </div>
        <div class="text-end text-muted small">${new Date().toLocaleString()}</div>
    `;
    chatBox.appendChild(userMessage);

    // Clear input and scroll to bottom
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send query to the server
    fetch('/chatbot/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
        body: `query=${encodeURIComponent(query)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        // Display bot response
        const botMessage = document.createElement('div');
        botMessage.className = 'message bot-message';
        botMessage.innerHTML = `
            <div class="d-flex justify-content-start">
                <span class="badge bg-secondary text-white p-2 rounded">${data.response}</span>
            </div>
            <div class="text-start text-muted small">(Label: ${data.label}, Confidence: ${data.confidence.toFixed(4)})</div>
        `;
        chatBox.appendChild(botMessage);

        // Show feedback buttons
        lastQuery = query;
        feedbackContainer.style.display = 'block';

        // Scroll to bottom
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        const errorMessage = document.createElement('div');
        errorMessage.className = 'message bot-message';
        errorMessage.innerHTML = `
            <div class="d-flex justify-content-start">
                <span class="badge bg-danger text-white p-2 rounded">Error: ${error.message}</span>
            </div>
        `;
        chatBox.appendChild(errorMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

function submitFeedback(feedback) {
    const chatBox = document.getElementById('chat-box');
    const feedbackContainer = document.getElementById('feedback-container');

    // Send feedback to the server
    fetch('/chatbot/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
        },
        body: `query=${encodeURIComponent(lastQuery)}&feedback=${feedback}`
    })
    .then(response => response.json())
    .then(data => {
        // Hide feedback buttons
        feedbackContainer.style.display = 'none';

        // Display feedback confirmation
        const feedbackMessage = document.createElement('div');
        feedbackMessage.className = 'message bot-message';
        feedbackMessage.innerHTML = `
            <div class="d-flex justify-content-start">
                <span class="badge bg-info text-white p-2 rounded">Feedback recorded: ${feedback}</span>
            </div>
        `;
        chatBox.appendChild(feedbackMessage);
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error('Error submitting feedback:', error);
    });
}

// Allow sending message on Enter key
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});