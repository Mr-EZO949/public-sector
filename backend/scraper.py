import requests
import json
import sys
import os
from bs4 import BeautifulSoup

def crawl_and_retrieve_url(url):
    """Crawl the specified URL and retrieve the main content."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        page_content = response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL {url}:", e)
        return []

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Remove unwanted elements
    for element in soup(['header', 'footer', 'nav', 'aside', 'form', 'script', 'style']):
        element.decompose()

    # Extract the main content
    main_content = soup.get_text(separator=' ', strip=True)

    # Prepare the crawled data
    crawled_data = [{"url": url, "content": main_content}]

    return crawled_data

def save_data_to_file(data, filename="crawled_data.json"):
    """Save crawled data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Crawled data saved to {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]

    # Crawl and retrieve content
    crawled_data = crawl_and_retrieve_url(url)
    
    # Save the result to a file
    if crawled_data:
        save_data_to_file(crawled_data, filename="crawled_data.json")
