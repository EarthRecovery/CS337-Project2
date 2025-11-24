# Recipe Q&A Web UI with Speech-to-Text

This is a web-based user interface for the Recipe Q&A system with integrated speech-to-text functionality.

## Features


- **Speech-to-Text**: Click the microphone button to ask questions using your voice (uses Web Speech API)
- **Real-time Q&A**: Ask questions about recipes and get instant responses
- **Step Navigation**: Track your current step and navigate through the recipe
- **Recipe Information**: View recipe details including prep time, cook time, and servings

## Requirements

- Python 3.7+
- Flask
- All dependencies from requirements.txt

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Download the spaCy English model:
```bash
python -m spacy download en_core_web_sm
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter a recipe URL from AllRecipes.com and click "Load Recipe"

4. Start asking questions using text or voice.

## Using Speech-to-Text

1. Click the microphone button 
2. Allow microphone access when prompted by your browser
3. Speak your question clearly
4. The question will be automatically sent after recognition

**Note**: Speech recognition works best in:
- Google Chrome
- Microsoft Edge
- Safari (on macOS/iOS)

## Example Questions

- "Show me the ingredients"
- "What tools do I need?"
- "Go to the next step"
- "How much salt do I need?"
- "What temperature?"
- "How long do I cook this?"
- "Go to step 5"
- "What is the first step?"

## Troubleshooting

### Speech Recognition Not Working

- Make sure you're using a supported browser (Chrome, Edge, Safari)
- Grant microphone permissions when prompted
- Check that your microphone is working properly
- Try speaking closer to the microphone

### Recipe Not Loading

- Verify the URL is from AllRecipes.com
- Check your internet connection
- Make sure all dependencies are installed

### Server Not Starting

- Check that port 5000 is not already in use
- Verify all dependencies are installed
- Check the console for error messages

## Architecture

- **Backend**: Flask server (app.py) that integrates with the existing QA system
- **Frontend**: HTML/CSS/JavaScript with Web Speech API
- **Speech Recognition**: Browser-based using Web Speech API (no server-side processing needed)
- **Session Management**: Uses Flask sessions to maintain state per user

## File Structure

```
nlpproject2/
├── app.py                  # Flask application
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── app.js         # Frontend logic + speech-to-text
├── project/
│   ├── qa.py              # Q&A logic
│   └── parser.py          # Recipe parser
└── requirements.txt       # Python dependencies
```


