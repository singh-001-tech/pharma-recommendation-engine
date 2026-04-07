import streamlit as st
import pandas as pd
import re

# ==========================================
# PART 1: ORIGINAL MATCHING LOGIC
# ==========================================

def combine_sheets(file_dict):
    """Combines all sheets from an Excel file into one DataFrame."""
    return pd.concat(file_dict.values(), ignore_index=True)

@st.cache_data
def load_data():
    """Loads all Market and Jan Aushadhi files and prepares the Salt Sets."""
    # 1. LOAD MARKET FILES
    m_int = pd.read_excel("Internal_Medicines_FINAL.xlsx", sheet_name=None)
    m_ext = pd.read_excel("External_Medicines_FINAL.xlsx", sheet_name=None)
    m_spec = pd.read_excel("Specialized_Medicines_FINAL.xlsx", sheet_name=None)
    
    market_df = pd.concat([combine_sheets(m_int), combine_sheets(m_ext), combine_sheets(m_spec)], ignore_index=True)
    market_df['source'] = 'market'

    # 2. LOAD JAN AUSHADHI FILES
    j_int = pd.read_excel("internal_medicines_jan.xlsx", sheet_name=None)
    j_ext = pd.read_excel("external_medicines_jan.xlsx", sheet_name=None)
    j_spec = pd.read_excel("specialised_medicines_jan.xlsx", sheet_name=None)
    
    jan_df = pd.concat([combine_sheets(j_int), combine_sheets(j_ext), combine_sheets(j_spec)], ignore_index=True)
    jan_df['source'] = 'jan'

    # 3. COMBINE DATASETS
    combined = pd.concat([market_df, jan_df], ignore_index=True)
    
    # 4. GENERATE SALT SETS FOR MATCHING
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
    """Original logic to extract numerical strength for comparison."""
    try:
        if pd.isna(strength): return None
        value = ''.join([c for c in str(strength).lower() if c.isdigit() or c == '.'])
        return float(value) if value else None
    except: return None

def check_strength_match(input_row, candidate_row, tolerance=0.10):
    """Original logic to determine if dosage matches within 10%."""
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

st.set_page_config(page_title="Pharma Recommendation Engine", layout="wide")
st.title("💊 Medicine Recommendation & Savings Engine")
st.markdown("---")

# Load data with a spinner
try:
    with st.spinner("Initializing medicine database..."):
        df = load_data()
except Exception as e:
    st.error(f"Error loading files: {e}")
    st.stop()

# REQUIREMENT 1: Searchable Dropdown
all_meds = sorted(df['name'].dropna().unique().tolist())
selected_medicine = st.selectbox(
    "Type or select your medicine name:", 
    options=all_meds, 
    index=None, 
    placeholder="Search for a medicine..."
)

if selected_medicine:
    # Get the details of the selected medicine
    input_row = df[df['name'] == selected_medicine].iloc[0]
    
    # NEW USER INPUTS: Consumption Details
    with st.expander("📊 Customize Your Savings Calculation", expanded=True):
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            units_per_purchase = st.number_input("Total units purchased each time (e.g. tablets in a strip):", min_value=1, value=10)
        with col_input2:
            purchases_per_month = st.number_input("How many times do you purchase this per month?", min_value=1, value=1)
    
    # Calculate total units consumed
    total_monthly_units = units_per_purchase * purchases_per_month
    total_yearly_units = total_monthly_units * 12

    st.info(f"**Selected:** {input_row['name']} | **Category:** {input_row['Header_Category']} | **Price/Unit:** ₹{input_row['price_per_unit']:.2f}")

    # FILTER CANDIDATES
    candidates = df[
        (df['salt_set'] == input_row['salt_set']) & 
        (df['Header_Category'] == input_row['Header_Category']) & 
        (df['name'] != input_row['name'])
    ]

    results = []
    for _, row in candidates.iterrows():
        match_type = check_strength_match(input_row, row)
        if match_type != "no_match":
            # REVISED SAVINGS LOGIC: Based on user consumption
            ppu_diff = input_row['price_per_unit'] - row['price_per_unit']
            results.append({
                "name": row['name'],
                "price": row['price_per_unit'],
                "monthly": ppu_diff * total_monthly_units,
                "yearly": ppu_diff * total_yearly_units,
                "confidence": "High" if match_type == "exact" else "Medium",
                "source": row['source']
            })

    if results:
        # Sort by lowest price
        res_df = pd.DataFrame(results).sort_values('price').head(5)
        
        st.subheader("💡 Recommended Alternatives")
        st.warning("📢 **Consult a certified medical professional or pharmacist before switching medications**")

        for _, row in res_df.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    jan_tag = " ✅ **(Available in Jan Aushadhi list)**" if row['source'] == 'jan' else ""
                    st.markdown(f"#### {row['name']}{jan_tag}")
                    st.write(f"Confidence Score: **{row['confidence']}**")
                
                with col2:
                    st.metric("Price per Unit", f"₹{row['price']:.2f}")
                
                with col3:
                    if row['yearly'] > 0:
                        st.write(f"**Your Est. Monthly Savings:** ₹{row['monthly']:.2f}")
                        st.markdown(f"### Yearly Savings: ₹{row['yearly']:.2f}")
                    else:
                        st.write("*(Price is higher or same)*")
    else:
        st.error("No suitable alternatives found for this medicine composition.")