import parser
import qa

def pipeline():
    data = parser.Parser("https://www.allrecipes.com/mediterranean-crispy-rice-chicken-bowl-recipe-8778475").parse()
    # qa_model = qa.QA(data)
    # qa_model.run()
    # qa_model.run_one_turn("What is the first step?")

if __name__ == "__main__":
    pipeline()