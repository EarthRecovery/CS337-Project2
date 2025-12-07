"""
Web scraper for recipe URLs.
Fetches HTML content from recipe websites.
"""

import requests
from bs4 import BeautifulSoup


class RecipeScraper:
    """Scrapes recipe content from URLs."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch_recipe(self, url):
        """
        Fetch recipe HTML from URL.

        Args:
            url: Recipe URL to scrape

        Returns:
            dict with 'html', 'cleaned_html', and 'title' keys, or None if failed
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # Get raw HTML
            raw_html = response.text

            # Also create a cleaned version 
            soup = BeautifulSoup(response.content, 'html.parser')

        
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()

          
            for comment in soup.find_all(text=lambda text: isinstance(text, type(soup.find_all()[0]))):
                if hasattr(comment, 'extract'):
                    comment.extract()

            cleaned_html = str(soup)

            # Extract title
            title = soup.title.string if soup.title else 'Unknown Recipe'

            return {
                'url': url,
                'raw_html': raw_html,
                'cleaned_html': cleaned_html,
                'title': title
            }

        except Exception as e:
            print(f"Error fetching recipe: {e}")
            return None
