import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np

st.set_page_config(layout="wide")
st.title("College Ranking Builder (IPEDS)")

DEFAULT_DATA_PATH = "data/ipeds_data1.csv"

uploaded_file = st.file_uploader("Upload your IPEDS CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv(DEFAULT_DATA_PATH)

st.markdown("### Step 1: Select and Weight Ranking Variables")

numeric_cols = df.select_dtypes(include='number').columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

selected_vars = st.multiselect("Choose numeric variables to include in the ranking:", options=numeric_cols)

score_config = {}
for var in selected_vars:
    col1, col2 = st.columns([2, 1])
    with col1:
        direction = st.radio(f"{var} — Higher or Lower is Better?", ["High is better", "Low is better"], key=f"dir_{var}")
    with col2:
        weight = st.slider("Weight", 0.0, 1.0, 0.1, 0.05, key=f"weight_{var}")
    score_config[var] = {"weight": weight, "direction": "high" if "High" in direction else "low"}

st.markdown("### Step 2: (Optional) Filter Institutions")

filtered_df = df.copy()

for col in selected_vars:
    col_min, col_max = int(df[col].min(skipna=True)), int(df[col].max(skipna=True))
    if col_min != col_max:
        selected_range = st.slider(f"{col} range:", col_min, col_max, (col_min, col_max), key=f"filter_{col}")
        filtered_df = filtered_df[filtered_df[col].between(selected_range[0], selected_range[1])]

st.markdown("### Step 3: View Rankings")

if score_config:
    norm_df = pd.DataFrame(index=filtered_df.index)
    for var, config in score_config.items():
        values = filtered_df[var].fillna(0)
        scaled = MinMaxScaler().fit_transform(values.values.reshape(-1, 1)).flatten()
        if config["direction"] == "low":
            scaled = 1 - scaled
        norm_df[var] = scaled * config["weight"]

    filtered_df['Composite Score'] = norm_df.sum(axis=1)
    ranked_df = filtered_df.sort_values("Composite Score", ascending=False)

    display_cols = ['institution name', 'Composite Score'] + selected_vars
    st.dataframe(ranked_df[display_cols].reset_index(drop=True))

    st.download_button(
        label="📥 Download Results",
        data=ranked_df[display_cols].to_csv(index=False).encode('utf-8'),
        file_name='ranked_ipeds_results.csv',
        mime='text/csv'
    )
