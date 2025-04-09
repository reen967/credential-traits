import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(layout="wide")
st.title("IPEDS Trait-Based College Explorer")

DEFAULT_DATA_PATH = "data/ipeds_data.csv"

# Upload or use default data
uploaded_file = st.file_uploader("Upload your IPEDS CSV file", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using default IPEDS dataset.")
    df = pd.read_csv(DEFAULT_DATA_PATH)

# Show raw dataset preview
with st.expander("📄 Preview Data", expanded=False):
    st.dataframe(df.head(10))

# Step 1: Filter by any numeric variable
st.subheader("Step 1: Filter Institutions by Any Variable")

filtered_df = df.copy()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
filter_ranges = {}

for col in numeric_cols:
    col_min = int(df[col].min(skipna=True))
    col_max = int(df[col].max(skipna=True))

    if col_min != col_max:  # Skip constant columns
        filter_ranges[col] = st.slider(
            f"{col} filter range:",
            min_value=col_min,
            max_value=col_max,
            value=(col_min, col_max)
        )
        filtered_df = filtered_df[
            filtered_df[col].between(filter_ranges[col][0], filter_ranges[col][1])
        ]

# Step 2: Choose scoring variables and assign weights
st.subheader("Step 2: Select Variables and Assign Weights for Scoring")

selected_vars = st.multiselect(
    "Choose variables to include in composite score",
    options=numeric_cols
)

weights = {}
for var in selected_vars:
    weights[var] = st.slider(f"Weight for {var}", 0.0, 1.0, 0.25, 0.05)

# Step 3: Scoring
if selected_vars:
    st.subheader("Step 3: Score and Rank Institutions")

    scaler = MinMaxScaler()
    norm_df = pd.DataFrame(
        scaler.fit_transform(filtered_df[selected_vars].fillna(0)),
        columns=selected_vars
    )

    composite_score = sum(norm_df[var] * weights[var] for var in selected_vars)
    filtered_df['Composite Score'] = composite_score

    ranked = filtered_df.sort_values("Composite Score", ascending=False)

    display_cols = ['institution name'] if 'institution name' in df.columns else []
    st.dataframe(ranked[display_cols + ['Composite Score'] + selected_vars].reset_index(drop=True))

    st.download_button(
        label="Download Filtered Results as CSV",
        data=ranked.to_csv(index=False).encode('utf-8'),
        file_name='filtered_ipeds_results.csv',
        mime='text/csv'
    )

