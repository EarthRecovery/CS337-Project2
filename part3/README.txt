## **Setup**

The setup procedure is identical to Part 1:

(
## Requirements

- Python 3.10+

## Installation

(to be done while in the `CS337-Project2/` directory, NOT `part3/`)
1. Install Python dependencies:
pip install -r requirements.txt

2. Download the spaCy English model:
python -m spacy download en_core_web_sm
)

## GitHub Repository

github address: [EarthRecovery/CS337-Project2](https://github.com/EarthRecovery/CS337-Project2)

To add GEMINI API_KEY, add a .env file under part3 dictionary, and add GEMINI_API_KEY=...

To run the QA system, execute the following as nessacary:

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
cd part3
cp .env.example .env
```

Then change the api key in the new `.env` file

```bash
GEMINI_API_KEY=your_api_key_here
```

**Important**: Add `.env` to your `.gitignore` to keep your API key private!

### 4. Run the Assistant

```bash
cd part2 # only if not already in the directory obviously
python main.py
```

Simply select the configuration dictionary to **Part 3 mode** when prompeted

## **Model**

This project uses **Gemini-2.5-flash-lite** with the **default temperature** settings.

## **System Architecture**

When the user starts interacting with the assistant, they first decide whether to enable the **LLM-driven agent**.
 If enabled, the pipeline operates as follows:

1. **Recipe Parsing via LLM**
    The system retrieves raw HTML from a recipe URL, then prompts the LLM to convert it into structured JSON-style data required for downstream QA tasks.
2. **Intent Detection**
    The LLM classifies the user’s question into predefined intent categories.
    If the intent is irrelevant to cooking, the system rejects the request.
3. **Question Answering**
    The system forms a response by combining information from:
   - parsed recipe data
   - user intent
   - interaction history
   - current cooking step

## **Core Capabilities**

- **State Tracking**
   The assistant infers the user’s current step by referencing prior interactions.
- **Parsing**
   The LLM performs end-to-end recipe extraction from raw HTML, and works even on unseen websites.
- **Intent Detection**
   Out-of-scope or irrelevant queries are handled via an **UNKNOWN** fallback intent.
- **Question Answering**
   The model receives the full recipe, history, and intent context.
   Large context improves reasoning but increases latency and cost.
- **YouTube Search**
   Triggered when the system detects “how-to”–style questions or procedural requests.
   It provides more actionable responses through video guidance.

## **Integration and Scaffolding**

- **State Representation**
   Recipes are parsed into structured JSON to support reliable retrieval and reasoning.
- **Tool Calls**
   The LLM extracts user intent, and the system invokes relevant functions (e.g., YouTube search).
- **Prompt Roles**
   Different prompts are used for different subtasks (parsing, intent detection, QA), improving reliability.
- **Intent Categories**
   We maintain multiple intent types to map different user behaviors to appropriate responses.

## **New Capabilities Introduced in Part 3**

### 1. Recipe introduction retrieval

```
User: show me introduction for the recipe  
LLM QA Response: This traditional kugelhopf recipe is a buttery, sweet Alsatian yeast bread baked in a tall, ridged mold and flavored with golden raisins, citrus, and almonds.
```

### 2. Support for new sites

The system can now parse recipes from platforms such as **epicurious.com**.

### 3. Nutrition query support

```
User: what is nutrition for this recipe?  
LLM QA Response: This recipe contains 759 kcal, 46g fat, 11g saturated fat, 190mg cholesterol,
1709mg sodium, 46g carbohydrates, 7g sugar, 3g fiber, 42g protein, 33mg vitamin C,
174mg calcium, 5mg iron, and 739mg potassium.
```