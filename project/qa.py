from spacy.tokenizer import Tokenizer 
import re
import spacy

class QuestionTypes():
    # recipe retrieval and display
    INGREDIENT_LIST = 1 # ex: "show me the ingredients list"
    TOOL_LIST       = 2 # ex: "show me what tools i'll need"
    METHOD_LIST     = 3 # ex: "what cooking techniques will i have to do?"
    # navigation utterances
    STEP_NEXT       = 4 # ex: "go to the next step"
    STEP_PREVIOUS   = 5 # ex: "go to the previous step"
    STEP_REPEAT     = 6 # ex: "repeat please"
    STEP_GOTO       = 7 # ex: "go to step n"
    # parameters of the current step
    QUANTITY        = 8 # ex: "how much of <ingredient> do I need?"
    TEMPERATURE     = 9 # ex: "what temperature?" 
    TIME            = 10 # ex: "how long do i <specific technique>?"
    DONENESS        = 11 # ex: "when is it done?"
    SUBSTITUION     = 12 # ex: "can i use <ingredient or tool> instead of <ingredient or tool>"
    # simple "what is", specific "how to", and vague "how to" questions
    WHAT_IS         = 13 # ex: "what is a <tool being mentioned>?"
    HOW_TO_SPECIFIC = 14 # ex: "how do i <specific technique>?"
    HOW_TO_VAGUE    = 15 # ex: "how do i do that?" – (use conversation history to infer what “that” refers to)
    # none of the above
    UNKNOWN         = 16 # ex: "how is barack obama feeling this afternoon?"

class QA:
    def __init__(self, model):
        self.model = model # JSON of extracted recipe data
        """
        {
            "step_number": int,
            "description": str,
            "ingredients": [list of ingredient names],
            "tools": [list of tools],
            "methods": [list of methods],
            "time": {
                "duration": str or dict of sub-times,
            },
            "temperature": {
                "oven": str (optional),
                "<ingredient>": str (optional)
            },
            "context": {
                "references": [related step numbers or preconditions],
                "warnings": [list of warnings or advice] (optional)
            }
        }
        """
        self.history = {} # what has been inputted (and outputted) already
        self.question_types = QuestionTypes
        self.nlp = spacy.load("en_core_web_sm")

    def _classify_question(self, question):
        # simple tokenization and lowercasing
        q = question.lower().strip()
        doc = self.nlp(q)
        tokens = [token for token in doc]

        # basic conditions added, ADD MORE LATER (NUEANCE)
        if "ingredient" in tokens:
            return QuestionTypes.INGREDIENT_LIST
        if "tool" in tokens or "equipment" in tokens:
            return QuestionTypes.TOOL_LIST
        if "technique" in tokens or "method" in tokens or "cooking technique" in q:
            return QuestionTypes.METHOD_LIST

        if "next step" in q or ("next" in tokens and "step" in tokens):
            return QuestionTypes.STEP_NEXT
        if "previous" in tokens or "back" in tokens:
            return QuestionTypes.STEP_PREVIOUS
        if "repeat" in tokens:
            return QuestionTypes.STEP_REPEAT
        if re.search(r"\bstep\s+(\d+)", q):
            return QuestionTypes.STEP_GOTO

        if "how much" in q or "quantity" in tokens or "amount" in tokens:
            return QuestionTypes.QUANTITY
        if "temperature" in tokens or "heat" in tokens:
            return QuestionTypes.TEMPERATURE
        if "how long" in q or "time" in tokens:
            return QuestionTypes.TIME
        if "done" in tokens or "ready" in tokens or "finished" in tokens:
            return QuestionTypes.DONENESS

        if "instead of" in q or "replace" in tokens or "substitute" in tokens:
            return QuestionTypes.SUBSTITUION
        if q.startswith("what is") or q.startswith("what's"):
            return QuestionTypes.WHAT_IS
        if q.startswith("how do"):
            return QuestionTypes.HOW_TO_SPECIFIC
        
        # more logic needed here
        '''
        return QuestionTypes.HOW_TO_VAGUE
        '''
        
        # if unidentifiable
        return QuestionTypes.UNKNOWN


    def _extractor(self, question, question_type):
        pass

    def question_parser(self, question):
        question_type = self._classify_question(question)
        relevant = self._extractor(question, question_type)
        return {"question": question,       # verbatim question
                "type":     question_type,  # question type
                "relevant": relevant        # revelant context
                }

    def run(self):
        # Implement QA main loop here
        while True:
            # maybe speech to text
            # get_question()
            question_parsed_data = self.question_parser(input("Please enter your question: "))

            # handle data and choose appropriate response
            # look from parser data or get url/youtube by calling agent()

            # output the answer

    def agent(self, question):
        # Implement agent logic, get Google URL or Youtube link
        pass

    def speech_to_text(self):
        # Implement speech-to-text logic here
        pass

    def run_one_turn(self,question):
        # only for testing purposes
        pass 