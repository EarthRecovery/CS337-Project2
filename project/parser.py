from spacy.tokenizer import Tokenizer 
from bs4 import BeautifulSoup
import requests
import re
import spacy

class Parser:
    def __init__(self, data_url):
        self.data_url = data_url
        self.webpage = {
            "url": data_url,
            "dish_name": "",
            "dish_intro": "",
            "prep_time": "",
            "cook_time": "",
            "total_time": "",
            "serving": 0,
            "ingredients": [],
            "Directions":{},
            "nutrition": {}
        }
        # example output: 
        # {'url': 'https://www.allrecipes.com/mediterranean-crispy-rice-chicken-bowl-recipe-8778475', 'dish_name': 'Mediterranean Crispy Rice Chicken Bowl', 'dish_intro': "This Mediterranean crispy rice chicken bowl features Greek flavors from seasoned chicken, tomatoes, Kalamata olives, feta cheese, banana peppers, and cucumber. It's dressed with a red wine vinaigrette, then topped with crunchy rice, crisped in the oven.", 'prep_time': '25 mins', 'cook_time': '50 mins', 'total_time': '1 hr 15 mins', 'serving': 4, 'ingredients': [{'quantity': '1 1/4', 'unit': 'pounds', 'name': 'boneless skinless chicken thighs'}, {'quantity': '4', 'unit': 'tablespoons', 'name': 'olive oi'}, {'quantity': '2', 'unit': 'teaspoons', 'name': 'seasoning,'}, {'quantity': '1/2', 'unit': 'teaspoon', 'name': 'paprika'}, {'quantity': '2', 'unit': 'cloves', 'name': 'garlic,'}, {'quantity': '1/4', 'unit': 'teaspoon', 'name': 'kosher salt'}], 'Directions': {'step_1': 'Preheat the oven to 400 degrees F (200 degrees C). Lightly grease a baking sheet or line with parchment.', 'step_2': 'Combine chicken, 1 tablespoon oil, 1 teaspoon Greek seasoning, paprika, garlic, and salt in a bowl. Stir until well coated; set aside.', 'step_3': 'For dressing, whisk olive oil, red wine vinegar, pepper brine, honey, Dijon mustard, salt, and black pepper together in a small bowl until well combined; set aside.', 'step_4': 'Combine cooked rice and soy sauce with remaining 3 tablespoons olive oil and 1 teaspoon Greek seasoning in a bowl. Spread rice onto the prepared baking sheet.', 'step_5': 'Bake rice in the preheated oven until rice is crispy and lightly browned, about 40 minutes.', 'step_6': 'Meanwhile, heat a small amount of oil in a skillet over medium-high heat. Add chicken and cook, undisturbed, until chicken is browned on one side and releases easily from pan, 3 to 4 minutes. Continue to cook and stir until chicken is no longer pink at the center and browned on all sides, about 4 minutes more. Add water to the skillet and continue to stir until bottom of skillet is deglazed. Remove from heat.', 'step_7': 'To serve, divide chicken, tomatoes, cucumber, red onion, banana peppers, parsley, and olives among 4 bowls. Top evenly with crispy rice and feta cheese and drizzle with dressing.'}, 'nutrition': {'calories': '759', 'fat': '46g', 'carbs': '46g', 'protein': '42g'}}
        self.data = None
        self.parsed_data = {
            "url": data_url,
            "dish_name": "",
            "dish_intro": "",
            "prep_time": "",
            "cook_time": "",
            "total_time": "",
            "serving": 0,
            "Ingredients": [],
            "Tools": [],
            "Methods_primary": [],
            "Methods_other": [],
            "Steps": [],
            "Nutrition": {}
        }
        self.nlp = spacy.load("en_core_web_sm")
        self.nlp.tokenizer = self.custom_tokenizer(self.nlp)

    @staticmethod
    def fix_imperative_verbs(doc):
        """
        Fix spaCy errors when parsing imperative verbs at the beginning of recipe steps,
        without using a verb lexicon, and supporting multi-sentence docs.
        """

        for sent in doc.sents:
            if len(sent) == 0:
                continue
            
            token = sent[0]   # first token of the sentence
            
            # Skip if spaCy already recognized as a verb
            if token.pos_ in ["VERB", "AUX"]:
                continue

            # Heuristic 1: ROOT but not verb → imperative verb
            if token.dep_ == "ROOT":
                token.pos_ = "VERB"
                token.tag_ = "VB"
                continue

            # Heuristic 2: next token is ADP/ADV/DET → typical structure of imperative sentence
            if len(sent) > 1:
                next_pos = sent[1].pos_
                if next_pos in ["ADP", "ADV", "DET"]:
                    token.pos_ = "VERB"
                    token.tag_ = "VB"
                    continue
            
            # Heuristic 3: token is capitalized + looks like a verb form (lemma == lowercase word)
            # Example: "Top", lemma="top"
            if token.text[0].isupper() and token.lemma_.lower() == token.text.lower():
                token.pos_ = "VERB"
                token.tag_ = "VB"
                continue

            # Heuristic 4: token is alphabetic and not a noun-like POS
            # (avoid misclassifying proper nouns)
            if token.pos_ in ["ADV", "NOUN", "PROPN", "ADJ"] and token.text.isalpha():
                token.pos_ = "VERB"
                token.tag_ = "VB"
                continue

        return doc

    def custom_tokenizer(self, nlp):
        pattern = re.compile(r"^[A-Za-z0-9]+(?:[-–—][A-Za-z0-9]+)+$")
        tokenizer = nlp.tokenizer
        tokenizer.token_match = pattern.match
        return tokenizer

    def load_data(self):
        # Implement data loading logic here
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        resp = requests.get(self.data_url, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Failed to load page: {resp.status_code}")
        
        soup = BeautifulSoup(resp.text, "html.parser")
        # dish_name
        name_tag = soup.find("h1", class_="article-heading")
        if name_tag:
            self.webpage["dish_name"] = name_tag.get_text().strip()

        # dish_intro
        intro_tag = soup.find("p", class_="article-subheading")
        if intro_tag:
            self.webpage["dish_intro"] = intro_tag.get_text().strip()

        # prep_time, cook_time, total_time
        detail_content_div = soup.find("div", class_="mm-recipes-details__content")
        if detail_content_div:
            subdivs = detail_content_div.find_all("div", recursive=False)
            prep_time_div = subdivs[0].find("div", class_="mm-recipes-details__value")
            self.webpage["prep_time"] = prep_time_div.get_text().strip() if prep_time_div else ""
            cook_time_div = subdivs[1].find("div", class_="mm-recipes-details__value")
            self.webpage["cook_time"] = cook_time_div.get_text().strip() if cook_time_div else ""
            total_time_div = subdivs[2].find("div", class_="mm-recipes-details__value")
            self.webpage["total_time"] = total_time_div.get_text().strip() if total_time_div else ""
            # serving
            serving_div = subdivs[3].find("div", class_="mm-recipes-details__value")
            if serving_div:
                serving_text = serving_div.get_text().strip()
                try:
                    self.webpage["serving"] = int(serving_text.split()[0])
                except:
                    self.webpage["serving"] = 0

        # ingredients
        ingredients_ul = soup.find("ul", class_="mm-recipes-structured-ingredients__list")
        ingredient_li = ingredients_ul.find_all("li", class_="mm-recipes-structured-ingredients__list-item") if ingredients_ul else []
        for ingredient in ingredient_li:
            full_text = ingredient.find_all("p")[0]
            quantity = full_text.find("span", attrs={"data-ingredient-quantity": True}).get_text().strip() if full_text.find("span", attrs={"data-ingredient-quantity": True}) else ""
            unit = full_text.find("span", attrs={"data-ingredient-unit": True}).get_text().strip() if full_text.find("span", attrs={"data-ingredient-unit": True}) else ""
            name = full_text.find("span", attrs={"data-ingredient-name": True}).get_text().strip() if full_text.find("span", attrs={"data-ingredient-name": True}) else ""
            other= None
            for content in full_text.contents:
                if isinstance(content, str):
                    other = content.strip()
            if other:
                name = name + " " + other
                name = name.strip()
            ingredient_dict = {
                "quantity": quantity,
                "unit": unit,
                "name": name
            }
            self.webpage["ingredients"].append(ingredient_dict)

        # Directions
        direction_ol = soup.find("ol", class_=["comp", "mntl-sc-block", "mntl-sc-block-startgroup", "mntl-sc-block-group--OL"])
        direction_li_list = direction_ol.find_all("li", class_="mntl-sc-block") if direction_ol else []
        for idx, direction_li in enumerate(direction_li_list):
            step_text = direction_li.find("p", class_=["comp", "mntl-sc-block", "mntl-sc-block-startgroup"]).get_text().strip() if direction_li.find("p", class_=["comp", "mntl-sc-block", "mntl-sc-block-startgroup"]) else ""
            self.webpage["Directions"][f"step_{idx+1}"] = step_text

        # nutrition
        nutrition_tbody = soup.find("tbody", class_="mm-recipes-nutrition-facts-summary__table-body")
        nutrition_tr_list = nutrition_tbody.find_all("tr") if nutrition_tbody else []
        for nutrition_tr in nutrition_tr_list:
            nutrient_name_td = nutrition_tr.find_all("td")[1]
            nutrient_value_td = nutrition_tr.find_all("td")[0]
            if nutrient_name_td and nutrient_value_td:
                nutrient_name = nutrient_name_td.get_text().strip().lower().replace(" ", "_")
                nutrient_value = nutrient_value_td.get_text().strip()
                self.webpage["nutrition"][nutrient_name] = nutrient_value

    def _parse_ingredients(self):
        for ing in self.webpage.get("ingredients", []):
            quantity = ing.get("quantity") or ""
            measurement = ing.get("unit") or ""
            name_raw = ing.get("name") or ""
            full_text = f"{quantity} {measurement} {name_raw}".strip()

            descriptor = None
            preparation = None

            doc_main = self.nlp(name_raw)

            descriptors_list = []
            # find adj
            for token in doc_main:
                if token.pos_ in ["ADJ","VERB"] and token.dep_ in ["amod","acomp"]:
                    descriptors_list.append(token.text)
            for i, token in enumerate(doc_main[:-1]): 
                if token.text.lower() == "to" and token.pos_ == "PART":
                    next_token = doc_main[i + 1]
                    if next_token.pos_ == "VERB" and "VerbForm=Inf" in next_token.morph:
                        descriptors_list.append(f"to {next_token.text}")
            if not descriptors_list:
                for token in doc_main:
                    if token.pos_ == "NUM" and token.dep_ in ["nummod", "compound"]:
                        descriptors_list.append(token.text)
            if not descriptors_list:
                for token in doc_main:
                    if token.pos_ == "VERB" and token.dep_ == "ROOT":
                        descriptors_list.append(token.text)
            if descriptors_list:
                descriptor = " ".join(descriptors_list)

            preparation_list = []
            after_comma = False
            if len(name_raw.split(",")) > 1:
                for token in doc_main:
                    if "PunctType=Comm" in token.morph:
                        after_comma = True
                        continue
                    if not after_comma:
                        continue
                    if after_comma:
                        if token.pos_ == "VERB" and ("VerbForm=Part" in token.morph or "VerbForm=Fin" in token.morph):
                            preparation_list.append(token.text)
                            for child in token.subtree:
                                if child.i > token.i:
                                    preparation_list.append(child.text)
                            break

            if preparation_list:
                preparation = " ".join(preparation_list)

            name_list = []
            for token in doc_main:
                if token.pos_ in ["NOUN", "PROPN", "ADJ"] and token.dep_ in ["compound","amod"]:
                    name_list.append(token.text)
                if token.pos_ in ["NOUN", "PROPN"] and token.dep_ in ["nsubj","ROOT", "dobj"]:
                    name_list.append(token.text)
                    break
            name = " ".join(name_list)


            if preparation:
                preparation = preparation.strip().strip(",.")
            if descriptor:
                descriptor = descriptor.strip().strip(",.")
            name = name.strip().strip(",.")

            self.parsed_data["Ingredients"].append({
                "full_text": full_text,
                "name": name,
                "quantity": quantity,
                "measurement": measurement,
                "descriptor": descriptor,
                "preparation": preparation
            })

    def keep_longest_unique(self,strings):
        strings = list(set(s.strip() for s in strings if s and s.strip()))
        strings.sort(key=len, reverse=True)

        result = []
        for s in strings:
            if not any(s in longer for longer in result):
                result.append(s)

        return result

    def _parse_steps(self):
        for step_key, step_desc in self.webpage.get("Directions", {}).items():
            step_dict = self._parse_one_step(step_desc, step_key)
            self.parsed_data["Steps"].append(step_dict)

        # flatten lists
        methods_raw = [method for step in self.parsed_data["Steps"] for method in step["methods"]]
        tools_raw = [tool for step in self.parsed_data["Steps"] for tool in step["tools"]]

        self.parsed_data["Methods_primary"] = self.keep_longest_unique(methods_raw)
        self.parsed_data["Tools"] = self.keep_longest_unique(tools_raw)

    @staticmethod
    def extract_noun_phrases(doc):
        noun_phrases = []

        for token in doc:
            if token.pos_ in ["NOUN", "PROPN"]:
                modifiers = []

                # (amod / compound / nummod / det)
                for child in token.children:
                    if child.dep_ in ["amod", "compound", "nummod", "det"]:
                        modifiers.append(child)

                modifiers = sorted(modifiers, key=lambda x: x.i)

                phrase_tokens = modifiers + [token]
                phrase = " ".join(w.text for w in phrase_tokens)

                noun_phrases.append(phrase)

        return noun_phrases

    def _parse_one_step(self, step_desc, step_key):
        step_dict = {
            "step_number": int(step_key.split("_")[1]),
            "description": step_desc,
            "ingredients": [],
            "tools": [],
            "methods": [],
            "time": {},
            "temperature": {},
            "context": {
                "references": [],
                "warnings": []
            }
        }

        # --- spaCy doc ---
        doc_step = self.nlp(step_desc)
        doc_step = self.fix_imperative_verbs(doc_step)

        def unique_keep_order(lst):
            seen = set()
            result = []
            for x in lst:
                if x not in seen:
                    seen.add(x)
                    result.append(x)
            return result

        def filter_longest_phrases(phrases):
            phrases_sorted = sorted(phrases, key=lambda x: len(x), reverse=True)
            result = []
            for p in phrases_sorted:
                if not any(p != q and p in q for q in result):
                    result.append(p)
            return result

        TOOL_NOISE = {
            "minutes", "minute", "hours", "hour", "secs", "seconds", "sec", "degrees", "degree"
        }

        for token in doc_step:
            if token.pos_ == "VERB":
                step_dict["methods"].append(token.lemma_)

        step_dict["methods"] = unique_keep_order(step_dict["methods"])


        noun_phrase = self.extract_noun_phrases(doc_step)
        noun_phrase = filter_longest_phrases(noun_phrase)

        ingredients_list = sorted(
            [ing["name"].lower() for ing in self.parsed_data["Ingredients"]],
            key=len,
            reverse=True
        )

        matched = []

        for np in noun_phrase:
            np_low = np.lower()

            for ing in ingredients_list:
                ing_low = ing.lower()

                if ing_low in np_low:
                    matched.append(np)
                    step_dict["ingredients"].append(np)
                    break

                ing_tokens = ing_low.split()
                if len(ing_tokens) >= 2:
                    head = ing_tokens[-1] 
                    if head in np_low:
                        matched.append(np)
                        step_dict["ingredients"].append(np)
                        break

        step_dict["ingredients"] = unique_keep_order(step_dict["ingredients"])

        tools_raw = [np for np in noun_phrase if np not in matched]

        tools_clean = []
        for t in tools_raw:
            t_low = t.lower()
            if any(noise in t_low for noise in TOOL_NOISE):
                continue
            if any(ch.isdigit() for ch in t_low):
                continue
            tools_clean.append(t)

        step_dict["tools"] = unique_keep_order(tools_clean)

        for token in doc_step:
            if token.like_num:
                next_token = None
                if token.i + 1 < len(doc_step):
                    next_token = doc_step[token.i + 1]

                if next_token and next_token.pos_ in ["NOUN", "PROPN"]:

                    if next_token.text.lower() in [
                        "minutes", "minute", "hours", "hour",
                        "secs", "seconds", "sec", "mins"
                    ]:
                        step_dict["time"] = f"{token.text} {next_token.text}"
                        continue

                    # temperature
                    if next_token.text.lower() in [
                        "°f", "°c", "degrees", "degree", "f", "c"
                    ]:
                        step_dict["temperature"] = f"{token.text} {next_token.text}"
                        continue

        return step_dict

    def _add_other_info(self):
        # Implement logic to add other relevant information to parsed_data
        self.parsed_data["dish_name"] = self.webpage.get("dish_name", "")
        self.parsed_data["dish_intro"] = self.webpage.get("dish_intro", "")
        self.parsed_data["prep_time"] = self.webpage.get("prep_time", "")
        self.parsed_data["cook_time"] = self.webpage.get("cook_time", "")
        self.parsed_data["total_time"] = self.webpage.get("total_time", "")
        self.parsed_data["serving"] = self.webpage.get("serving", 0)
        self.parsed_data["Nutrition"] = self.webpage.get("nutrition", {})

    def parse(self):
        self.load_data()
        # Implement parsing logic here
        self._parse_ingredients()
        self._parse_steps()
        self._add_other_info()
        pass

# TA suggested sentence splitting within steps

    @staticmethod
    def ingredients_test():
        parser = Parser("https://www.allrecipes.com/tennessee-onions-recipe-8609254")
        parser.load_data()
        parser._parse_ingredients()
        for ing in parser.parsed_data["Ingredients"]:
            print(ing)

    @staticmethod
    def spacy_test():
        parser = Parser("https://www.allrecipes.com/tennessee-onions-recipe-8609254")
        test_sentences = [
            "1 teaspoon garlic powder",
        ]
        for sentence in test_sentences:
            doc = parser.nlp(sentence)
            print(f"Sentence: {sentence}")
            for token in doc:
                print(f"  {token.text:15} {token.pos_:10} {token.dep_:10} {token.morph}")
            print()

    @staticmethod
    def steps_test():
        parser = Parser("https://www.allrecipes.com/mediterranean-crispy-rice-chicken-bowl-recipe-8778475")
        parser.load_data()
        parser._parse_ingredients()
        step = "Combine chicken, 1 tablespoon oil, 1 teaspoon Greek seasoning, paprika, garlic, and salt in a bowl. Stir until well coated; set aside. "
        doc_step = parser.nlp(step)
        doc_step = parser.fix_imperative_verbs(doc_step)
        parser._parse_one_step(step, "step_1")

if __name__ == "__main__":
    parser = Parser("https://www.allrecipes.com/recipe/275427/air-fryer-roasted-brussels-sprouts-with-maple-mustard-mayo/")
    parser.parse()
    print(parser.webpage)
    print(parser.parsed_data)
