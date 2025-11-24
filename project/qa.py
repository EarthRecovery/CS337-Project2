from spacy.tokenizer import Tokenizer 
from enum import Enum
import re
import spacy

# {'Directions': {'step_1': 'Preheat the oven to 350 degrees F (175 degrees C).',
#                 'step_2': 'Bring a large pot of lightly salted water to a '
#                           'boil. Add lasagna noodles and cook for 10 minutes '
#                           'or until al dente; drain.',
#                 'step_3': 'Meanwhile, place ground beef, garlic, oregano, '
#                           'garlic powder, salt, and black pepper in a large '
#                           'skillet over medium heat; cook and stir until beef '
#                           'is crumbly and evenly browned, about 10 minutes.',
#                 'step_4': 'Mix cottage cheese, Parmesan cheese, and eggs '
#                           'together in a large bowl until thoroughly combined.',
#                 'step_5': 'Lay 4 noodles side by side on the bottom of a '
#                           '9x13-inch baking pan; top with a layer of prepared '
#                           'tomato-basil sauce, a layer of ground beef mixture, '
#                           'and a layer of cottage cheese mixture. Repeat '
#                           'layers twice more, ending with a layer of sauce; '
#                           'sprinkle mozzarella cheese on top. Cover the dish '
#                           'with aluminum foil.',
#                 'step_6': 'Bake in the preheated oven until the lasagna is '
#                           'bubbling and the cheese has melted, about 30 '
#                           'minutes. Remove foil and bake until cheese has '
#                           'begun to brown, about 10 more minutes. Allow to '
#                           'stand at least 10 minutes before serving.'},
#  'cook_time': '1 hr',
#  'dish_intro': 'This lasagna with ground beef and whole wheat noodles is an '
#                'easy, yet hearty family-pleasing dish.',
#  'dish_name': 'Classic and Simple Meat Lasagna',
#  'ingredients': [{'name': 'whole wheat lasagna noodles',
#                   'quantity': '12',
#                   'unit': ''},
#                  {'name': 'lean ground beef', 'quantity': '1', 'unit': 'pound'},
#                  {'name': 'garlic, chopped', 'quantity': '2', 'unit': 'cloves'},
#                  {'name': 'dried oregano, or to taste',
#                   'quantity': '1',
#                   'unit': 'teaspoon'},
#                  {'name': 'garlic powder', 'quantity': '½', 'unit': 'teaspoon'},
#                  {'name': 'salt and ground black pepper to taste',
#                   'quantity': '',
#                   'unit': ''},
#                  {'name': 'cottage cheese',
#                   'quantity': '1',
#                   'unit': '(16 ounce) package'},
#                  {'name': 'shredded Parmesan cheese',
#                   'quantity': '½',
#                   'unit': 'cup'},
#                  {'name': 'eggs', 'quantity': '2', 'unit': ''},
#                  {'name': 'tomato-basil pasta sauce',
#                   'quantity': '4 ½',
#                   'unit': 'cups'},
#                  {'name': 'shredded mozzarella cheese',
#                   'quantity': '2',
#                   'unit': 'cups'}],
#  'nutrition': {'calories': '501',
#                'carbs': '47g',
#                'fat': '19g',
#                'protein': '36g'},
#  'prep_time': '25 mins',
#  'serving': 1,
#  'total_time': '10 mins',
#  'url': 'https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/'}
# {'Ingredients': [{'descriptor': 'whole',
#                   'full_text': '12  whole wheat lasagna noodles',
#                   'measurement': '',
#                   'name': 'whole wheat lasagna noodles',
#                   'preparation': None,
#                   'quantity': '12'},
#                  {'descriptor': 'lean',
#                   'full_text': '1 pound lean ground beef',
#                   'measurement': 'pound',
#                   'name': 'lean ground beef',
#                   'preparation': None,
#                   'quantity': '1'},
#                  {'descriptor': 'chopped',
#                   'full_text': '2 cloves garlic, chopped',
#                   'measurement': 'cloves',
#                   'name': 'garlic',
#                   'preparation': 'chopped',
#                   'quantity': '2'},
#                  {'descriptor': 'dried to taste',
#                   'full_text': '1 teaspoon dried oregano, or to taste',
#                   'measurement': 'teaspoon',
#                   'name': 'oregano',
#                   'preparation': None,
#                   'quantity': '1'},
#                  {'descriptor': 'garlic',
#                   'full_text': '½ teaspoon garlic powder',
#                   'measurement': 'teaspoon',
#                   'name': 'garlic powder',
#                   'preparation': None,
#                   'quantity': '½'},
#                  {'descriptor': 'black to taste',
#                   'full_text': 'salt and ground black pepper to taste',
#                   'measurement': '',
#                   'name': 'salt',
#                   'preparation': None,
#                   'quantity': ''},
#                  {'descriptor': None,
#                   'full_text': '1 (16 ounce) package cottage cheese',
#                   'measurement': '(16 ounce) package',
#                   'name': 'cottage cheese',
#                   'preparation': None,
#                   'quantity': '1'},
#                  {'descriptor': 'shredded',
#                   'full_text': '½ cup shredded Parmesan cheese',
#                   'measurement': 'cup',
#                   'name': 'Parmesan cheese',
#                   'preparation': None,
#                   'quantity': '½'},
#                  {'descriptor': None,
#                   'full_text': '2  eggs',
#                   'measurement': '',
#                   'name': 'eggs',
#                   'preparation': None,
#                   'quantity': '2'},
#                  {'descriptor': 'tomato-basil',
#                   'full_text': '4 ½ cups tomato-basil pasta sauce',
#                   'measurement': 'cups',
#                   'name': 'tomato-basil pasta sauce',
#                   'preparation': None,
#                   'quantity': '4 ½'},
#                  {'descriptor': 'shredded',
#                   'full_text': '2 cups shredded mozzarella cheese',
#                   'measurement': 'cups',
#                   'name': 'mozzarella cheese',
#                   'preparation': None,
#                   'quantity': '2'}],
#  'Methods': ['sprinkle',
#              'preheat',
#              'combine',
#              'bubble',
#              'repeat',
#              'remove',
#              'begin',
#              'layer',
#              'serve',
#              'brown',
#              'stand',
#              'cover',
#              'bring',
#              'bake',
#              'melt',
#              'stir',
#              'cook',
#              'salt',
#              'Bake',
#              'mix',
#              'add',
#              'end',
#              'Lay'],
#  'Nutrition': {'calories': '501',
#                'carbs': '47g',
#                'fat': '19g',
#                'protein': '36g'},
#  'Steps': [{'context': {'advice': [],
#                         'available_mixtures': [],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Preheat the oven to 350 degrees F (175 degrees C)',
#             'ingredients': [],
#             'methods': ['preheat'],
#             'step_number': 1,
#             'temperature': '350 degrees F',
#             'time': {},
#             'tools': ['the oven']},
#            {'context': {'advice': [],
#                         'available_mixtures': [],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Bring a large pot of lightly salted water to a '
#                            'boil',
#             'ingredients': ['salted water'],
#             'methods': ['bring', 'salt'],
#             'step_number': 2,
#             'temperature': {},
#             'time': {},
#             'tools': ['a large pot', 'a boil']},
#            {'context': {'advice': [],
#                         'available_mixtures': [],
#                         'observations': ['until al dente'],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Add lasagna noodles and cook for 10 minutes or '
#                            'until al dente',
#             'ingredients': ['lasagna noodles'],
#             'methods': ['add', 'cook'],
#             'step_number': 3,
#             'temperature': {},
#             'time': '10 minute',
#             'tools': ['al dente']},
#            {'context': {'advice': [],
#                         'available_mixtures': [],
#                         'observations': ['until beef is crumbly and evenly '
#                                          'browned, about 10 minutes'],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'cook and stir until beef is crumbly and evenly '
#                            'browned, about 10 minutes',
#             'ingredients': ['beef'],
#             'methods': ['cook', 'stir', 'brown'],
#             'step_number': 4,
#             'temperature': {},
#             'time': '10 minute',
#             'tools': []},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4'],
#                         'observations': ['until thoroughly combined'],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Mix cottage cheese, Parmesan cheese, and eggs '
#                            'together in a large bowl until thoroughly combined',
#             'ingredients': ['Parmesan cheese', 'cottage cheese', 'eggs'],
#             'methods': ['mix', 'combine'],
#             'step_number': 5,
#             'temperature': {},
#             'time': {},
#             'tools': ['a large bowl']},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Lay 4 noodles side by side on the bottom of a '
#                            '9x13-inch baking pan',
#             'ingredients': ['4 noodles'],
#             'methods': ['Lay', 'bake'],
#             'step_number': 6,
#             'temperature': {},
#             'time': {},
#             'tools': ['side']},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Repeat layers twice more, ending with a layer of '
#                            'sauce',
#             'ingredients': ['sauce'],
#             'methods': ['repeat', 'layer', 'end'],
#             'step_number': 7,
#             'temperature': {},
#             'time': {},
#             'tools': ['a layer']},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'sprinkle mozzarella cheese on top',
#             'ingredients': ['mozzarella cheese'],
#             'methods': ['sprinkle'],
#             'step_number': 8,
#             'temperature': {},
#             'time': {},
#             'tools': []},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Cover the dish with aluminum foil',
#             'ingredients': [],
#             'methods': ['cover'],
#             'step_number': 9,
#             'temperature': {},
#             'time': {},
#             'tools': ['aluminum foil', 'the dish']},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': ['until the lasagna is bubbling and '
#                                          'the cheese has melted, about 30 '
#                                          'minutes'],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Bake in the preheated oven until the lasagna is '
#                            'bubbling and the cheese has melted, about 30 '
#                            'minutes',
#             'ingredients': ['the lasagna', 'the cheese'],
#             'methods': ['Bake', 'bubble', 'melt'],
#             'step_number': 10,
#             'temperature': {},
#             'time': '30 minute',
#             'tools': ['oven']},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': ['until cheese has begun to brown, '
#                                          'about 10 more minutes'],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Remove foil and bake until cheese has begun to '
#                            'brown, about 10 more minutes',
#             'ingredients': ['cheese'],
#             'methods': ['remove', 'bake', 'begin'],
#             'step_number': 11,
#             'temperature': {},
#             'time': {},
#             'tools': ['foil']},
#            {'context': {'advice': [],
#                         'available_mixtures': ['mixture_step_4',
#                                                'mixture_step_5'],
#                         'observations': [],
#                         'oven_preheated': False,
#                         'oven_temperature': None,
#                         'references': [],
#                         'warnings': []},
#             'description': 'Allow to stand at least 10 minutes before serving',
#             'ingredients': [],
#             'methods': ['allow', 'stand', 'serve'],
#             'step_number': 12,
#             'temperature': {},
#             'time': '10 minute',
#             'tools': []}],
#  'Tools': ['aluminum foil',
#            'a large bowl',
#            'a large pot',
#            'the oven',
#            'the dish',
#            'al dente',
#            'a layer',
#            'a boil',
#            'side'],
#  'cook_time': '1 hr',
#  'dish_intro': 'This lasagna with ground beef and whole wheat noodles is an '
#                'easy, yet hearty family-pleasing dish.',
#  'dish_name': 'Classic and Simple Meat Lasagna',
#  'prep_time': '25 mins',
#  'serving': 1,
#  'total_time': '10 mins',
#  'url': 'https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/'}


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
    def __init__(self):
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
                return {"nav": self.model["Steps"][self.current_step + 1]}
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
        history_item = {
            "question": q_data["question"],
            "type": q_data["type"],
            "relevant": q_data["relevant"],
            "step": self.current_step,
        }
        self.history.append(history_item)

    # QA main loop here
    def run(self):
        if self.model is None:
            while True:
                print("Please input a URL for recipe parsing first, the URL must from AllRecipes.com")
                URL = input("Enter recipe URL: ")
                pattern = r'^https?://(www\.)?allrecipes\.com/.*$'
                if re.match(pattern, URL):
                    from parser import Parser
                    try:
                        self.model = Parser(URL).parse()
                        print("Recipe data successfully parsed and loaded.")
                        self.max_step = len(self.model["Steps"])
                        break
                    except Exception as e:
                        print(f"Error parsing recipe: {e}")
                else:
                    print("Invalid URL. Please try again.")
        while True:
            """
            # maybe speech to text for input?
            input = self.speech_to_text()
            question_parsed_data = self.question_parser(input)
            """
            # get_question()
            question_parsed_data = self.question_parser(input("Please enter your question, if you want to exit, input \"exit\": "))

            # handle data and choose appropriate response by calling agent()
            status = self.agent(question_parsed_data)

            if status == -1:
                break

            # update memory i.e. state tracking
            self._add_to_history(question_parsed_data)

        print("QA session ended.")


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