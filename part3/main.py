import parser
import qa
from dotenv import load_dotenv
import os
from google import genai

class LLM_Model:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in your .env file.")
        
        # Keep a reference to the client so its underlying HTTP session
        # remains open while QA runs.
        self.client = genai.Client(api_key=self.api_key)
        self.model = self.client.models

def pipeline():

    LLM_model = LLM_Model()
    qa_model = qa.QA(LLM_model.model)   
    qa_model.run()
    # qa_model.run_one_turn("What is the first step?")

if __name__ == "__main__":
    pipeline()