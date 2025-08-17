import requests
from bs4 import BeautifulSoup
# --- THE DEFINITIVE FIX IS HERE ---
from ddgs import DDGS # Changed from 'duckduckgo_search' to 'ddgs'
# ----------------------------------
import re

def web_search(query: str) -> str:
    """Performs a web search using DuckDuckGo and returns the top 5 results."""
    print(f"> Searching the web for: '{query}'")
    try:
        # This part of the code was already correct and works with the new library
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
        if not results:
            return "No search results found."
        return "\n".join([f"{i+1}. {r['title']} ({r['href']})" for i, r in enumerate(results)])
    except Exception as e:
        return f"Error performing web search: {e}"

def scrape_webpage(url: str) -> str:
    """Scrapes the textual content of a webpage."""
    print(f"> Reading content from: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join(p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3']))
        clean_text = re.sub(r'\s{2,}', ' ', text).strip()
        return f"Content from '{url}' (first 4000 chars):\n{clean_text[:4000]}"
    except Exception as e:
        return f"Error scraping webpage '{url}': {e}"