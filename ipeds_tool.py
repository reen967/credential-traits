import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

st.set_page_config(layout="wide")
st.title("IPEDS Custom Ranking Builder")

DEFAULT_DATA_PATH = "data/ipeds_data.csv"

uploaded_file = st.file_uploader("Upload your IPEDS CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using default IPEDS dataset.")
    df = pd.read_csv(DEFAULT_DATA_PATH)

st.subheader("Step 1: Define Your Ranking Criteria")

# Define your variables with metadata
VARIABLES = [
    {"label": "4-year Graduation rate", "col": "4-year Graduation rate", "direction": "high"},
    {"label": "6-year Graduation rate", "col": "6-year Graduation rate", "direction": "high"},
    {"label": "8-year Graduation rate", "col": "8-year Graduation rate - bachelor's degree within 200% of normal time", "direction": "high"},
    {"label": "SAT EBRW 75th percentile", "col": "SAT Evidence-Based Reading and Writing 75th percentile score", "direction": "high"},
    {"label": "SAT Math 75th percentile", "col": "SAT Math 75th percentile score", "direction": "high"},
    {"label": "ACT Composite 75th percentile", "col": "ACT Composite 75th percentile score", "direction": "high"},
    {"label": "Percent Pell Grant Recipients", "col": "Percent of undergraduate students awarded Federal Pell grants", "direction": "high"},
    {"label": "Average Net Price", "col": "Average net price-students awarded grant or scholarship aid, 2022-23", "direction": "low"},
    {"label": "Total Price (in-state, off campus)", "col": "Total price for in-state students living off campus (not with family)  2023-24", "direction": "low"},
    {"label": "Percent Admitted", "col": "Percent admitted - total", "direction": "low"},
    {"label": "Transfer-in %", "col": "Transfer-in Percentage", "direction": "high"},
    {"label": "25+ Enrollment %", "col": "25+ Percentage", "direction": "high"},
    {"label": "Part-time Undergraduate Enrollment", "col": "Part-time undergraduate enrollment", "direction": "high"},
    {"label": "Undergraduate Enrollment", "col": "Undergraduate enrollment", "direction": "high"},
    {"label": "SAT Aggregate", "col": "SAT Aggregate", "direction": "high"},
]

# Select variables to include in the score
selected_variables = st.multiselect("Select variables to include in your ranking:", options=[v["label"] for v in VARIABLES])

# Assign weight and direction for each selected variable
weight_config = {}
for var in VARIABLES:
    if var["label"] in selected_variables:
        st.markdown(f"**{var['label']}**")
        weight = st.slider(f"Weight for {var['label']}", 0.0, 1.0, 0.1, 0.05)
        direction = st.selectbox(f"Preferred direction for {var['label']}", ["high", "low"], index=0 if var["direction"] == "high" else 1)
        weight_config[var["col"]] = {"weight": weight, "direction": direction}

# Normalize, score, and rank
if weight_config:
    st.subheader("Ranked Institutions")
    filtered_df = df.copy()
    score_df = pd.DataFrame(index=filtered_df.index)

    for col, config in weight_config.items():
        if col in filtered_df.columns:
            values = filtered_df[col].fillna(0)
            scaled = MinMaxScaler().fit_transform(values.values.reshape(-1, 1)).flatten()
            if config["direction"] == "low":
                scaled = 1 - scaled
            score_df[col] = scaled * config["weight"]

    filtered_df['Composite Score'] = score_df.sum(axis=1)
    ranked_df = filtered_df.sort_values("Composite Score", ascending=False)

    display_cols = ['institution name', 'Composite Score'] + list(weight_config.keys())
    st.dataframe(ranked_df[display_cols].reset_index(drop=True))

    st.download_button(
        label="Download Ranked Results as CSV",
        data=ranked_df[display_cols].to_csv(index=False).encode('utf-8'),
        file_name='ranked_ipeds_results.csv',
        mime='text/csv'
    )

