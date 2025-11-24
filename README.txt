Project 2: Yuxiang Lin, Matthew Mailman, Andre Washington
Group 5

# Recipe Parser and Q&A System with Speech-to-Text

A web-based conversational interface for parsing and navigating recipes from AllRecipes.com, featuring speech-to-text input.



## Requirements

- Python 3.10+
- Modern web browser (Chrome, Edge, or Safari recommended for speech recognition)

## Installation

1. Install Python dependencies:
pip install -r requirements.txt

2. Download the spaCy English model:
python -m spacy download en_core_web_sm

## Running the Application

### Web Interface (Recommended):
python app.py

Then navigate to: http://localhost:5001

### Terminal Interface:
python project/main.py

## Supported Website
This parser supports AllRecipes.com only.

## Features Implemented

### Core Features:
Recipe parsing from AllRecipes.com
Ingredient extraction (name, quantity, measurement)
Tool identification
Method extraction
Step-by-step parsing
Comprehensive question answering

### Optional Features (All 6 Implemented):
Descriptor extraction (e.g., "fresh", "extra-virgin")
Preparation extraction (e.g., "finely chopped", "minced")
Other cooking methods (all methods extracted, not just primary)
Atomic steps (complex directions broken into single actions)
Contextual annotations (oven temperature, prepared ingredients carried forward)
Information type differentiation (warnings, advice, observations)

### Extra Credit:
Web interface with Flask
Speech-to-text input (Web Speech API)

## Testing Questions for TA

### 1. Recipe Retrieval and Display:
- "Show me the ingredients list"
- "What tools do I need?"
- "Show me all the methods"

### 2. Navigation Commands:
- "Go to the next step"
- "Go back one step"
- "Go to step 5"
- "Repeat please"

### 3. Step Parameter Queries:
- "How much salt do I need?" (must be on a step with salt)
- "How much of that do I need?" (vague - infers from current step)
- "What temperature?"
- "How long do I bake it?"

### 4. Clarification Questions:
- "What is a whisk?"

### 5. Procedure Questions:
- "How do I preheat the oven?"
- "How do I do that?" (vague - refers to current step method)

### 6. Exit:
- "exit"

## Example Test Recipe URLs

1. https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/
2. https://www.allrecipes.com/mediterranean-crispy-rice-chicken-bowl-recipe-8778475
3. https://www.allrecipes.com/spiral-spicy-cucumber-salad-recipe-11814637/

## Troubleshooting

### Recipe Not Loading:
- Ensure URL is from AllRecipes.com
- Check internet connection

### Speech Recognition Not Working:
- Use Chrome, Edge, or Safari
- Grant microphone permissions

### Port Already in Use:
- Change port in app.py: app.run(debug=True, port=5002)
