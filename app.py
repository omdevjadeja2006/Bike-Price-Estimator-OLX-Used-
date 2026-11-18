import streamlit as st
import requests

st.set_page_config(
    page_title="Used Motorcycle Price Estimator",
    page_icon="🏍️",
    layout="centered"
)

# Set backend endpoint URL (adjust IP if running across local Wi-Fi)
API_BASE_URL = "http://127.0.0.1:8000"

st.title("🏍️ Motorcycle Market Price Estimator")
st.write("Get an instant fair market valuation and realistic negotiation range based on machine learning.")

st.markdown("---")


@st.cache_data(ttl=600)
def load_categories():
    try:
        res = requests.get(f"{API_BASE_URL}/categories", timeout=3)
        if res.status_code == 200:
            return res.json()
    except Exception:
        return None
    return None


categories = load_categories()

# Prepare dropdown lists with dynamic pipeline options + fallback
if categories and categories.get("brands"):
    brands_list = categories["brands"] + ["Other / Enter Custom"]
    models_list = categories["models"] + ["Other / Enter Custom"]
    cities_list = categories["cities"] + ["Other / Enter Custom"]
else:
    # Fallback lists if backend hasn't loaded categories yet
    brands_list = ["Hero", "Honda", "TVS", "Bajaj", "Royal Enfield", "Yamaha", "Suzuki", "KTM", "Other / Enter Custom"]
    models_list = ["Classic 350", "Splendor Plus", "Pulsar 150", "Apache RTR 160", "Other / Enter Custom"]
    cities_list = ["Ahmedabad", "Bangalore", "Delhi", "Mumbai", "Pune", "Other / Enter Custom"]

with st.form("bike_form"):
    st.subheader("Enter Vehicle Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Dynamic Brand Input
        brand_choice = st.selectbox("Brand", brands_list)
        if brand_choice == "Other / Enter Custom":
            brand = st.text_input("Enter Custom Brand Name", value="Hero").strip().title()
        else:
            brand = brand_choice

        # Dynamic Model Input
        model_choice = st.selectbox("Model Name", models_list)
        if model_choice == "Other / Enter Custom":
            model = st.text_input("Enter Custom Model Name", value="Classic 350").strip().title()
        else:
            model = model_choice

        # Dynamic City Input
        city_choice = st.selectbox("City", cities_list)
        if city_choice == "Other / Enter Custom":
            city = st.text_input("Enter Custom City", value="Ahmedabad").strip().title()
        else:
            city = city_choice

        is_premium = st.selectbox("Is Premium Brand?", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

    with col2:
        year = st.number_input("Manufacture Year", min_value=1990, max_value=2026, value=2020)
        age = st.number_input("Age of Bike (Years)", min_value=0, max_value=35, value=6)
        km_driven = st.number_input("Total KM Driven", min_value=0, value=25000, step=1000)

    km_per_year = km_driven / age if age > 0 else km_driven
    submit_btn = st.form_submit_button("Estimate Fair Price", use_container_width=True)

if submit_btn:
    payload = {
        "Brand": brand,
        "Model": model,
        "City": city,
        "Year": int(year),
        "Age": int(age),
        "KM_Driven": float(km_driven),
        "KM_driven_per_year": float(km_per_year),
        "Is_Premium_Brand": int(is_premium)
    }

    with st.spinner("Connecting to FastAPI backend..."):
        try:
            response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("Valuation Complete!")
                
                # Primary Fair Market Price Display
                st.metric(
                    label="Estimated Fair Market Value",
                    value=f"₹{result['exact_price']:,.0f}"
                )
                
                # Valuation Negotiation Range
                st.info(f"**Expected Range:** ₹{result['range_low']:,.0f} – ₹{result['range_high']:,.0f}")
                
                # Condition Context
                with st.expander("💡 How to use this range for negotiation"):
                    st.write(f"- **Lower Bound (₹{result['range_low']:,.0f}):** Fair target for bikes with body scratches, worn tires, or urgent sale requirements.")
                    st.write(f"- **Fair Price (₹{result['exact_price']:,.0f}):** Standard benchmark price for average condition with regular service records.")
                    st.write(f"- **Upper Bound (₹{result['range_high']:,.0f}):** Justified for mint condition vehicles, new battery/tires, or active warranty.")
            else:
                st.error(f"Backend API Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to FastAPI server. Ensure main.py is running on port 8000!")