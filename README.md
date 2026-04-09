# 💊 Pharma-Saving-Recommendations-Engine (Phase 1)

## **Project Overview**
In the Indian pharmaceutical market, branded medicines often come with a significant markup. This project is a data-driven solution designed to help consumers find **Jan Aushadhi (generic)** alternatives that are chemically identical but significantly more affordable.

### **Core Impact Metrics**
* **Matching Accuracy:** ✨ **97.42%** (Validated against 25,000 test cases)
* **Data Scale:** Processed over **250,000+ medicine records**
* **Average Savings:** Potential for **80-90% reduction** in monthly medical expenses

---

## **How the Recommendation Engine Works**
I built a custom matching logic to ensure clinical safety and accuracy. Instead of simple keyword searches, the engine uses:

1. **Salt-Set Matching:** It extracts active chemical ingredients (e.g., Paracetamol) and treats them as a Python Set. This ensures that even if ingredients are listed in a different order, a match is found.
2. **10% Strength Tolerance:** The engine parses dosage strengths (e.g., 500mg) and validates that the generic alternative is within a $10\%$ range of the branded version.
3. **Form Factor Locking:** It ensures that "Tablets" are only compared to "Tablets," preventing incorrect recommendations between different delivery methods (like creams vs. pills).



---

## **Technical Stack**
* **Language:** Python 3.x
* **Interface:** Streamlit (Web Application)
* **Data Processing:** Pandas, OpenPyXL
* **Version Control:** Git & GitHub

---

## **Project Structure**
* `app.py`: The live web application logic and UI.
* `medicine_recommendation_engine_v1.py.ipynb`: The research lab where matching logic was developed and accuracy was tested.
* `/data`: Processed Excel databases categorized by medicine type (Internal, External, Specialized).
* `dcleaning.ipynb` & `jan_aushadhi.ipynb`: The ETL pipeline notebooks used to clean 250k+ raw records.

---

# 💊 Pharma-Saving-Recommendations-Engine (Phase 2: AI Intelligence Layer)

## **Project Evolution**
While Phase 1 focused on the clinical accuracy of medicine matching, **Phase 2** elevates the system into a production-ready application by solving for "The Human Element." This phase introduces a multi-tiered search architecture that handles typos, fuzzy queries, and ensures enterprise-grade security for sensitive credentials.

### **Phase 2 Core Impact**
* **Accessibility:** Enabled users with zero technical medical knowledge to find records despite complex spellings.
* **Architecture:** Decoupled the AI logic into a modular `intelligence.py` script for better maintainability.
* **Security:** Implemented zero-leakage protocols for API management using Streamlit Secrets.

---

## **🚀 Key Feature Upgrades**

### **1. Search-Augmented Intelligence (SAI)**
Integrated the **Serper API** to act as the engine's "Global Brain." 
- **Auto-Correction:** The system now catches and fixes pharmaceutical typos (e.g., `mteformn` → `Metformin`).
- **Hybrid Response Handling:** Engineered a custom parser to handle both Google-style "Did you mean" (spelling suggestions) and "Showing results for" (forced corrections).

### **2. Hybrid Fuzzy Search UI**
Redesigned the search experience to combine the flexibility of text input with the precision of dropdown menus:
- **Regex Fuzzy Filtering:** Implemented `str.contains()` logic in Pandas to filter 250k+ records in real-time.
- **Dynamic Selection:** Once the AI identifies the correct salt/brand, the UI dynamically populates a dropdown with specific variants (strengths, forms, and packs) from the local database.

### **3. Enterprise Security & DevOps**
Shifted from hard-coded configurations to professional environment management:
- **Secrets Management:** Utilized `st.secrets` (TOML-based) to hide API credentials.
- **Repository Shielding:** Configured `.gitignore` to prevent accidental exposure of private keys and large-scale Excel databases to public repositories.

---

## **🛠 Phase 2 Technical Stack**
* **AI Layer:** Serper (Search-Augmented Intelligence)
* **Frontend/State:** Streamlit (Session State management)
* **Data Processing:** Pandas (Fuzzy matching & result filtering)
* **Security:** Streamlit Secrets & Git Version Control

---

## **How it Works: The Intelligence Gate**
1. **Local Search:** Checks the 250,000+ local records for the exact or partial string.
2. **AI Correction:** If zero local matches are found, the `intelligence.py` module queries the Serper API.
3. **Local Validation:** The AI suggestion is cross-referenced with the local dataset to ensure the engine only suggests medicines for which it has pricing data.
4. **Contextual UI:** The UI triggers a "Did you mean?" prompt, which, when clicked, updates the search state and re-runs the local matching logic.

---

## **Safety Disclaimer**
📢 **Note:** This tool is for informational and educational purposes only. Users are strictly advised to **consult a certified medical professional or pharmacist** before switching medications.