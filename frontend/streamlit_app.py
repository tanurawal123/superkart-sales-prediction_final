import os
import requests
import pandas as pd
import streamlit as st

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:7860")
REFERENCE_YEAR = 2026  # must match the backend's REFERENCE_YEAR

st.set_page_config(page_title="SuperKart Sales Predictor", layout="centered")
st.title("SuperKart — Product Store Sales Predictor")

tab1, tab2 = st.tabs(["Single Prediction", "Batch Prediction"])

with tab1:
    st.subheader("Enter product & store details")
    col1, col2 = st.columns(2)
    with col1:
        product_id = st.text_input("Product Id", value="FDA15")
        product_weight = st.number_input("Product Weight (kg)", min_value=0.0, value=12.66, step=0.01)
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input("Product Allocated Area", min_value=0.0, max_value=1.0, value=0.03, step=0.01)
        product_mrp = st.number_input("Product MRP", min_value=0.0, value=117.08, step=0.01)
    with col2:
        product_type_category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
        store_establishment_year = st.number_input("Store Establishment Year", min_value=1980, max_value=REFERENCE_YEAR, value=2010, step=1)
        store_size = st.selectbox("Store Size", ["Small", "Medium", "High"])
        store_location_city_type = st.selectbox("Store Location City Type", ["Tier 1", "Tier 2", "Tier 3"])
        store_type = st.selectbox("Store Type", ["Supermarket Type1", "Supermarket Type2", "Departmental Store", "Food Mart"])

    if st.button("Predict Sales"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id[:2].upper(),
            "Store_Age_Years": REFERENCE_YEAR - store_establishment_year,
            "Product_Type_Category": product_type_category,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=15)
            if response.status_code == 200:
                st.success(f"Prediction: {response.json()}")
            else:
                st.error(response.text)
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach backend API: {e}")

with tab2:
    st.subheader("Upload a CSV for batch predictions")
    st.caption(
        "The CSV must contain: Product_Weight, Product_Sugar_Content, Product_Allocated_Area, "
        "Product_MRP, Store_Size, Store_Location_City_Type, Store_Type, Product_Id_char, "
        "Store_Age_Years, Product_Type_Category"
    )
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None and st.button("Run Batch Prediction"):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
            response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=60)
            if response.status_code == 200:
                pred_df = pd.DataFrame(list(response.json().items()), columns=["Row_Index", "Predicted_Sales"])
                st.dataframe(pred_df)
            else:
                st.error(response.text)
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach backend API: {e}")
