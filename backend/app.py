from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import ollama
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def generate_search_query(user_query):
    base_query = f"Genera una query di ricerca Google per trovare informazioni ufficiali del governo italiano su: '{user_query}'. Fornisci solo il testo della query di ricerca e nient'altro. Includi 'site:gov.it' per cercare nei siti governativi ufficiali."

    message = {'role': 'user', 'content': base_query}

    response = ollama.chat(model='llama3.2', messages=[message])
    # Extract the content from the response
    search_query = extract_response_content(response)
    if search_query:
        print("Generated Search Query:", search_query)
    else:
        print("Failed to generate search query from response:", response)
        search_query = ""

    return search_query

def extract_response_content(response):
    """Helper function to extract content from the Ollama response."""
    if isinstance(response, dict):
        if 'content' in response:
            return response['content'].strip()
        elif 'message' in response and 'content' in response['message']:
            return response['message']['content'].strip()
        elif 'response' in response:
            return response['response'].strip()
        else:
            print("Unexpected response format:", response)
            return None
    elif isinstance(response, str):
        return response.strip()
    else:
        print("Response is neither dict nor str:", type(response))
        return None

def search_google(search_query):
    api_key = "f6790a37ddfa459a870182f81307c1bc3cca83203797a83c487300b150237bc8"  # Replace with your actual SerpAPI key
    params = {
        "q": search_query,
        "api_key": api_key,
        "num": 1,  # Get only the top result
        "hl": "it",  # Set language to Italian
        "gl": "it"   # Set country to Italy
    }
    print("Sending Search Query to SerpAPI:", search_query)
    
    response = requests.get("https://serpapi.com/search", params=params)
    if response.status_code == 200:
        search_results = response.json()
        if 'organic_results' in search_results and search_results['organic_results']:
            top_result = search_results['organic_results'][0]
            link = top_result.get('link')
            snippet = top_result.get('snippet', '')
            return link, snippet
        else:
            print("No organic results for this query:", search_query)
    else:
        print("Error from SerpAPI:", response.status_code, response.text)
    
    return None, "Could not find relevant information."

def run_scraper(url):
    """Run scraper.py on the specified URL to crawl and store content."""
    try:
        result = subprocess.run(['python', 'scraper.py', url], capture_output=True, text=True)
        if result.returncode == 0:
            print("Scraper ran successfully.")
            return True
        else:
            print("Error running scraper:", result.stderr)
            return False
    except Exception as e:
        print("Exception while running scraper:", e)
        return False

def load_scraped_data(filename="crawled_data.json"):
    """Load scraped data from a JSON file."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    else:
        print(f"{filename} does not exist.")
        return []

def query_llama_with_data(user_query, crawled_data, source_link):
    """Send the user query and crawled data to Llama for final answer."""
    context_text = " ".join([entry['content'] for entry in crawled_data])
    prompt = f"""
Sei un assistente che fornisce informazioni basate su fonti ufficiali del governo italiano. Rispondi alla seguente domanda in modo chiaro e conciso, utilizzando esclusivamente le informazioni pertinenti presenti nel testo sottostante. Ignora qualsiasi contenuto non correlato alla domanda, come menu di navigazione, footer o informazioni di contatto.

**Domanda:**
{user_query}

**Risposta:**
(Fornisci la risposta qui.)

**Testo della Fonte:**
{context_text}

**Nota:**
- Scrivi la risposta in italiano.
- Alla fine della risposta, aggiungi 'Fonte:' seguito dal link alla fonte.
"""
    response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])

    # Extract the content from the response
    answer = extract_response_content(response)
    if answer:
        return answer.strip()
    else:
        return "Non è stato possibile ottenere una risposta."

def process_query(user_query):
    # Remove crawled_data.json if it exists
    if os.path.exists("crawled_data.json"):
        os.remove("crawled_data.json")

    search_query = generate_search_query(user_query)
    link, snippet = search_google(search_query)
    
    if link:
        # Step 1: Run the scraper on the found URL
        if run_scraper(link):
            # Step 2: Load the scraped content
            crawled_data = load_scraped_data()
            if crawled_data:
                # Step 3: Query Llama with the crawled data and return answer
                source_link = link
                return query_llama_with_data(user_query, crawled_data, source_link)
            else:
                return "Non è stato possibile caricare i dati estratti."
        else:
            return "La scansione del sito non è riuscita."
    else:
        return "Non è stato possibile trovare informazioni pertinenti."

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'error': 'Nessuna domanda fornita.'}), 400
    
    answer = process_query(user_query)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
