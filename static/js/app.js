// Global variables
let recognition = null;
let isListening = false;

// Initialize speech recognition
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            isListening = true;
            document.getElementById('mic-btn').classList.add('listening');
            document.getElementById('speech-status').classList.remove('hidden');
        };

        recognition.onend = function() {
            isListening = false;
            document.getElementById('mic-btn').classList.remove('listening');
            document.getElementById('speech-status').classList.add('hidden');
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('question-input').value = transcript;
            // Auto-send after speech recognition
            setTimeout(() => {
                sendQuestion();
            }, 500);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            isListening = false;
            document.getElementById('mic-btn').classList.remove('listening');
            document.getElementById('speech-status').classList.add('hidden');

            let errorMsg = 'Speech recognition error. ';
            if (event.error === 'not-allowed') {
                errorMsg += 'Please allow microphone access.';
            } else if (event.error === 'no-speech') {
                errorMsg += 'No speech detected. Please try again.';
            } else {
                errorMsg += 'Please try again.';
            }
            showError(errorMsg);
        };
    } else {
        console.warn('Speech recognition not supported in this browser');
        document.getElementById('mic-btn').disabled = true;
        document.getElementById('mic-btn').title = 'Speech recognition not supported in this browser';
    }
}

// DOM elements
document.addEventListener('DOMContentLoaded', function() {
    const loadRecipeBtn = document.getElementById('load-recipe-btn');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const questionInput = document.getElementById('question-input');
    const recipeUrlInput = document.getElementById('recipe-url');

    // Initialize speech recognition
    initSpeechRecognition();

    // Load recipe
    loadRecipeBtn.addEventListener('click', loadRecipe);

    // Send question
    sendBtn.addEventListener('click', sendQuestion);

    // Enter key to send
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendQuestion();
        }
    });

    // Microphone button
    micBtn.addEventListener('click', function() {
        if (!recognition) {
            showError('Speech recognition is not supported in your browser. Please use Chrome, Edge, or Safari.');
            return;
        }

        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
});

// Load recipe function
async function loadRecipe() {
    const url = document.getElementById('recipe-url').value.trim();

    if (!url) {
        showError('Please enter a recipe URL');
        return;
    }

    // Show loading state
    const loadBtn = document.getElementById('load-recipe-btn');
    loadBtn.disabled = true;
    loadBtn.textContent = 'Loading...';

    try {
        const response = await fetch('/api/load_recipe', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        });

        const data = await response.json();

        if (response.ok) {
            // Display recipe info
            document.getElementById('dish-name').textContent = data.dish_name;
            document.getElementById('dish-intro').textContent = data.dish_intro;
            document.getElementById('prep-time').textContent = `Prep: ${data.prep_time}`;
            document.getElementById('cook-time').textContent = `Cook: ${data.cook_time}`;
            document.getElementById('total-time').textContent = `Total: ${data.total_time}`;
            document.getElementById('serving').textContent = `Servings: ${data.serving}`;

            document.getElementById('recipe-info').classList.remove('hidden');
            document.getElementById('chat-section').classList.remove('hidden');

            // Update step indicator
            updateStepIndicator();

            showSuccess('Recipe loaded successfully! You can now ask questions.');
        } else {
            showError(data.error || 'Failed to load recipe');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        loadBtn.disabled = false;
        loadBtn.textContent = 'Load Recipe';
    }
}

// Send question function
async function sendQuestion() {
    const question = document.getElementById('question-input').value.trim();

    if (!question) {
        return;
    }

    // Add user message to chat
    addMessageToChat(question, 'user');

    // Clear input
    document.getElementById('question-input').value = '';

    // Show loading
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;
    sendBtn.textContent = 'Thinking...';

    try {
        const response = await fetch('/api/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question: question })
        });

        const data = await response.json();

        if (response.ok) {
            // Add system response to chat
            addMessageToChat(data.response, 'system');

            // Update step indicator
            updateStepIndicator();

            // Check if exit
            if (data.exit) {
                showSuccess('Session ended. Load a new recipe to continue.');
            }
        } else {
            addMessageToChat(data.error || 'Error processing question', 'system');
        }
    } catch (error) {
        addMessageToChat('Network error: ' + error.message, 'system');
    } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
    }
}

// Add message to chat
function addMessageToChat(message, type) {
    const chatContainer = document.getElementById('chat-container');

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Handle multiline text and preserve formatting
    const lines = message.split('\n');
    lines.forEach((line, index) => {
        if (line.trim()) {
            const p = document.createElement('p');
            p.textContent = line;
            contentDiv.appendChild(p);
        }
        if (index < lines.length - 1) {
            contentDiv.appendChild(document.createElement('br'));
        }
    });

    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update step indicator
async function updateStepIndicator() {
    try {
        const response = await fetch('/api/get_state');
        const data = await response.json();

        if (response.ok) {
            document.getElementById('current-step').textContent = data.current_step;
            document.getElementById('max-step').textContent = data.max_step;
        }
    } catch (error) {
        console.error('Error updating step indicator:', error);
    }
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;

    const section = document.getElementById('recipe-input-section');

    // Remove any existing error messages
    const existingError = section.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    section.appendChild(errorDiv);

    // Remove after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;

    const section = document.getElementById('recipe-input-section');

    // Remove any existing success messages
    const existingSuccess = section.querySelector('.success-message');
    if (existingSuccess) {
        existingSuccess.remove();
    }

    section.appendChild(successDiv);

    // Remove after 5 seconds
    setTimeout(() => {
        successDiv.remove();
    }, 5000);
}
