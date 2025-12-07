"""
Entry point for Part 2: LLM-Only Recipe Assistant.

This system uses pure prompt-driven LLM reasoning with no explicit rules.
All decision-making happens within the LLM via the unified system prompt.
"""

from llm_assistant import LLMRecipeAssistant


def main():
    """
    Run the LLM-only recipe assistant.
    """
    # Initialize assistant with recommended model and settings
    assistant = LLMRecipeAssistant(
        model_name="gemini-2.0-flash-lite",  
        temperature=1.0  # Default temperature
    )

    # Run interactive conversation
    assistant.run_interactive()


if __name__ == "__main__":
    main()
