import html
from spacy.tokenizer import Tokenizer
from bs4 import BeautifulSoup
import requests
import re
import spacy


class Parser:
    # ----- Patterns for Different Information Types -----
    WARNING_PATTERNS = [
        re.compile(r"\bbe careful\b", re.IGNORECASE),
        re.compile(r"\bdo not\b", re.IGNORECASE),
        re.compile(r"\bdon't\b", re.IGNORECASE),
        re.compile(r"\bavoid\b", re.IGNORECASE),
        re.compile(r"\bmake sure\b", re.IGNORECASE),
        re.compile(r"\bensure\b", re.IGNORECASE),
        re.compile(r"\bbe sure\b", re.IGNORECASE),
        re.compile(r"\bbe cautious\b", re.IGNORECASE),
    ]

    ADVICE_PATTERNS = [
        re.compile(r"\byou can\b", re.IGNORECASE),
        re.compile(r"\boptional\b", re.IGNORECASE),
        re.compile(r"\bif you prefer\b", re.IGNORECASE),
        re.compile(r"\bit'?s ok\b", re.IGNORECASE),
        re.compile(r"\bit'?s okay\b", re.IGNORECASE),
        re.compile(r"\bit is ok\b", re.IGNORECASE),
        re.compile(r"\bit is okay\b", re.IGNORECASE),
        re.compile(r"\byou may\b", re.IGNORECASE),
        re.compile(r"\bfeel free to\b", re.IGNORECASE),
    ]

    OBS_PATTERNS = [
        # Non-greedy "until" — stops before ., ;, and, but
        re.compile(r"\buntil\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),

        # "when" conditions (non-greedy)
        re.compile(r"\bwhen\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),

        # "will become", "will look", "will thicken" — non-greedy
        re.compile(r"\bwill become\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),
        re.compile(r"\bwill look\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),
        re.compile(r"\bwill thicken\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),

        # Common cooking state descriptors
        re.compile(r"\bshould be\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),
        re.compile(r"\bturn(s)? (?:golden|brown|opaque)\b.*?(?=\.|;|,| and | but |$)", re.IGNORECASE),
    ]


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
            "Directions": {},
            "nutrition": {}
        }
        # example output:
        # {'url': 'https://www.allrecipes.com/mediterranean-crispy-rice-chicken-bowl-recipe-8778475', ...}

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
            "Methods": [],
            "Steps": [],
            "Nutrition": {}
        }

        # ---- Global context state: used for context propagation across steps ----
        self.context_state = {
            "oven_preheated": False,
            "oven_temp": None,        # e.g. "350 degrees F"
            "prepared_items": set(),  # e.g. {"mixture_step_2", "frosting_step_4"}
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

    def load_data_from_allrecipes(self):
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
        ingredients_ul = soup.find_all("ul", class_="mm-recipes-structured-ingredients__list")
        ingredient_li = []
        for ul in ingredients_ul:
            ingredient_li.extend(ul.find_all("li", class_="mm-recipes-structured-ingredients__list-item"))
        for ingredient in ingredient_li:
            full_text = ingredient.find_all("p")[0]
            quantity = full_text.find("span", attrs={"data-ingredient-quantity": True}).get_text().strip() if full_text.find("span", attrs={"data-ingredient-quantity": True}) else ""
            unit = full_text.find("span", attrs={"data-ingredient-unit": True}).get_text().strip() if full_text.find("span", attrs={"data-ingredient-unit": True}) else ""
            name = full_text.find("span", attrs={"data-ingredient-name": True}).get_text().strip() if full_text.find("span", attrs={"data-ingredient-name": True}) else ""
            other = None
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
            direction_ol = soup.select_one("ol.mntl-sc-block-group--OL")
            direction_li_list = direction_ol.select("li.mntl-sc-block") if direction_ol else []

            for idx, li in enumerate(direction_li_list, 1):
                p = li.select_one("p.mntl-sc-block-html")
                step_text = p.get_text(strip=True) if p else ""
                self.webpage["Directions"][f"step_{idx}"] = step_text

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

    # def load_data_from_bonappetit(self):
    #     # Implement data loading logic here
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    #     }
    #     resp = requests.get(self.data_url, headers=headers)
    #     if resp.status_code != 200:
    #         raise Exception(f"Failed to load page: {resp.status_code}")

    #     soup = BeautifulSoup(resp.text, "html.parser")
    #     # dish_name
    #     name_tag = soup.find("h1", attrs={"data-testid": "ContentHeaderHed"})
    #     if name_tag:
    #         self.webpage["dish_name"] = name_tag.get_text().strip()

    #     # dish_intro
    #     intro_tag = soup.find("div", attrs={"data-testid": "BodyWrapper"})
    #     if intro_tag:
    #         intro_p_list = intro_tag.find_all("p")
    #         intro_texts = [p.get_text().strip() for p in intro_p_list]
    #         self.webpage["dish_intro"] = " ".join(intro_texts)

    #     # prep_time, cook_time, total_time
    #     detail_content_div = soup.find("div", attrs={"data-testid": "InfoSliceList"})
    #     if detail_content_div:
    #         detail_p_list = detail_content_div.find_all("p")
    #         total_time_p = detail_p_list[1]
    #         yield_p = detail_p_list[3]
    #         self.webpage["total_time"] = total_time_p.get_text().strip() if total_time_p else ""
    #         yield_data = yield_p.get_text().strip() if yield_p else ""
    #         if yield_data:
    #             try:
    #                 self.webpage["serving"] = int(yield_data.split()[0])
    #             except:
    #                 self.webpage["serving"] = 0
    #     else:
    #         print("No detail content div found")

    #     # ingredients
    #     ingredients_div = soup.find("div", class_="InfoSliceItem-sAZIH jermig")
    #     div_lists = ingredients_div.find_all("div", recursive=False) if ingredients_div else []
    #     ingridient_body_div = div_lists[0] if div_lists else None
    #     p_list = ingridient_body_div.find_all("p") if ingridient_body_div else []
    #     div_lists_2 = ingridient_body_div.find_all("div", recursive=False) if ingridient_body_div else []
    #     for p,div in zip(p_list, div_lists_2):
    #         quantity = p.get_text().strip() if p else ""
    #         name = div.get_text().strip() if div else ""
    #         pattern = pattern = r"<a\b[^>]*>"
    #         name = re.sub(pattern, "", name)
    #         ingredient_dict = {
    #             "quantity": quantity,
    #             "unit": "",
    #             "name": name
    #         }
    #         self.webpage["ingredients"].append(ingredient_dict)

    #     # Directions
    #     wrapper = soup.find("div", attrs={"data-testid": "InstructionsWrapper"})
    #     direction_li = wrapper.find_all("li", recursive=False)[0] if wrapper else None
    #     h4_list = direction_li.find_all("h4") if direction_li else []
    #     p_list = direction_li.find_all("p") if direction_li else []
    #     def clean_keep_strong(html):
    #         soup = BeautifulSoup(html, "html.parser")
    #         for tag in soup.find_all():
    #             if tag.name != "strong":
    #                 tag.unwrap()     
    #         return str(soup)
    #     for idx, (h4, p) in enumerate(zip(h4_list, p_list)):
    #         step_number = int(h4.get_text().strip().split()[1]) if h4 else ""
    #         step_text = p.get_text().strip() if p else ""
    #         step_text = clean_keep_strong(step_text)
    #         self.webpage["Directions"][f"step_{step_number}"] = step_text


    def load_data(self):
        if "allrecipes.com" in self.data_url:
            self.load_data_from_allrecipes()
        # elif "bonappetit.com" in self.data_url:
        #     self.load_data_from_bonappetit() # connot be used
        else:
            raise Exception("Unsupported website for data loading.")

    def _parse_ingredients(self):
        for ing in self.webpage.get("ingredients", []):
            quantity = ing.get("quantity") or ""
            measurement = ing.get("unit") or ""
            name_raw = ing.get("name") or ""
            full_text = f"{quantity} {measurement} {name_raw}".strip()

            def ingredients_filter(text):
                if not text:
                    return ""

                raw = text.strip()

                # remove extra info in parentheses and after "such as", "like"
                raw = re.sub(r"\(.*?\)", "", raw)

                # remove "such as X", "like X"
                raw = re.sub(r"\bsuch as\b.*", "", raw, flags=re.IGNORECASE)
                raw = re.sub(r"\blike\b.*", "", raw, flags=re.IGNORECASE)

                return raw

            name_raw = ingredients_filter(name_raw)

            descriptor = None
            preparation = None

            doc_main = self.nlp(name_raw)

            descriptors_list = []
            # find adj
            for token in doc_main:
                if token.pos_ in ["ADJ", "VERB"] and token.dep_ in ["amod", "acomp"]:
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
                if token.pos_ in ["NOUN", "PROPN", "ADJ"] and token.dep_ in ["compound", "amod"]:
                    name_list.append(token.text)
                if token.pos_ in ["NOUN", "PROPN"] and token.dep_ in ["nsubj", "ROOT", "dobj"]:
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

    def filter_methods(self, methods):
        input = self.keep_longest_unique(methods)

        STOP_WORDS = {
            "to", "be", "this", "that", "for", "with", "into", "on", "in", "of",
            "and", "or", "the", "a", "an", "it", "they", "allow", "remain"
        }

        input = [m for m in input if m not in STOP_WORDS]

        return input

    def keep_longest_unique(self, strings):
        strings = list(set(s.strip() for s in strings if s and s.strip()))
        strings.sort(key=len, reverse=True)

        result = []
        for s in strings:
            if not any(s in longer for longer in result):
                result.append(s)

        return result
    
    def split_into_atomic_steps(self, step_desc):
        """
        Split one direction paragraph into atomic actionable steps.
        Also extract warnings / observations / advice instead of dropping them.
        """
        doc = self.nlp(step_desc)

        # 1) First coarse split by punctuation
        raw_segments = re.split(r"[.;]", step_desc)

        atomic_segments = []
        special_notes = {
            "warnings": [],
            "advice": [],
            "observations": []
        }

        def classify_special(seg):
            s = seg.lower().strip()

            # warnings
            if s.startswith(("be careful", "be sure", "make sure", "ensure", "avoid ")):
                return "warnings"

            # advice
            if s.startswith(("you can", "you may", "it's okay", "it’s okay", "feel free")):
                return "advice"

            # observations
            if s.startswith(("this ", "that ", "it ", "the mixture will", "the sauce will")):
                return "observations"

            return None

        for seg in raw_segments:
            seg = seg.strip().strip(",")
            if not seg:
                continue

            # Remove leading filler words (“to”, “then”, “and”)
            seg = re.sub(r"^(to|then|and|so|but|or)\b", "", seg, flags=re.IGNORECASE).strip()
            if not seg:
                continue

            special_type = classify_special(seg)
            if special_type:
                special_notes[special_type].append(seg)
                continue  # Skip adding as step

            doc2 = self.nlp(seg)
            verbs = [t for t in doc2 if t.pos_ == "VERB"]

            if not verbs:
                continue  

            if len(seg.split()) <= 2 and len(verbs) == 0:
                continue
            atomic_segments.append(seg)

        return atomic_segments, special_notes
    
    def _parse_steps(self):
        self.context_state = {
            "oven_preheated": False,
            "oven_temperature": None,
            "prepared_items": set(),
        }

        directions = self.webpage.get("Directions", {})
        atomic_step_counter = 1

        for step_key, step_desc in directions.items():

            atomic_segments, special_notes = self.split_into_atomic_steps(step_desc)
            pending_special = special_notes

            for atomic_text in atomic_segments:

                parsed_step = self._parse_one_step(
                    atomic_text,
                    f"step_{atomic_step_counter}"
                )
                parsed_step["context"]["warnings"].extend(pending_special["warnings"])
                parsed_step["context"]["advice"].extend(pending_special["advice"])
                parsed_step["context"]["observations"].extend(pending_special["observations"])

                pending_special = {
                    "warnings": [],
                    "advice": [],
                    "observations": []
                }

                # Add to final steps list
                self.parsed_data["Steps"].append(parsed_step)
                atomic_step_counter += 1

        methods_raw = [m for step in self.parsed_data["Steps"] for m in step["methods"]]
        tools_raw = [t for step in self.parsed_data["Steps"] for t in step["tools"]]

        self.parsed_data["Methods"] = self.filter_methods(methods_raw)
        self.parsed_data["Tools"] = self.keep_longest_unique(list(dict.fromkeys(tools_raw)))

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

    def pos_filter_tool(self, tool, nlp):
        doc = nlp(tool)
        has_noun = any(t.pos_ in ["NOUN", "PROPN"] for t in doc)
        if not has_noun:
            return False
        last_token = doc[-1]
        if last_token.pos_ not in ["NOUN", "PROPN"]:
            return False
        banned_abstract = {"shape", "piece", "head", "turkey", "circle", "bottom", "center"}
        root = doc[0].lemma_
        if root in banned_abstract:
            return False
        return True
    
    def extract_temperature(self, text):
        t = text.lower()
        # ---- ignore angle (45 degree angle) ----
        if "degree angle" in t or "degrees angle" in t:
            return {}

        # ---- pattern 1: 350 degrees F ----
        m = re.search(r"(\d+)\s*degrees?\s*(f|c|°f|°c)", t)
        if m:
            num, unit = m.groups()
            return f"{num} degrees {unit.upper()}"

        # ---- pattern 2: 350°F / 350 °F / 350F ----
        m = re.search(r"(\d+)\s*°?\s*(f|c)", t)
        if m:
            num, unit = m.groups()
            return f"{num}°{unit.upper()}"

        # ---- pattern 3: 350 F (space but no degree symbol) ----
        m = re.search(r"(\d+)\s*(f|c)\b", t)
        if m:
            num, unit = m.groups()
            return f"{num}°{unit.upper()}"

        return {}


    def extract_time(self, text):
        text_l = text.lower()

        # 1) Time range: "5 to 10 minutes"
        m = re.search(r"(\d+)\s*(?:to|-|–)\s*(\d+)\s*(minute|minutes|min)", text_l)
        if m:
            t1, t2, unit = m.groups()
            return {
                "min": f"{t1} {unit}",
                "max": f"{t2} {unit}"
            }

        # 2) "about 5 minutes" / "for 5 minutes"
        m = re.search(r"(about|around|for)?\s*(\d+)\s*(minute|minutes|min)", text_l)
        if m:
            _, num, unit = m.groups()
            return f"{num} {unit}"

        # 3) hours + minutes "1 hour and 20 minutes"
        m = re.search(r"(\d+)\s*hour[s]?\s*(?:and)?\s*(\d+)?\s*(minute|minutes)?", text_l)
        if m:
            hr, mn, unit = m.groups()
            if mn:
                return f"{hr} hours {mn} minutes"
            return f"{hr} hours"

        return {}

    def _parse_one_step(self, step_desc, step_key):
        step_number = int(step_key.replace("step_", ""))
        step_dict = {
            "step_number": step_number,
            "description": step_desc,
            "ingredients": [],
            "tools": [],
            "methods": [],
            "time": {},
            "temperature": {},
            "context": {
                "references": [],
                "warnings": [],
                "advice": [],
                "observations": [],
                # initial context from global state (before this step's updates)
                "oven_preheated": self.context_state.get("oven_preheated"),
                "oven_temperature": self.context_state.get("oven_temp"),
                "available_mixtures": list(self.context_state.get("prepared_items", [])),
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
            "minutes", "minute", "hours", "hour", "secs", "seconds", "sec", "degrees", "degree","shape", "piece", "head", "turkey", "circle", "bottom", "center",
    "formation", "feathers", "beak", "brownie", "line", "half",
        }
        TOOL_NOISE_SIMPLE = {
            "f", "c", "°f", "°c"
        }

        # ---- Methods (verbs) ----
        for token in doc_step:
            if token.pos_ == "VERB":
                step_dict["methods"].append(token.lemma_)

        step_dict["methods"] = unique_keep_order(step_dict["methods"])

        # ---- Noun phrases ----
        noun_phrase = self.extract_noun_phrases(doc_step)
        noun_phrase = filter_longest_phrases(noun_phrase)

        # ---- Ingredients matching ----
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

                np_tokens = np_low.split()
                ing_tokens = ing_low.split()
                for np_token in np_tokens:
                    if np_token in ing_tokens:
                        matched.append(np)
                        step_dict["ingredients"].append(np)
                        break

        step_dict["ingredients"] = unique_keep_order(step_dict["ingredients"])

        # ---- Tools: noun phrases not used as ingredients, + filters ----
        tools_raw = [np for np in noun_phrase if np not in matched]

        tools_clean = []
        for t in tools_raw:
            t_low = t.lower()
            if any(noise in t_low for noise in TOOL_NOISE):
                continue
            if any(ch.isdigit() for ch in t_low):
                continue
            if t_low in TOOL_NOISE_SIMPLE:
                continue
            if not self.pos_filter_tool(t, self.nlp):
                continue
            tools_clean.append(t)

        step_dict["tools"] = unique_keep_order(tools_clean)

        # ---- Differentiate information types: warnings / advice / observations ----
        # warnings
        for pat in self.WARNING_PATTERNS:
            m = pat.search(step_desc)
            if m:
                step_dict["context"]["warnings"].append(step_desc[m.start():].strip())

        # advice
        for pat in self.ADVICE_PATTERNS:
            m = pat.search(step_desc)
            if m:
                step_dict["context"]["advice"].append(step_desc[m.start():].strip())

        # observations
        for pat in self.OBS_PATTERNS:
            m = pat.search(step_desc)
            if m:
                step_dict["context"]["observations"].append(step_desc[m.start():].strip())

        # ---- Update global context_state AFTER interpreting this step ----
        # 1) Oven preheat
        if ("preheat" in step_dict["methods"] or "pre-heatt" in step_desc.lower()) and step_dict["temperature"]:
            self.context_state["oven_preheated"] = True
            self.context_state["oven_temp"] = step_dict["temperature"]

        # 2) Mixture creation (combine / mix / stir)
        if any(m in step_dict["methods"] for m in ["combine", "mix", "stir"]):
            # create a generic mixture name tied to this step
            mixture_name = f"mixture_step_{step_number}"
            self.context_state["prepared_items"].add(mixture_name)

        # time extraction
        time_info = self.extract_time(step_desc)
        step_dict["time"] = time_info

        # temperature extraction
        temp_info = self.extract_temperature(step_desc)
        step_dict["temperature"] = temp_info

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
        self._parse_ingredients()
        self._parse_steps()
        self._add_other_info()
        return self.parsed_data

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
        step = "Combine chicken, 1 tablespoon oil, 1 teaspoon Greek seasoning, paprika, garlic, and salt in a bowl. Stir until well coated; set aside."
        doc_step = parser.nlp(step)
        doc_step = parser.fix_imperative_verbs(doc_step)
        parsed = parser._parse_one_step(step, "step_1")
        print(parsed)

    @staticmethod
    def show_parsed_data():
        string = "the center"
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(string)
        for token in doc:
            print(f"{token.text}: {token.pos_} {token.dep_} {token.morph}")

    @staticmethod
    def test_crawling():
        parser = Parser("https://www.bonappetit.com/recipe/make-ahead-gravy")
        parser.load_data()
        from pprint import pprint
        pprint(parser.webpage)


if __name__ == "__main__":
    parser = Parser("https://www.allrecipes.com/spiral-spicy-cucumber-salad-recipe-11814637/")
    parsed = parser.parse()
    from pprint import pprint
    pprint(parser.webpage)
    pprint(parsed)

    # Parser.show_parsed_data()
    # Parser.test_crawling()