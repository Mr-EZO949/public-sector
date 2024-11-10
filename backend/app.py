from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import ollama

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


def generate_dork_queries(user_query):
    # Generate multiple prompts for different Dork queries
    base_query = f"Generate a Google Dork query to find official Italian government information on: '{user_query}'. Provide only the query code, AND NOTHING ELSE"

    # Define a list of variations to try
    messages = [
        {'role': 'user', 'content': base_query + " Include 'site:gov.it' for official sources."},
        {'role': 'user', 'content': base_query + " Include keywords like 'site:agenziaentrate.gov.it'."},
        {'role': 'user', 'content': base_query + " Use terms like 'apply' or 'how to' if relevant."},
        {'role': 'user', 'content': base_query + " Include specific keywords related to taxes, health, etc."}
    ]

    # Generate a list of Dork queries
    dork_queries = []
    for message in messages:
        response = ollama.chat(model='llama3.2', messages=[message])
        if 'message' in response and 'content' in response['message']:
            dork_query = response['message']['content']
            dork_queries.append(dork_query)
            print("Generated Dork Query:", dork_query)  # Print each generated query for debugging
        else:
            print("Unexpected response format:", response)  # Print any unexpected structure for debugging

    return dork_queries

# Function to search Google with the Dork query using SerpAPI
import requests

def search_google(dork_queries):
    api_key = "fa08a6c2d1897b4bd560b25095e87c16429bc1c0ae3ea78265fb578e0ab29f5a"  # Replace with your SerpAPI key
    # Loop through each generated Dork query
    for dork_query in dork_queries:
        params = {"q": dork_query, "api_key": api_key}
        print("Sending Dork Query to SerpAPI:", dork_query)  # Log the current Dork query
        
        response = requests.get("https://serpapi.com/search", params=params)

        if response.status_code == 200:
            search_results = response.json()
            
            # Check if 'organic_results' exists in the response
            if 'organic_results' in search_results and search_results['organic_results']:
                top_result = search_results['organic_results'][0]
                return top_result['link'], top_result['snippet']
            else:
                print("No organic results for this query:", dork_query)  # Log for debugging
        else:
            print("Error from SerpAPI:", response.status_code, response.text)  # Log error details
    
    # If no results found after all queries
    return None, "Could not find relevant information."


# Function to process the final query and return relevant information
def process_query(user_query):
    # Step 1: Generate a Dork query
    dork_query = generate_dork_queries(user_query)
    
    # Step 2: Search Google with the generated Dork query
    best_url, snippet = search_google(dork_query)
    
    # Step 3: Return the search result or an error message
    if best_url:
        return f"Here is a relevant link: {best_url} \n\nSnippet: {snippet}"
    else:
        return "Could not find relevant information."

# Flask route to handle incoming queries
@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user_query = data.get('query', '')
    
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Process the query to get the final answer
    answer = process_query(user_query)
    return jsonify({'answer': answer})

if __name__ == '__main__':
    app.run(debug=True)
