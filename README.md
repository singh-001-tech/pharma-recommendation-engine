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

## **Safety Disclaimer**
📢 **Note:** This tool is for informational and educational purposes only. Users are strictly advised to **consult a certified medical professional or pharmacist** before switching medications.