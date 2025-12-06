from spacy.tokenizer import Tokenizer 
from enum import Enum
import re
import spacy


class QuestionTypes(Enum):
    # recipe retrieval and display
    INGREDIENT_LIST = 1 # ex: "show me the ingredients list"
    TOOL_LIST       = 2 # ex: "show me what tools i'll need"
    METHOD_LIST     = 3 # ex: "what cooking techniques will i have to do?"
    STEP_LIST       = 18 # ex: "show me all the steps not implemented yet"
    # navigation utterances
    STEP_NEXT       = 4 # ex: "go to the next step"
    STEP_PREVIOUS   = 5 # ex: "go to the previous step"
    STEP_REPEAT     = 6 # ex: "repeat please"
    STEP_GOTO       = 7 # ex: "go to step n"
    # parameters of the current step
    QUANTITY        = 8 # ex: "how much of <ingredient> do I need?"
#     Please enter your question, if you want to exit, input "exit": goto step 4
# Step 4: cook and stir until beef is crumbly and evenly browned, about 10 minutes
# Please enter your question, if you want to exit, input "exit": how many beef
# You need 1 pound of lean ground beef.
    QUANTITY_VAGUE  = 19 # ex: "how much do I need?" – (use conversation history to infer which ingredient is being referred to)
    TEMPERATURE     = 9 # ex: "what temperature?" 
#     Please enter your question, if you want to exit, input "exit": goto step 1
# Step 1: Preheat the oven to 350 degrees F (175 degrees C)
# Please enter your question, if you want to exit, input "exit": what temperature
# The temperature mentioned for this step is: 350 degrees F
    TIME            = 10 # ex: "how long do i <specific technique>?"
#     Please enter your question, if you want to exit, input "exit": goto step 4
# Step 4: cook and stir until beef is crumbly and evenly browned, about 10 minutes
# Please enter your question, if you want to exit, input "exit": what time 
# The time mentioned for this step is: 10 minute
    DONENESS        = 11 # ex: "when is it done?"
    SUBSTITUION     = 12 # ex: "can i use <ingredient or tool> instead of <ingredient or tool>"
    # simple "what is", specific "how to", and vague "how to" questions
    WHAT_IS         = 13 # ex: "what is a <tool being mentioned>?"
#     Please enter your question, if you want to exit, input "exit": what is aab
# For information about 'aab', you can check the following links:
# Google: https://www.google.com/search?q=aab
# YouTube: https://www.youtube.com/results?search_query=aab
    HOW_TO_SPECIFIC = 14 # ex: "how do i <specific technique>?"
    HOW_TO_VAGUE    = 15 # ex: "how do i do that?" – (use conversation history to infer what “that” refers to)
    # none of the above
    UNKNOWN         = 16 # ex: "how is barack obama feeling this afternoon?"
    EXIT            = 17 # ex: "exit"

QUESTION_TYPE_DESCRIPTIONS = {
    "INGREDIENT_LIST": "Show or request the ingredient list for the recipe.",
    "TOOL_LIST": "Ask for tools or equipment needed.",
    "METHOD_LIST": "Ask about cooking techniques required in the recipe.",
    "STEP_LIST": "Ask for all remaining or full list of cooking steps.",
    
    "STEP_NEXT": "Move forward to the next step.",
    "STEP_PREVIOUS": "Go back to the previous step.",
    "STEP_REPEAT": "Repeat or reread the current step.",
    "STEP_GOTO": "Jump to a specific step number.",
    
    "QUANTITY": "Ask how much of a specific ingredient is needed.",
    "QUANTITY_VAGUE": "Ask 'how much?' without specifying ingredient — requires context to resolve.",
    
    "TEMPERATURE": "Ask what temperature to use for cooking.",
    "TIME": "Ask for duration or how long something should be cooked.",
    "DONENESS": "Ask how to tell when something is done.",
    
    "SUBSTITUTION": "Ask whether one ingredient or tool can replace another.",
    
    "WHAT_IS": "Ask for the definition or meaning of a tool or term.",
    "HOW_TO_SPECIFIC": "Ask how to perform a specific technique or action.",
    "HOW_TO_VAGUE": "Ask 'how do I do that?' where the reference must be inferred from context.",

    "NUTRITION": "Ask about nutritional information of the recipe or ingredients.",
    "INTRODUCTION": "Ask for an introduction or overview of the recipe.",
    
    "UNKNOWN": "Out-of-scope or unrelated questions not about cooking.",
    
    "EXIT": "Exit command — unused in this project; out-of-scope questions map to UNKNOWN."
}

INTENT_PROMPT = """
You are an intent classifier for a cooking assistant system.

Below is a set of intent labels and their meanings:

INGREDIENT_LIST: Show or request the ingredient list for the recipe.
TOOL_LIST: Ask for tools or equipment needed.
METHOD_LIST: Ask about cooking techniques required in the recipe.
STEP_LIST: Ask for all remaining or full list of cooking steps.
STEP_NEXT: Move forward to the next step.
STEP_PREVIOUS: Go back to the previous step.
STEP_REPEAT: Repeat or reread the current step.
STEP_GOTO: Jump to a specific step number.
QUANTITY: Ask how much of a specific ingredient is needed.
QUANTITY_VAGUE: Ask “how much?” without specifying ingredient — requires context to resolve.
TEMPERATURE: Ask what temperature to use.
TIME: Ask for duration or how long something should be cooked.
DONENESS: Ask how to tell when something is done.
SUBSTITUTION: Ask whether one ingredient or tool can replace another.
WHAT_IS: Ask for the definition or meaning of a tool or term.
HOW_TO_SPECIFIC: Ask how to perform a specific technique or action.
HOW_TO_VAGUE: Ask “how do I do that?” where the reference must be inferred from context.
INTRODUCTION: Ask for an introduction or overview of the recipe.
NUTRITION: Ask about nutritional information of the recipe or ingredients.
UNKNOWN: Out-of-scope or non-cooking question.
EXIT: Exit command — treat as UNKNOWN in this system.

Task:
Given the user's input, output ONLY the label (one of the keys above). 
Do NOT answer the question itself.
Do NOT output any explanation.
If the input is unrelated to cooking, output “UNKNOWN”.

User query:
"{user_query}"

Your output must be exactly one of the labels above, in uppercase, with no extra text.
"""

QA_PROMPT = """
You are a cooking QA assistant. Use ONLY the provided recipe data and conversation history.
user are intent to ask a question about {intent}

current step:
{current_step}

Recipe data (JSON):
{recipe_json}

Conversation history (oldest → newest):
{history}

User question:
{user_question}

Instructions:
- Answer concisely and directly.
- If a fact is missing from the recipe data, say you cannot find it rather than inventing it.
- If the user asks about a step, include the step number and description if available.
- you should find what step are user in based on the conversation history.
- Do not include the prompt contents in your reply; return only the final answer text.
finally, if you think the step number has changed, update the current step number accordingly in your answer. output the format " [STEP n]" where n is the new current step number. If the step number remains the same, do not include this in your answer.
"""

YOUTUBE_PROMPT = """
You are a cooking assistant that provides YouTube search links for cooking techniques or tools.
You are asked to generate a YouTube search URL based on the user's query.   
Now youneed to identify what user want to search on YouTube based on the user question and conversation history.

current step:
{current_step}

Recipe data (JSON):
{recipe_json}

Conversation history (oldest → newest):
{history}

User question:
{user_question}

Instructions:
- Answer concisely and directly.
- If a fact is missing from the recipe data, say you cannot find it rather than inventing it.
- If the user asks about a step, include the step number and description if available.
- you should find what step are user in based on the conversation history.
- Do not include the prompt contents in your reply; return only the final answer text.
you should return a word or a phrase that best represents what user want to search on YouTube.
"""


ordinal_words = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "last": -1,     # special marker for last step
    "final": -1,    # final step = last step
}

numeric_words = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10
}

class QA:
    def __init__(self, LLM_model):
        self.model = None # JSON of extracted recipe data
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
        self.LLM_model = LLM_model
        self.use_llm_agent = False
        self.history = [] # what has been inputted (and outputted) already
        self.current_step = 0 # current step number being executed
        self.question_types = QuestionTypes
        self.nlp = spacy.load("en_core_web_sm")
        self.max_step = 0

    def same_word(self, a, b):
        return self.nlp(a)[0].lemma_.lower() == self.nlp(b)[0].lemma_.lower()

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
        if "steps" in lemmas_set or "step list" in q or "recipe" in lemmas_set:
            return QuestionTypes.STEP_LIST

        if "next step" in q or ("next" in lemmas_set and "step" in lemmas_set) or "what's next" in q:
            return QuestionTypes.STEP_NEXT
        if "previous" in lemmas_set or "back" in lemmas_set:
            return QuestionTypes.STEP_PREVIOUS
        if "repeat" in lemmas_set or "again" in lemmas_set:
            return QuestionTypes.STEP_REPEAT
        if re.search(r"\bstep\s+(\d+)\b", q):
            return QuestionTypes.STEP_GOTO

        # "step two" / "step one" / "step five"
        if any(re.search(rf"\bstep\s+{w}\b", q) for w in numeric_words.keys()):
            return QuestionTypes.STEP_GOTO

        # "first step" / "second step" / "last step"
        if any(re.search(rf"\b{w}\s+step\b", q) for w in ordinal_words.keys()):
            return QuestionTypes.STEP_GOTO

        # forms like "go to the first" / "go to the second"
        if any(re.search(rf"\b{w}\b", q) and "step" in q for w in ordinal_words.keys()):
            return QuestionTypes.STEP_GOTO

        if "how much" in q or "quantity" in lemmas_set or "how many" in q or "quantity" in lemmas_set or "amount" in lemmas_set:
            if "that" in q or "it" in q:
                return QuestionTypes.QUANTITY_VAGUE
            else:
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
            if "that" in q or "it" in q:
                return QuestionTypes.HOW_TO_VAGUE
            else:
                return QuestionTypes.HOW_TO_SPECIFIC
        if q == "exit":
            return QuestionTypes.EXIT
        
        # more logic needed here, esp with context
        '''
        return QuestionTypes.HOW_TO_VAGUE
        '''
        
        # if unidentifiable
        return QuestionTypes.UNKNOWN
    
    def extract_step_number(self, q):
        q = q.lower()

        # 1. explicit numeric: "step 3"
        m = re.search(r"\bstep\s+(\d+)\b", q)
        if m:
            return int(m.group(1))

        # 2. numeric words: “step two”
        for word, num in numeric_words.items():
            if re.search(rf"\bstep\s+{word}\b", q):
                return num

        # 3. ordinal: “first step”
        for word, num in ordinal_words.items():
            if re.search(rf"\b{word}\s+step\b", q):
                return num

        # 4. ordinal appearing with step in sentence
        for word, num in ordinal_words.items():
            if word in q and "step" in q:
                return num

        # 5. last/final
        if "last step" in q or "final step" in q:
            return -1

        return None


    def _extractor(self, question, question_type):
        q = question.lower().strip()
        # extract ingredient/tool/etc mentioned after "of", "for", "about", etc
        def extract_keyword(q, candidates):
            for c in candidates:
                if c.lower() in q:
                    return c
            return None

        if question_type == self.question_types.INGREDIENT_LIST:
            return {"items": self.model["Ingredients"]}
        if question_type == self.question_types.TOOL_LIST:
            return {"items": self.model["Tools"]}
        if question_type == self.question_types.METHOD_LIST:
            return {"items": self.model["Methods"]}
        if question_type == self.question_types.STEP_LIST:
            return {"items": self.model["Steps"]}

        if question_type == self.question_types.STEP_NEXT:
            if self.current_step != self.max_step:
                return {"nav": self.model["Steps"][self.current_step]}
            else:
                return {"nav": None}  # already at last step
        if question_type == self.question_types.STEP_PREVIOUS:
            if self.current_step > 1:
                return {"nav": self.model["Steps"][self.current_step - 1]}
            else:
                return {"nav": None}  # already at first step
        if question_type == self.question_types.STEP_REPEAT:
            if self.current_step >= 1 and self.current_step <= self.max_step:
                return {"nav": self.model["Steps"][self.current_step - 1]}
            else:
                return {"nav": None}  # invalid current step
        if question_type == self.question_types.STEP_GOTO:
            step_num = self.extract_step_number(q)
            return {"nav": "goto", "step_number": step_num}

        if question_type == self.question_types.QUANTITY:
            step = self.model["Steps"][self.current_step - 1]
            
            for ing in self.model["Ingredients"]:
                ingredients_name = []
                for ing2 in ing["name"].split():
                    ingredients_name.append(ing2.lower())
                for ing3 in ingredients_name:
                    if ing3 in q:
                        return {"ingredient": ing}

            return {"ingredient": None}

        if question_type == self.question_types.QUANTITY_VAGUE:

            # case 1: previous question was QUANTITY → repeat last ingredient
            if len(self.history) > 0 and self.history[-1]["type"] == self.question_types.QUANTITY:
                return self.history[-1]["relevant"]

            # case 2: infer ingredient from current step
            step = self.model["Steps"][self.current_step - 1]
            if step["ingredients"]:
                for ing_name in step["ingredients"]:
                    for ing in self.model["Ingredients"]:
                        if self.same_word(ing_name, ing["name"]):
                            return {"ingredient": ing}
            return {"ingredient": None}
        if question_type == self.question_types.TEMPERATURE:
            step = self.model["Steps"][self.current_step - 1]
            if step["temperature"] is not None:
                return {"temperature": step["temperature"]}
            else:
                return {"temperature": None}
        if question_type == self.question_types.TIME:
            step = self.model["Steps"][self.current_step - 1]
            if step["time"] is not None:
                return {"time": step["time"]}
            else:
                return {"time": None}
        if question_type == self.question_types.DONENESS:
            target = extract_keyword(q, self.model["Ingredients"] + self.model["Methods"])
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

        if question_type == self.question_types.HOW_TO_VAGUE:
            # NEEDS CONTEXTUAL UNDERSTANDING, SKIPPING FOR NOW
            step = self.model["Steps"][self.current_step - 1]
            if step["methods"]:
                return {"action": step["methods"]}  # return all methods in current step as guess
            else:
                return {"action": None}
        
        if question_type == self.question_types.EXIT:
            return {}

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
        
    """
    # if desired type requires video (like HOW_TO), then get Google or Youtube URL
    self._external_media_finder(q_data)
    """

    def agent(self, q_data) -> int:  # if exit, return -1; else return 0
        q_type = q_data["type"]

        # ---------- Recipe Retrieval ----------
        if q_type == self.question_types.INGREDIENT_LIST: # ok
            ingredients = q_data["relevant"]["items"]
            print("Here are all the ingredients called for:")
            for ing in ingredients:
                print(ing["full_text"])

        elif q_type == self.question_types.TOOL_LIST: # ok
            tools = q_data["relevant"]["items"]
            print("Here are all the tools called for:")
            print(*tools, sep="\n")

        elif q_type == self.question_types.METHOD_LIST: # ok
            methods = q_data["relevant"]["items"]
            print("Here are all the methods called for:")
            print(*methods, sep="\n")

        elif q_type == self.question_types.STEP_LIST: # ok
            print("Here are all the steps in the recipe that you have not completed yet:")
            step_list = q_data["relevant"]["items"]
            for step in step_list:
                if step["step_number"] > self.current_step:
                    print(f"Step {step['step_number']}: {step['description']}")

        # ---------- Navigation ----------
        elif q_type == self.question_types.STEP_NEXT: # ok
            nav_data = q_data["relevant"]["nav"]
            if nav_data is None:
                print("You are already at the last step.")
            else:
                self.current_step += 1
                print(f"Step {self.current_step}: {nav_data['description']}")
 
        elif q_type == self.question_types.STEP_PREVIOUS: # ok
            nav_data = q_data["relevant"]["nav"]
            if nav_data is None:
                print("You are already at the first step.")
            else:
                self.current_step -= 1
                print(f"Step {self.current_step}: {nav_data['description']}")

        elif q_type == self.question_types.STEP_REPEAT: # ok
            nav_data = q_data["relevant"]["nav"]
            if nav_data is None:
                print("There is no current step to repeat. You may start steps by going to the next step.")
            else:
                print(f"Step {self.current_step}: {nav_data['description']}")

        elif q_type == self.question_types.STEP_GOTO: # ok
            step_num = q_data["relevant"]["step_number"]
            if step_num is None:
                print("I couldn't determine which step you wanted to go to.")
            else:
                if step_num == -1:  # last step
                    step_num = self.max_step
                if 1 <= step_num <= self.max_step:
                    self.current_step = step_num
                    nav_data = self.model["Steps"][self.current_step - 1]
                    print(f"Step {self.current_step}: {nav_data['description']}")
                else:
                    print(f"Step {step_num} is out of range. This recipe has {self.max_step} steps.")

        # ---------- Step Parameter Queries ----------
        elif q_type == self.question_types.QUANTITY: # part ok
            if self.current_step == 0:
                print("You are not currently on any step. Please navigate to a step first.")
                return 0
            ingredient = q_data["relevant"]["ingredient"]
            if ingredient is None:
                print("I couldn't determine which ingredient you were asking about.")
            else:
                print(f"You need {ingredient['quantity']} {ingredient['measurement']} of {ingredient['name']}.")

        elif q_type == self.question_types.QUANTITY_VAGUE:
            if self.current_step == 0:
                print("You are not currently on any step. Please navigate to a step first.")
                return 0
            ingredient = q_data["relevant"]["ingredient"]
            if ingredient is None:
                print("I couldn't determine which ingredient you were asking about.")
            else:
                print(f"You need {ingredient['quantity']} {ingredient['measurement']} of {ingredient['name']}.")

        elif q_type == self.question_types.TEMPERATURE:
            if self.current_step == 0:
                print("You are not currently on any step. Please navigate to a step first.")
                return 0
            if q_data["relevant"]["temperature"] is None:
                print("There is no specific temperature mentioned for this step.")
            else:
                print(f"The temperature mentioned for this step is: {q_data['relevant']['temperature']}")

        elif q_type == self.question_types.TIME:
            if self.current_step == 0:
                print("You are not currently on any step. Please navigate to a step first.")
                return 0
            if q_data["relevant"]["time"] is None:
                print("There is no specific time mentioned for this step.")
            else:
                print(f"The time mentioned for this step is: {q_data['relevant']['time']}")

        elif q_type == self.question_types.DONENESS:
            pass

        # ---------- Other Questions ----------
        elif q_type == self.question_types.SUBSTITUION:
            pass

        elif q_type == self.question_types.WHAT_IS:
            # Extract the term the user is asking about
            term = q_data["relevant"]["term"]  # example: "whisk", "baking soda"
            
            # Build search query
            query = term.replace(" ", "+")
            
            # Return external knowledge links
            google_url = f"https://www.google.com/search?q={query}"
            youtube_url = f"https://www.youtube.com/results?search_query={query}"

            print(f"For information about '{term}', you can check the following links:")

            print(f"Google: {google_url}")
            print(f"YouTube: {youtube_url}")


        elif q_type == self.question_types.HOW_TO_SPECIFIC:
            term = q_data["relevant"]["action"]  # example: "whisk eggs", "bake a cake"
            query = term.replace(" ", "+")
            
            google_url = f"https://www.google.com/search?q={query}"
            youtube_url = f"https://www.youtube.com/results?search_query={query}"

            print(f"For instructions on how to {term}, you can check the following links:")

            print(f"Google: {google_url}")
            print(f"YouTube: {youtube_url}")

        elif q_type == self.question_types.HOW_TO_VAGUE:
            methods = q_data["relevant"]["action"]
            if methods is None:
                print("I couldn't determine what action you were referring to.")
            else:
                print("I guess you are asking how to do the following methods:")
                for method in methods:
                    query = method.replace(" ", "+")
                    
                    google_url = f"https://www.google.com/search?q={query}"
                    youtube_url = f"https://www.youtube.com/results?search_query={query}"

                    print(f"For instructions on how to {method}, you can check the following links:")

                    print(f"Google: {google_url}")
                    print(f"YouTube: {youtube_url}")
                    print("------------------------------")

        # ---------- Exit ----------
        elif q_type == self.question_types.EXIT:
            print("Exiting the QA system. Goodbye!")
            return -1

        # ---------- Unknown ----------
        else:
            print("I'm not sure how to answer that.")

        return 0

    def speech_to_text(self):
    # Implement speech-to-text logic here
        pass

    def _add_to_history(self, q_data):
        if self.use_llm_agent:
            self.history.append(q_data)
        else:
            history_item = {
                "question": q_data["question"],
                "type": q_data["type"],
                "relevant": q_data["relevant"],
                "step": self.current_step,
            }
            self.history.append(history_item)

    def state_tracking(self, history):
        prompt = f"Based on the following conversation history, track the current step number in the recipe:{history}, Your output should be the current step number only."
        response = self.LLM_model.generate_content(
            model = "gemini-2.5-flash-lite",
            contents = prompt
        )

        print(f"State Tracking LLM Response: {response}")
        print("True step number:", self.current_step)
        print(f"Prompt: {prompt}")

    def llm_agent(self, question) -> int:
        if question.lower().strip() == "exit":
            return -1
        
        # get intent
        prompt = INTENT_PROMPT.format(user_query=question)
        intent_response = self.LLM_model.generate_content(
            model = "gemini-2.5-flash-lite",
            contents = prompt
        )
        intent_label = intent_response.candidates[0].content.parts[0].text

        if intent_label not in QUESTION_TYPE_DESCRIPTIONS:
            intent_label = "UNKNOWN"

        if intent_label == "EXIT":
            return -1
        
        if intent_label == "UNKNOWN":
            print("I'm not sure how to answer that.")
            return 0
        def youtube_search(query: str) -> str:
            """Return a YouTube search URL for a given query."""
            base_url = "https://www.youtube.com/results?search_query="
            formatted_query = query.strip().replace(" ", "+")
            return f"{base_url}{formatted_query}"

        if intent_label in ["HOW_TO_SPECIFIC", "WHAT_IS", "HOW_TO_VAGUE"]:
            qa_prompt = YOUTUBE_PROMPT.format(
                current_step = self.current_step,
                recipe_json = self.model,
                history = self.history,
                user_question = question
            )
            qa_response = self.LLM_model.generate_content(
                model = "gemini-2.5-flash-lite",
                contents = qa_prompt
            )
            target = qa_response.candidates[0].content.parts[0].text
            youtube_url = youtube_search(target)
            print(f"For information about '{target}', you can check the following link:")
            print(f"YouTube: {youtube_url}")
            return 0

        # get answer
        qa_prompt = QA_PROMPT.format(
            current_step = self.current_step,
            intent = QUESTION_TYPE_DESCRIPTIONS[intent_label],
            recipe_json = self.model,
            history = self.history,
            user_question = question
        )

        answer_response = self.LLM_model.generate_content(
            model = "gemini-2.5-flash-lite",
            contents = qa_prompt
        )
        answer_text = answer_response.candidates[0].content.parts[0].text
        # Extract updated step number if present in the format " [STEP n]"
        step_match = re.search(r"\[STEP\s+(\d+)\]", answer_text)
        if step_match:
            new_step = int(step_match.group(1))
            if 1 <= new_step <= self.max_step:
                self.current_step = new_step
            # Remove the step update notation from the answer text
            answer_text = re.sub(r"\s*\[STEP\s+\d+\]", "", answer_text)
        print(f"LLM QA Response: {answer_text}")

        history_data = {
            "question": question,  
            "type": intent_label,
            "answer": answer_text
        }
        return history_data

    # QA main loop here
    def run(self):
        if self.model is None:
            while True:
                print("Use LLM or not for question answering? (y/n)")
                choice = input().strip().lower()
                if choice == 'y':
                    self.use_llm_agent = True
                    break
                elif choice == 'n':
                    self.use_llm_agent = False
                    break
                else:
                    print("Invalid choice. Please enter 'y' or 'n'.")
            if not self.use_llm_agent:

                while True:
                    print("Please input a URL for recipe parsing first, the URL must from AllRecipes.com")
                    URL = input("Enter recipe URL: ")
                    pattern = r'^https?://(www\.)?allrecipes\.com/.*$'
                    if re.match(pattern, URL):
                        from parser import Parser
                        try:
                            self.model = Parser(URL, self.LLM_model).parse(use_LLM=False)
                            print("Recipe data successfully parsed and loaded.")
                            self.max_step = len(self.model["Steps"])
                            break
                        except Exception as e:
                            print(f"Error parsing recipe: {e}")
                    else:
                        print("Invalid URL. Please try again.")
            else:
                while True:
                    print("Please input a URL for recipe parsing first, the URL must from AllRecipes.com")
                    URL = input("Enter recipe URL: ")
                    from parser import Parser
                    try:
                        self.model = Parser(URL, self.LLM_model).parse(use_LLM=True)
                        print("Recipe data successfully parsed and loaded.")
                        self.max_step = len(self.model["Steps"])
                        break
                    except Exception as e:
                        print(f"Error parsing recipe: {e}")

            
        while True:
            """
            # maybe speech to text for input?
            input = self.speech_to_text()
            question_parsed_data = self.question_parser(input)
            """
            # get_question()
            if not self.use_llm_agent:
                question_parsed_data = self.question_parser(input("Please enter your question, if you want to exit, input \"exit\": "))

                # handle data and choose appropriate response by calling agent()
                # status = self.agent(question_parsed_data)
                status = self.agent(question_parsed_data)
                if status == -1:
                    break
                self._add_to_history(question_parsed_data)
            else:

                llm_response = self.llm_agent(input("Please enter your question, if you want to exit, input \"exit\": "))
                if llm_response == -1:
                    break
                self._add_to_history(llm_response)
            # update memory i.e. state tracking
            
            # print(question_parsed_data)
            # if self.current_step != 0:
            #     self.state_tracking(self.history)

        print("QA session ended.")