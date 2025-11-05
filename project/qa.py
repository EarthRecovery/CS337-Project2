
class QA:
    def __init__(self, model):
        self.model = model
        self.history = {}
        self.question_types = []
        # Recipe retrieval and display (see example above, including "Show me the ingredients list")
        # Navigation utterances ("Go back one step", "Go to the next step", "Repeat please", "Take me to the 1st step", "Take me to the n-th step")
        # Asking about the parameters of the current step ("How much of <ingredient> do I need?", "What temperature?", "How long do I <specific technique>?", "When is it done?", "What can I use instead of <ingredient or tool>")
        # Simple "what is" questions ("What is a <tool being mentioned>?")
        # Specific "how to" questions ("How do I <specific technique>?").
        # Vague "how to" questions ("How do I do that?" – use conversation history to infer what “that” refers to)

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