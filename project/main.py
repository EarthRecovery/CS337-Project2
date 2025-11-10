import parser
import qa

def pipeline():
    data = parser.Parser("https://www.allrecipes.com/mediterranean-crispy-rice-chicken-bowl-recipe-8778475").parse()
    # qa_model = qa.QA(data)
    # qa_model.run()
    # qa_model.run_one_turn("What is the first step?")

if __name__ == "__main__":
    pipeline()


# example of parsed_data output from parser.Parser.parse()
# {
#   "Ingredients": [
#     {
#       "name": "boneless skinless chicken thighs",
#       "quantity": "1 1/4",
#       "measurement": "pounds",
#       "descriptor": null,
#       "preparation": null
#     },
#     {
#       "name": "olive oil",
#       "quantity": "4",
#       "measurement": "tablespoons",
#       "descriptor": null,
#       "preparation": null
#     },
#     {
#       "name": "Greek seasoning",
#       "quantity": "2",
#       "measurement": "teaspoons",
#       "descriptor": null,
#       "preparation": null
#     },
#     {
#       "name": "paprika",
#       "quantity": "1/2",
#       "measurement": "teaspoon",
#       "descriptor": null,
#       "preparation": null
#     },
#     {
#       "name": "garlic",
#       "quantity": "2",
#       "measurement": "cloves",
#       "descriptor": null,
#       "preparation": null
#     },
#     {
#       "name": "kosher salt",
#       "quantity": "1/4",
#       "measurement": "teaspoon",
#       "descriptor": null,
#       "preparation": null
#     }
#   ],
#   "Tools": [
#     "oven",
#     "baking sheet",
#     "parchment paper",
#     "bowl",
#     "whisk",
#     "skillet",
#     "spatula",
#     "knife"
#   ],
#   "Methods_primary": [
#     "bake",
#     "cook",
#     "whisk"
#   ],
#   "Methods_other": [
#     "combine",
#     "stir",
#     "heat",
#     "spread",
#     "deglaze",
#     "divide",
#     "drizzle",
#     "top"
#   ],
#   "Steps": [
#   {
#     "step_number": 1,
#     "description": "Preheat the oven to 400°F (200°C). Lightly grease a baking sheet or line with parchment.",
#     "ingredients": [],
#     "tools": ["oven", "baking sheet", "parchment paper"],
#     "methods": ["preheat", "grease", "line"],
#     "time": {},
#     "temperature": {"oven": "400°F"},
#     "action": "preheat",
#     "object": "oven",
#     "context": null,
#     "info": {
#       "Actionable": [
#         "Preheat the oven to 400°F (200°C).",
#         "Lightly grease a baking sheet or line with parchment."
#       ],
#       "Warning": [],
#       "Advice": [],
#       "Observation": []
#     }
#   },
#   {
#     "step_number": 2,
#     "description": "Combine chicken, 1 tablespoon oil, 1 teaspoon Greek seasoning, paprika, garlic, and salt in a bowl. Stir until well coated; set aside.",
#     "ingredients": ["chicken thighs", "olive oil", "Greek seasoning", "paprika", "garlic", "salt"],
#     "tools": ["bowl"],
#     "methods": ["combine", "stir"],
#     "time": {},
#     "temperature": {},
#     "action": "combine",
#     "object": "chicken mixture",
#     "context": null,
#     "info": {
#       "Actionable": [
#         "Combine chicken, oil, seasoning, paprika, garlic, and salt in a bowl.",
#         "Stir until well coated."
#       ],
#       "Warning": [],
#       "Advice": [],
#       "Observation": []
#     }
#   },
#   {
#     "step_number": 3,
#     "description": "For dressing, whisk olive oil, red wine vinegar, pepper brine, honey, Dijon mustard, salt, and black pepper together in a small bowl until well combined; set aside.",
#     "ingredients": ["olive oil", "red wine vinegar", "pepper brine", "honey", "Dijon mustard", "salt", "black pepper"],
#     "tools": ["whisk", "bowl"],
#     "methods": ["whisk"],
#     "time": {},
#     "temperature": {},
#     "action": "whisk",
#     "object": "dressing mixture",
#     "context": null,
#     "info": {
#       "Actionable": [
#         "Whisk olive oil, vinegar, brine, honey, mustard, salt, and pepper together until combined."
#       ],
#       "Warning": [],
#       "Advice": [],
#       "Observation": []
#     }
#   },
#   {
#     "step_number": 4,
#     "description": "Combine cooked rice and soy sauce with remaining 3 tablespoons olive oil and 1 teaspoon Greek seasoning in a bowl. Spread rice onto the prepared baking sheet.",
#     "ingredients": ["cooked rice", "soy sauce", "olive oil", "Greek seasoning"],
#     "tools": ["bowl", "baking sheet"],
#     "methods": ["combine", "spread"],
#     "time": {},
#     "temperature": {},
#     "action": "combine",
#     "object": "rice mixture",
#     "context": {"oven_preheated": "400°F"},
#     "info": {
#       "Actionable": [
#         "Combine cooked rice, soy sauce, olive oil, and seasoning in a bowl.",
#         "Spread rice onto prepared baking sheet."
#       ],
#       "Warning": [],
#       "Advice": [],
#       "Observation": []
#     }
#   },
#   {
#     "step_number": 5,
#     "description": "Bake rice in the preheated oven until crispy and lightly browned, about 40 minutes.",
#     "ingredients": ["rice"],
#     "tools": ["oven", "baking sheet"],
#     "methods": ["bake"],
#     "time": {"duration": "40 minutes"},
#     "temperature": {"oven": "400°F"},
#     "action": "bake",
#     "object": "rice",
#     "context": {"oven_preheated": "400°F"},
#     "info": {
#       "Actionable": [
#         "Bake rice in the preheated oven until crispy and lightly browned."
#       ],
#       "Warning": [],
#       "Advice": [
#         "If rice starts browning too quickly, cover lightly with foil."
#       ],
#       "Observation": [
#         "Rice becomes crisp and golden when properly baked."
#       ]
#     }
#   },
#   {
#     "step_number": 6,
#     "description": "Heat oil in a skillet over medium-high heat. Add chicken and cook, undisturbed, until browned on one side and releases easily, 3 to 4 minutes. Continue to cook and stir until no longer pink and browned on all sides, about 4 minutes more. Add water and deglaze the skillet; remove from heat.",
#     "ingredients": ["oil", "chicken", "water"],
#     "tools": ["skillet", "spatula"],
#     "methods": ["heat", "cook", "stir", "deglaze"],
#     "time": {"duration": "7 to 8 minutes"},
#     "temperature": {"stovetop": "medium-high"},
#     "action": "cook",
#     "object": "chicken",
#     "context": null,
#     "info": {
#       "Actionable": [
#         "Heat oil in skillet over medium-high heat.",
#         "Cook chicken until browned on both sides.",
#         "Add water and deglaze skillet."
#       ],
#       "Warning": [
#         "Be careful of oil splatter when adding chicken to hot oil."
#       ],
#       "Advice": [
#         "Use tongs instead of a fork to avoid piercing the chicken."
#       ],
#       "Observation": [
#         "Chicken releases easily from the pan when properly seared."
#       ]
#     }
#   },
#   {
#     "step_number": 7,
#     "description": "To serve, divide chicken, tomatoes, cucumber, red onion, banana peppers, parsley, and olives among 4 bowls. Top evenly with crispy rice and feta cheese and drizzle with dressing.",
#     "ingredients": ["chicken", "tomatoes", "cucumber", "red onion", "banana peppers", "parsley", "olives", "crispy rice", "feta cheese", "dressing"],
#     "tools": ["bowl"],
#     "methods": ["divide", "top", "drizzle"],
#     "time": {},
#     "temperature": {},
#     "action": "assemble",
#     "object": "serving bowls",
#     "context": null,
#     "info": {
#       "Actionable": [
#         "Divide chicken and vegetables among bowls.",
#         "Top with crispy rice and feta cheese.",
#         "Drizzle dressing evenly before serving."
#       ],
#       "Warning": [],
#       "Advice": [
#         "Serve immediately to maintain crisp rice texture."
#       ],
#       "Observation": [
#         "The dish has a fresh, crunchy texture when served warm."
#       ]
#     }
#   }
# ]

# }
