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
    TIME            = 10 # ex: "how long do I <specific technique>?"
    DONENESS        = 11 # ex: "when is it done?"
    SUBSTITUION     = 12 # ex: "can I use <ingredient or tool> instead of <ingredient or tool>"

    # simple "what is", specific "how to", and vague "how to" questions
    WHAT_IS         = 13 # ex: "what is a <tool being mentioned>?"
    HOW_TO_SPECIFIC = 14 # ex: "how do I <specific technique>?"
    HOW_TO_VAGUE    = 15 # ex: "how do I do that?" – (use conversation history to infer what “that” refers to)

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

    def question_parser(self, question):
        # parse the input question, identify its type and relevant context
        pass

    def run(self):
        # Implement QA main loop here
        while True:
            # maybe speech to text
            # get_question()
            question_parsed_data  = self.question_parser(input("Please enter your question: "))

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