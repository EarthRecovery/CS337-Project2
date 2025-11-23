from spacy.tokenizer import Tokenizer 
from enum import Enum
import re
import spacy

class QuestionTypes(Enum):
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

        # create token lists/sets (lemmas used generalizability)
        token_lemmas = [token.lemma_.lower() for token in doc]
        lemmas_set = set(token_lemmas)

        # basic conditions added, ADD MORE LATER (NUANCE)
        if re.search(r"\bingredients?\b", q):
            return QuestionTypes.INGREDIENT_LIST
        if re.search(r"\btools?\b", q) or "equipment" in lemmas_set:
            return QuestionTypes.TOOL_LIST
        if "technique" in lemmas_set or "method" in lemmas_set or "cooking technique" in q:
            return QuestionTypes.METHOD_LIST

        if "next step" in q or ("next" in lemmas_set and "step" in lemmas_set):
            return QuestionTypes.STEP_NEXT
        if "previous" in lemmas_set or "back" in lemmas_set:
            return QuestionTypes.STEP_PREVIOUS
        if "repeat" in lemmas_set:
            return QuestionTypes.STEP_REPEAT
        if re.search(r"\bstep\s+(\d+)", q):
            return QuestionTypes.STEP_GOTO

        if "how much" in q or "quantity" in lemmas_set or "amount" in lemmas_set:
            return QuestionTypes.QUANTITY
        if "heat" in lemmas_set or re.search(r"\btemp(?:erature)?\b", q):
            return QuestionTypes.TEMPERATURE
        if "how long" in q or "time" in lemmas_set:
            return QuestionTypes.TIME
        if "done" in lemmas_set or "ready" in lemmas_set or "finished" in lemmas_set or (re.search(r"\bwhen is\b", q) and re.search(r"\b(done|ready)\b", q)):
            return QuestionTypes.DONENESS

        if "instead of" in q or "replace" in lemmas_set or "substitute" in lemmas_set:
            return QuestionTypes.SUBSTITUION
        if q.startswith("what is") or q.startswith("what's"):
            return QuestionTypes.WHAT_IS
        if q.startswith("how do"):
            return QuestionTypes.HOW_TO_SPECIFIC
        
        # more logic needed here, esp with context
        '''
        return QuestionTypes.HOW_TO_VAGUE
        '''
        
        # if unidentifiable
        return QuestionTypes.UNKNOWN


    def _extractor(self, question, question_type):
        q = question.lower().strip()

        # extract an integer after "step n"
        def extract_step_number(q):
            m = re.search(r"\bstep\s+(\d+)", q)
            if m:
                return int(m.group(1))  
            else:
                return None
        # extract ingredient/tool/etc mentioned after "of", "for", "about", etc
        def extract_keyword(q, candidates):
            for c in candidates:
                if c.lower() in q:
                    return c
            return None

        # flatten lists from model
        all_ingredients = []
        all_tools = []
        for step in self.model:
            all_ingredients.extend(step.get("ingredients", []))
            all_tools.extend(step.get("tools", []))

        if question_type == self.question_types.INGREDIENT_LIST:
            return {"items": all_ingredients}
        if question_type == self.question_types.TOOL_LIST:
            return {"items": all_tools}
        if question_type == self.question_types.METHOD_LIST:
            methods = []
            for step in self.model:
                methods.extend(step.get("methods", []))
            return {"items": methods}

        if question_type == self.question_types.STEP_NEXT:
            return {"nav": "next"}
        if question_type == self.question_types.STEP_PREVIOUS:
            return {"nav": "previous"}
        if question_type == self.question_types.STEP_REPEAT:
            return {"nav": "repeat"}
        if question_type == self.question_types.STEP_GOTO:
            step_num = extract_step_number(q)
            return {"nav": "goto", "step_number": step_num}

        if question_type == self.question_types.QUANTITY:
            ing = extract_keyword(q, all_ingredients)
            return {"ingredient": ing}
        if question_type == self.question_types.TEMPERATURE:
            temp_target = extract_keyword(q, all_ingredients + ["oven"])
            return {"target": temp_target}
        if question_type == self.question_types.TIME:
            method = extract_keyword(q, [m for step in self.model for m in step.get("methods", [])])
            return {"method": method}
        if question_type == self.question_types.DONENESS:
            target = extract_keyword(q, all_ingredients + [m for step in self.model for m in step.get("methods", [])])
            return {"target": target}

        # MORE LOGIC REQUIRED FOR ALL 3, THIS IS SIMPLE TO (try and) GET CODE RUNNING
        if question_type == self.question_types.SUBSTITUION:
            m = re.search(r"use (.*?) instead of (.*)", q)
            if m:
                return {
                    "new": m.group(1).strip(),
                    "old": m.group(2).strip()
                }
            return {"new": None, "old": None}
        if question_type == self.question_types.WHAT_IS:
            m = re.search(r"(what is|what's)\s+(.*)", q)
            if m:
                term = m.group(2).rstrip("?").strip()
                return {"term": term}
            return {"term": None}
        if question_type == self.question_types.HOW_TO_SPECIFIC:
            m = re.search(r"how do i (.*)", q)
            if m:
                action = m.group(1).rstrip("?").strip()
                return {"action": action}
            return {"action": None}

        # MORE LOGIC REQUIRED
        """
        # vague "how do I do that?"
        if question_type == self.question_types.HOW_TO_VAGUE:
            return {"refer_to_history": True}
        """

        # fallback (i.e. if UNKNOWN)
        return {}


    def question_parser(self, question):
        question_type = self._classify_question(question)
        relevant = self._extractor(question, question_type)
        return {"question": question,       # verbatim question
                "type":     question_type,  # question type
                "relevant": relevant        # revelant context (different for each question)
                }
        """
        relevant has the follow types: "items", "nav", "ingrediant", "target", "method", "term", "action", and "new" "old" pairs
                                                  ^(navigation commands)                                        ^(for substitution)
        """


    ### helper functions for agent ###

    def _external_media_finder(self, q_data):
        pass

    def _agent_ingredient_list(self, q_data):
        ingredients = self.model["ingredients"]
        print("Here are all the ingredients called for:")
        print(*ingredients, sep="\n")
    def _agent_tool_list(self, q_data):
        tools = self.model["tools"]
        print("Here are all the tools called for:")
        print(*tools, sep="\n")
    def _agent_method_list(self, q_data):
        methods = self.model["methods"]
        print("Here are all the methods called for:")
        print(*methods, sep="\n")

    def _agent_step_next(self, q_data):
        pass
    def _agent_step_previous(self, q_data):
        pass
    def _agent_step_repeat(self, q_data):
        pass
    def _agent_step_goto(self, q_data):
        pass
    def _agent_quantity(self, q_data):
        pass
    def _agent_temperature(self, q_data):
        pass
    def _agent_time(self, q_data):
        pass
    def _agent_doneness(self, q_data):
        pass
    def _agent_substitution(self, q_data):
        pass
    def _agent_what_is(self, q_data):
        pass
    def _agent_how_to_specific(self, q_data):
        pass
    def _agent_how_to_vague(self, q_data):
        pass
        
    """
    # if desired type requires video (like HOW_TO), then get Google or Youtube URL
    self._external_media_finder(q_data)
    """

    def agent(self, q_data):
        q_type = q_data["type"]

        if q_type == self.question_types.INGREDIENT_LIST:
            self._agent_ingredient_list(q_data)
        if q_type == self.question_types.TOOL_LIST:
            self._agent_tool_list(q_data)
        if q_type == self.question_types.METHOD_LIST:
            self._agent_method_list(q_data)

        if q_type == self.question_types.STEP_NEXT:
            self._agent_step_next(q_data)
        if q_type == self.question_types.STEP_PREVIOUS:
            self._agent_step_previous(q_data)
        if q_type == self.question_types.STEP_REPEAT:
            self._agent_step_repeat(q_data)
        if q_type == self.question_types.STEP_GOTO:
            self._agent_step_goto(q_data)

        if q_type == self.question_types.QUANTITY:
            self._agent_quantity(q_data)
        if q_type == self.question_types.TEMPERATURE:
            self._agent_temperature(q_data)
        if q_type == self.question_types.TIME:
            self._agent_time(q_data)
        if q_type == self.question_types.DONENESS:
            self._agent_doneness(q_data)

        if q_type == self.question_types.SUBSTITUION:
            self._agent_substitution(q_data)
        if q_type == self.question_types.WHAT_IS:
            self._agent_what_is(q_data)
        if q_type == self.question_types.HOW_TO_SPECIFIC:
            self._agent_how_to_specific(q_data)
        if q_type == self.question_types.HOW_TO_VAGUE:
            self._agent_how_to_vague(q_data)

        # if UNKNOWN
        return "I'm not sure how to answer that."

    def speech_to_text(self):
    # Implement speech-to-text logic here
        pass

    # QA main loop here
    def run(self):
        while True:
            """
            # maybe speech to text for input?
            input = self.speech_to_text()
            question_parsed_data = self.question_parser(input)
            """
            # get_question()
            question_parsed_data = self.question_parser(input("Please enter your question: "))

            # handle data and choose appropriate response by calling agent()
            self.agent(question_parsed_data)

            # update memory i.e. state tracking
            """function here"""


    ##################### TESTING #####################


    @staticmethod
    def _test_question(question):
        # mock model
        model = [
            {
                "step_number": 1,
                "description": "Chop onions and heat olive oil.",
                "ingredients": ["onions", "olive oil"],
                "tools": ["knife", "cutting board"],
                "methods": ["chop", "heat"],
                "time": {"duration": "5 minutes"},
                "temperature": {"oven": None},
                "context": {"references": [], "warnings": []}
            },
            {
                "step_number": 2,
                "description": "Saute the onions until golden.",
                "ingredients": ["onions"],
                "tools": ["pan", "spatula"],
                "methods": ["saute"],
                "time": {"duration": "8 minutes"},
                "temperature": {"pan": "medium heat"},
                "context": {"references": [1], "warnings": []}
            }
        ]
        qa = QA(model)
        parsed = qa.question_parser(question)

        # print results
        print("\n")
        print("input:", question)
        print("detected type:", parsed["type"].name)
        print("relevant info extracted", parsed["relevant"])

    @staticmethod
    def run_test_suite():
        # bunch of questions (ADD MORE ONCE FIXED)
        test_questions = [
            "show me the ingredients list",
            "what tools do I need?",
            "what cooking technique is used in step 1?",
            "go to the next step",
            "go to step 2",
            "how much onions do I need?",
            "what temperature should I heat the oil?", 
            "how long do I saute?",
            "when is it done?",                         
            "can I use butter instead of olive oil?",
            "what is a spatula?",
            "how do I chop the onions?",
            "how do I do that?",                        # HOW_TO_VAGUE not implimented yet
            "who is obama?",
            "what is obama's first name?"               # nonsense WHAT_IS type question -- fix?
        ]

        # test all the questions above
        for question in test_questions:
            QA._test_question(question)

    def run_one_turn(self, question):
        # only for testing purposes
        pass 


if __name__ == "__main__":
    QA.run_test_suite()