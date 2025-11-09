from bs4 import BeautifulSoup
import requests

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
        self.data = None

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
        print(self.webpage)

    def parse(self):
        self.load_data()
        # Implement parsing logic here
        pass

# TA suggested sentence splitting within steps