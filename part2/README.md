# Part 2 — LLM-Only Recipe Assistant

**Group 5**: Yuxiang Lin, Matthew Mailman, Andre Washington

A pure prompt driven conversational recipe assistant powered entirely by Gemini LLM

## Overview

All recipe understanding, question answering, and conversation management happens within the LLM itself with no explicit Python rules,

## GitHub Repository

[EarthRecovery/CS337-Project2](https://github.com/EarthRecovery/CS337-Project2)

## Model Configuration

- **Model**: `gemini-2.0-flash-lite` 
- **Temperature**: `1.0` (default)
- **Max Output Tokens**: `1000`

## System Architecture

### Pure LLM Approach

Unlike the rules-based system (Part 1) or hybrid system (Part 3), this implementation:

1. **No Explicit Rules**: All recipe interpretation happens via natural language understanding
2. **No Structured State**: No Python dictionaries tracking current step, ingredients, etc.
3. **Conversation-Only Context**: The LLM maintains state purely through conversation history
4. **Single Unified Prompt**: One large system prompt defines the assistant's entire behavior

### How It Works

```
User provides recipe URL
        ↓
Python scrapes HTML/text
        ↓
Recipe content + System Prompt → LLM
        ↓
LLM understands recipe structure
        ↓
User asks questions
        ↓
LLM answers using conversation history + recipe context
        ↓
Repeat...
```

### Components

1. **`prompts.py`**: Contains the unified system prompt
   - Defines assistant role and capabilities
   - Provides examples of question types and responses
   - Guides conversation management and state tracking
   - Instructs on handling ambiguity and out-of-scope questions

2. **`scraper.py`**: Web scraping utility
   - Fetches HTML from recipe URLs
   - Cleans and extracts text content
   - Returns raw recipe text to be sent to LLM

3. **`llm_assistant.py`**: Main assistant class
   - Manages Gemini API client
   - Maintains conversation history
   - Handles recipe loading and chat interactions
   - No rule-based logic—just passes messages to/from LLM

4. **`main.py`**: Entry point
   - Initializes LLM assistant
   - Runs interactive conversation loop

## Setup Instructions

### 1. Install Dependencies

```bash
pip install google-genai python-dotenv requests beautifulsoup4
```

### 2. Create API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Create a Gemini API key

### 3. Configure Environment

Create a `.env` file in the `part2/` directory:

```bash
GEMINI_API_KEY=your_api_key_here
```

**Important**: Add `.env` to your `.gitignore` to keep your API key private!

### 4. Run the Assistant

```bash
cd part2
python main.py
```

## Usage

### Interactive Mode

```
$ python main.py


LLM-Only Recipe Assistant


This assistant uses pure LLM reasoning with no explicit rules.
All understanding comes from the language model and conversation history.

Enter recipe URL: https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/

Fetching recipe from: https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/

Recipe loaded: Classic and Simple Meat Lasagna

I'm ready to help you cook! You can ask me questions about the recipe.
Try asking: 'Show me the ingredients', 'What's the first step?', 'How do I do that?', etc.
Type 'exit' to quit.

You: Show me the ingredients## Supported Question Types

The LLM handles all question types through natural language understanding:

### Recipe Retrieval
- "Show me the ingredients"
- "What tools do I need?"
- "What cooking methods are used?"
- "List all the steps"

### Navigation
- "What's the first step?"
- "Next step" / "Go to the next step"
- "Previous step" / "Go back"
- "Repeat that" / "Say that again"
- "Go to step 5"

### Parameter Queries
- "How much sugar do I need?"
- "How much?" (vague  infers from context)
- "What temperature?"
- "How long do I bake it?"
- "When is it done?"

### Clarification & How-To
- "What is a mandoline?"
- "How do I julienne?"
- "How do I do that?" (vague  infers from context)

### Substitutions
- "Can I use olive oil instead of butter?"
- "What can I substitute for eggs?"

### Out-of-Scope Handling
- Non-cooking questions are politely declined
- User is redirected to recipe-related topics

## Example Conversations

### Example 1: Basic Navigation

```
You: What's the first step?
Assistant: Step 1: Preheat the oven to 350°F (175°C).

You: Next
Assistant: Step 2: In a large skillet, cook the ground beef over medium heat until browned, breaking it into crumbles. Drain excess fat.

You: How much beef?
Assistant: You need 1 pound of lean ground beef for this recipe.
```

### Example 2: Vague Reference Handling

```
You: Go to step 4
Assistant: Step 4: In a mixing bowl, beat the eggs with the ricotta cheese and half of the mozzarella.

You: How many?
Assistant: You need 3 eggs for this step.

You: And how much of the cheese?
Assistant: You'll use 15 ounces of ricotta cheese and 8 ounces of mozzarella (that's half of the total 16 ounces).
```

### Example 3: Open-Ended Questions

```
You: How do I know when the lasagna is done?
Assistant: The lasagna is done when the cheese on top is melted and golden brown, and the edges are bubbling. This typically takes about 30-35 minutes in a 350°F oven. You can also insert a knife in the center - it should come out hot.

You: Should I cover it with foil?
Assistant: The recipe doesn't specify, but it's common to cover lasagna with foil for the first 20-25 minutes to prevent over-browning, then remove the foil for the last 10 minutes to let the cheese get golden and bubbly.
```


### API Key Errors

```
ValueError: GEMINI_API_KEY not found. Please set it in your .env file.
```

**Solution**: Create a `.env` file with your API key:
```
GEMINI_API_KEY=your_key_here
```

### Rate Limit Errors

```
Error: Rate limit exceeded
```

**Solution**: You've hit the free tier limit. Wait or reduce request frequency.

### Recipe Scraping Failures

```
Error fetching recipe: ...
```

**Solution**:
- Check internet connection
- Verify URL is valid
- Some sites may block scraping


## License

Part of CS337 Project 2 - Northwestern University
