import streamlit as st
import requests
import json
from rapidfuzz import process, fuzz

# Correct way to pull from Streamlit Cloud Secrets
API_KEY = st.secrets["SERPER_API_KEY"]

# Noise words to strip out from Google's correction before returning
NOISE_WORDS = [
    "medicine", "Medicine",
    "india", "India",
    "tablet", "Tablet",
    "tablets", "Tablets",
    "drug", "Drug",
    "generic", "Generic",
    "ip", "IP",
    "bp", "BP",
]

def clean_suggestion(raw):
    """
    Strips all noise/context words that we injected into the query
    so that what's returned is purely the corrected medicine name.
    """
    result = raw
    for word in NOISE_WORDS:
        result = result.replace(word, "")
    result = " ".join(result.split())  # collapse multiple spaces
    return result.strip().capitalize()


def get_spelling_suggestion(query):
    """
    Asks Google for a spelling correction via the Serper API.

    Strategy:
    - We send the query with extra context ("medicine india") so Google
      has enough signal to correct even heavily misspelled words.
    - We handle BOTH response formats Google uses:
        1. data["spelling"]                              -> direct correction
        2. data["searchInformation"]["showingResultsFor"] -> forced redirect
    - After getting the suggestion, we strip all the context words we
      added so only the corrected medicine name is returned.
    - We also try a SECOND pass with just the raw query (no prefix) as a
      fallback, since some medicine names confuse Google when "medicine"
      is prepended.
    """
    url = "https://google.serper.dev/search"

    headers = {
        'X-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }

    def query_serper(q):
        payload = json.dumps({"q": q, "gl": "in"})
        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"❌ Serper API Error: {response.status_code} - {response.text}")
            return None
        data = response.json()

        if "spelling" in data:
            return data["spelling"]
        elif (
            "searchInformation" in data
            and "showingResultsFor" in data["searchInformation"]
        ):
            return data["searchInformation"]["showingResultsFor"]
        return None

    try:
        # Pass 1: query with context for better Google correction
        raw = query_serper(f"{query} medicine india")

        # Pass 2 fallback: bare query, sometimes works better
        if not raw:
            raw = query_serper(query)

        if raw:
            return clean_suggestion(raw)

        return None

    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None


def get_local_fuzzy_suggestion(query, name_list, threshold=70):
    """
    Fallback when Serper returns nothing.
    Fuzzy-matches the query against all medicine names in the local
    database using rapidfuzz. Returns the best matching name or None.
    """
    query_clean = query.strip().lower()
    result = process.extractOne(
        query_clean,
        name_list,
        scorer=fuzz.WRatio,
        score_cutoff=threshold
    )
    if result:
        return result[0]  # returns the matched name
    return None


# Standalone Test Block
if __name__ == "__main__":
    test_cases = ["mteformn", "betadlme", "betadlne", "dol9", "crocn", "azthromycin"]

    for test_word in test_cases:
        print(f"\nTesting: '{test_word}'")
        result = get_spelling_suggestion(test_word)
        if result:
            print(f"  ✅ Serper corrected to: {result}")
        else:
            print(f"  ⚠️  Serper returned nothing — local fuzzy would kick in.")
