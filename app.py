import streamlit as st
import pandas as pd
from intelligence import get_spelling_suggestion

# ==========================================
# PART 1: DATA LOADING & MATCHING LOGIC
# ==========================================

def combine_sheets(file_dict):
    return pd.concat(file_dict.values(), ignore_index=True)

@st.cache_data
def load_data():
    m_int = pd.read_excel("Internal_Medicines_FINAL.xlsx", sheet_name=None)
    m_ext = pd.read_excel("External_Medicines_FINAL.xlsx", sheet_name=None)
    m_spec = pd.read_excel("Specialized_Medicines_FINAL.xlsx", sheet_name=None)
    market_df = pd.concat([combine_sheets(m_int), combine_sheets(m_ext), combine_sheets(m_spec)], ignore_index=True)
    market_df['source'] = 'market'

    j_int = pd.read_excel("internal_medicines_jan.xlsx", sheet_name=None)
    j_ext = pd.read_excel("external_medicines_jan.xlsx", sheet_name=None)
    j_spec = pd.read_excel("specialised_medicines_jan.xlsx", sheet_name=None)
    jan_df = pd.concat([combine_sheets(j_int), combine_sheets(j_ext), combine_sheets(j_spec)], ignore_index=True)
    jan_df['source'] = 'jan'

    combined = pd.concat([market_df, jan_df], ignore_index=True)
    combined['name_clean'] = combined['name'].str.strip().str.lower()
    
    def extract_salt_set(row):
        salts = []
        for i in range(1, 4):
            name = row.get(f'Salt {i} Name')
            if pd.notna(name) and str(name).strip().lower() != "na":
                salts.append(str(name).strip().lower())
        return set(salts)
    combined['salt_set'] = combined.apply(extract_salt_set, axis=1)
    return combined

def extract_strength_value(strength):
    try:
        if pd.isna(strength): return None
        value = ''.join([c for c in str(strength).lower() if c.isdigit() or c == '.'])
        return float(value) if value else None
    except: return None

def check_strength_match(input_row, candidate_row, tolerance=0.10):
    exact = True
    for i in range(1, 4):
        in_s = extract_strength_value(input_row.get(f'Salt {i} Strength'))
        can_s = extract_strength_value(candidate_row.get(f'Salt {i} Strength'))
        if in_s and can_s:
            if in_s != can_s: exact = False
            if not (in_s * (1 - tolerance) <= can_s <= in_s * (1 + tolerance)):
                return "no_match"
    return "exact" if exact else "tolerance"

# ==========================================
# PART 2: WEBSITE INTERFACE (Streamlit)
# ==========================================

st.set_page_config(page_title="Pharma Recommendation Engine", layout="wide", page_icon="💊")

# --- GLOBAL DISCLAIMER ---
st.error("⚠️ **MEDICAL DISCLAIMER:** This tool is for informational purposes only and is NOT a substitute for professional medical advice. Always consult a certified doctor before changing or starting any medication.")

st.title("💊 Medicine Recommendation & Savings Engine")
st.markdown("---")

try:
    with st.spinner("Initializing 250k+ records..."):
        df = load_data()
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

if 'search_term' not in st.session_state:
    st.session_state['search_term'] = ""

search_query = st.text_input(
    "Search for your medicine:", 
    value=st.session_state['search_term'],
    placeholder="Type name here (e.g., Dolo, Metformin, Crocn)..."
)

selected_medicine = None

if search_query:
    query_clean = search_query.strip().lower()
    matches = df[df['name_clean'].str.contains(query_clean, na=False)]
    
    if not matches.empty:
        selected_medicine = st.selectbox(
            f"Select from {len(matches)} matches found in our database:",
            options=sorted(matches['name'].unique().tolist()),
            index=None,
            placeholder="Select the exact variant..."
        )
    else:
        with st.spinner("Checking spelling..."):
            suggestion = get_spelling_suggestion(search_query)
        
        if suggestion:
            suggestion_clean = suggestion.strip().lower()
            ai_matches = df[df['name_clean'].str.contains(suggestion_clean, na=False)]
            
            if not ai_matches.empty:
                st.warning(f"No records found for '{search_query}'.")
                if st.button(f"👉 Did you mean: {suggestion}?"):
                    st.session_state['search_term'] = suggestion
                    st.rerun()
            else:
                st.error(f"We found '{suggestion}' online, but it isn't in our current database.")
        else:
            st.error(f"'{search_query}' not found. Please verify the name.")

# --- UPDATED RESULTS SECTION ---
if selected_medicine:
    input_row = df[df['name'] == selected_medicine].iloc[0]
    
    with st.container(border=True):
        st.success(f"### Selected: {input_row['name']}")
        
        # Display Salts and Strengths for the selected medicine
        st.write("**Chemical Composition:**")
        cols = st.columns(3)
        for i in range(1, 4):
            salt_name = input_row.get(f'Salt {i} Name')
            salt_strength = input_row.get(f'Salt {i} Strength')
            if pd.notna(salt_name) and str(salt_name).lower() != "na":
                with cols[i-1]:
                    st.markdown(f"🔬 **{salt_name}**")
                    st.caption(f"Strength: {salt_strength}")
    
    st.markdown("---")
    
    with st.expander("📊 Customize Your Savings Calculation", expanded=True):
        c1, c2 = st.columns(2)
        with c1: u_p = st.number_input("Units per purchase:", min_value=1, value=10)
        with c2: p_m = st.number_input("Purchases per month:", min_value=1, value=1)
    
    yearly_units = u_p * p_m * 12
    st.info(f"**Current Price:** ₹{input_row['price_per_unit']:.2f} per unit")

    candidates = df[(df['salt_set'] == input_row['salt_set']) & 
                    (df['Header_Category'] == input_row['Header_Category']) & 
                    (df['name'] != input_row['name'])]

    results = []
    for _, row in candidates.iterrows():
        match_type = check_strength_match(input_row, row)
        if match_type != "no_match":
            diff = input_row['price_per_unit'] - row['price_per_unit']
            results.append({
                "name": row['name'], "price": row['price_per_unit'],
                "yearly": diff * yearly_units, "source": row['source']
            })

    if results:
        res_df = pd.DataFrame(results).sort_values('price').head(5)
        st.subheader("💡 Recommended Alternatives")
        for _, row in res_df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    tag = " ✅ (Jan Aushadhi)" if row['source'] == 'jan' else " 🏥 (Private Generic)"
                    st.markdown(f"#### {row['name']}{tag}")
                with col2: st.metric("Price/Unit", f"₹{row['price']:.2f}")
                with col3:
                    if row['yearly'] > 0: st.markdown(f"### Savings: ₹{row['yearly']:.2f}/yr")
    else:
        st.error("No cheaper alternatives found.")

    if st.button("Start New Search"):
        st.session_state['search_term'] = ""
        st.rerun()