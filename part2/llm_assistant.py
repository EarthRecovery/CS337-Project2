"""
LLM-Only Recipe Assistant.
All reasoning and decision-making happens within the LLM via prompting.
No explicit rules or structured state tracking in Python.
"""

import os
from dotenv import load_dotenv
from google import genai
from scraper import RecipeScraper
from prompts import get_system_prompt


class LLMRecipeAssistant:
    """
    Pure LLM-driven recipe assistant.
    Uses conversation history as the only context.
    """

    def __init__(self, model_name="gemini-2.0-flash-lite", temperature=1.0):
        """
        Initialize the LLM assistant.

        Args:
            model_name: Gemini model to use
            temperature: Sampling temperature (0.0 to 2.0)
        """
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        print(f"DEBUG: API key loaded: {self.api_key[:20] if self.api_key else 'None'}... (length: {len(self.api_key) if self.api_key else 0})")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.scraper = RecipeScraper()

        # Conversation history 
        self.conversation_history = []
        self.recipe_content = None
        self.recipe_url = None

    def load_recipe(self, url):
        """
        Load a recipe from URL and add it to conversation context.

        Args:
            url: Recipe URL to scrape

        Returns:
            bool: True if successful, False otherwise
        """
        print(f"\nFetching recipe from: {url}")
        recipe_data = self.scraper.fetch_recipe(url)

        if not recipe_data:
            print("Failed to fetch recipe. Please check the URL and try again.")
            return False

        self.recipe_url = url
        self.recipe_content = recipe_data['cleaned_html']

        # Add system prompt + recipe to conversation
        system_prompt = get_system_prompt()

        initial_message = f"""{system_prompt}

## RECIPE CONTENT

Recipe URL: {url}
Recipe Title: {recipe_data['title']}

Here is the HTML content of the recipe page (cleaned of scripts, styles, and navigation elements).
Use the HTML structure to accurately understand and extract recipe information:

{self.recipe_content}

---

The recipe has been loaded. You can now help the user navigate and understand this recipe.
Parse the HTML to identify ingredients, steps, tools, methods, times, and temperatures.
"""

        self.conversation_history = [
            {
                "role": "user",
                "parts": [{"text": initial_message}]
            },
            {
                "role": "model",
                "parts": [{"text": "I've loaded the recipe and I'm ready to help you cook! You can ask me to show you the ingredients, explain steps, navigate through the recipe, or answer any questions about the cooking process. What would you like to know?"}]
            }
        ]

        print(f"\nRecipe loaded: {recipe_data['title']}")
        print("\nI'm ready to help you cook! You can ask me questions about the recipe.")
        print("Try asking: 'Show me the ingredients', 'What's the first step?', 'How do I do that?', etc.")
        print("Type 'exit' to quit.\n")

        return True

    def chat(self, user_message):
        """
        Send a message to the LLM and get a response.

        Args:
            user_message: User's question or command

        Returns:
            str: LLM's response
        """
        # Check for exit
        if user_message.lower().strip() in ['exit', 'quit', 'bye']:
            return None

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })

        try:
            # Generate response using conversation history
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.conversation_history,
                config={
                    "temperature": self.temperature,
                    "max_output_tokens": 1000,
                }
            )

            # Extract response text
            if hasattr(response, 'text'):
                assistant_response = response.text
            else:
                assistant_response = response.candidates[0].content.parts[0].text

            # Add assistant response to history
            self.conversation_history.append({
                "role": "model",
                "parts": [{"text": assistant_response}]
            })

            return assistant_response

        except Exception as e:
            error_msg = f"Error communicating with LLM: {e}"
            print(error_msg)
            return error_msg

    def run_interactive(self):
        """
        Run interactive conversation loop.
        """
        # Get recipe URL
        print("=" * 60)
        print("LLM-Only Recipe Assistant")
        print("=" * 60)
        print("\nThis assistant uses pure LLM reasoning with no explicit rules.")
        print("All understanding comes from the language model and conversation history.\n")

        recipe_url = input("Enter recipe URL: ").strip()

        if not recipe_url:
            print("No URL provided. Exiting.")
            return

        # Load recipe
        if not self.load_recipe(recipe_url):
            return

        # Conversation loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                response = self.chat(user_input)

                if response is None:  # Exit command
                    print("\nAssistant: Thanks for cooking with me! Goodbye!")
                    break

                print(f"\nAssistant: {response}")

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue

    def run_single_turn(self, recipe_url, user_question):
        """
        Run a single question-answer turn 

        Args:
            recipe_url: Recipe URL to load
            user_question: Question to ask

        Returns:
            str: Assistant's response
        """
        if not self.load_recipe(recipe_url):
            return "Failed to load recipe."

        return self.chat(user_question)
