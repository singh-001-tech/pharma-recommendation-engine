import streamlit as st
import requests
import json

API_KEY = st.secrets["SERPER_API_KEY"]

def get_spelling_suggestion(query):
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": f"medicine {query}", "gl": "in"})
    headers = {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"❌ Serper API Error: {response.status_code} - {response.text}")
            return None
        data = response.json()
        suggestion = None
        if "spelling" in data:
            suggestion = data["spelling"]
        elif "searchInformation" in data and "showingResultsFor" in data["searchInformation"]:
            suggestion = data["searchInformation"]["showingResultsFor"]

        if suggestion:
            clean_suggestion = suggestion.replace("medicine", "").replace("Medicine", "").strip()
            return clean_suggestion.capitalize()
        return None
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

if __name__ == "__main__":
    test_word = "mteformn"
    print(f"Testing Intelligence Layer for: '{test_word}'")
    result = get_spelling_suggestion(test_word)
    if result:
        print(f"✅ Success! Google corrected it to: {result}")
    else:
        print("⚠️ No suggestion found.")