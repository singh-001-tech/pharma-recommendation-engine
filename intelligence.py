import streamlit as st
import requests
import json

# Correct way to pull from Streamlit Cloud Secrets
API_KEY = st.secrets["SERPER_API_KEY"]

def get_spelling_suggestion(query):
    """
    Asks Google for a spelling correction using a hybrid check for 
    both 'spelling' and 'showingResultsFor' keys.
    """
    url = "https://google.serper.dev/search"
    
    payload = json.dumps({
        "q": f"medicine {query}",
        "gl": "in" 
    })
    
    headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        
        if response.status_code != 200:
            print(f"❌ Serper API Error: {response.status_code} - {response.text}")
            return None
            
        data = response.json()
        suggestion = None

        # Logic to catch both types of Google corrections
        if "spelling" in data:
            suggestion = data["spelling"]
        elif "searchInformation" in data and "showingResultsFor" in data["searchInformation"]:
            suggestion = data["searchInformation"]["showingResultsFor"]

        if suggestion:
            # Clean the suggestion to remove our 'medicine' keyword
            clean_suggestion = suggestion.replace("medicine", "").replace("Medicine", "").strip()
            return clean_suggestion.capitalize()
            
        return None

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

# Standalone Test Block
if __name__ == "__main__":
    test_word = "mteformn"
    print(f"Testing Intelligence Layer for: '{test_word}'")
    result = get_spelling_suggestion(test_word)
    if result:
        print(f"✅ Success! Google corrected it to: {result}")
    else:
        print("⚠️ No suggestion found.")