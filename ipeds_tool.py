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

st.subheader("Step 1: Filter Institutions")

filtered_df = df.copy()
numeric_cols = df.select_dtypes(include='number').columns.tolist()
categorical_cols = df.select_dtypes(include='object').columns.tolist()

selected_vars = []  # Keep track of variables selected for filtering and scoring

# Numeric filters
st.markdown("### Numeric Filters")
for col in numeric_cols:
    col_min = int(df[col].min(skipna=True))
    col_max = int(df[col].max(skipna=True))

    if col_min != col_max:
        use_col = st.checkbox(f"Filter by {col} (numeric)")
        if use_col:
            selected_vars.append(col)
            range_vals = st.slider(f"{col} range:", col_min, col_max, (col_min, col_max))
            filtered_df = filtered_df[
                filtered_df[col].between(range_vals[0], range_vals[1])
            ]

# Categorical filters
st.markdown("### Categorical Filters")
categorical_filters = {}
for col in categorical_cols:
    unique_vals = df[col].dropna().unique().tolist()
    if 1 < len(unique_vals) < 30:  # avoid large cardinality text fields
        use_col = st.checkbox(f"Filter by {col} (category)")
        if use_col:
            selected_vars.append(col)
            selected_options = st.multiselect(f"Select values for {col}", options=unique_vals, default=unique_vals)
            categorical_filters[col] = selected_options
            filtered_df = filtered_df[filtered_df[col].isin(selected_options)]

st.subheader("Step 2: Assign Weights to Selected Variables")

weights = {}

# Assign weights only to selected filter variables
for var in selected_vars:
    weights[var] = st.slider(f"Weight for {var}", 0.0, 1.0, 0.2, 0.05)

# Normalize and score
if weights:
    st.subheader("Step 3: Score and Rank Institutions")

    # Numeric normalization
    norm_df = pd.DataFrame(index=filtered_df.index)
    for var in selected_vars:
        if var in numeric_cols:
            scaler = MinMaxScaler()
            norm_df[var] = scaler.fit_transform(filtered_df[[var]].fillna(0))
        elif var in categorical_filters:
            # For categorical: binary score of 1 if it matches one of the selected values
            norm_df[var] = filtered_df[var].isin(categorical_filters[var]).astype(int)

    # Composite score
    composite_score = sum(norm_df[var] * weights[var] for var in selected_vars)
    filtered_df['Composite Score'] = composite_score

    ranked = filtered_df.sort_values("Composite Score", ascending=False)

    display_cols = ['institution name'] if 'institution name' in df.columns else []
    st.write("### Ranked List of Institutions")
    st.dataframe(ranked[display_cols + ['Composite Score'] + selected_vars].reset_index(drop=True))

    st.download_button(
        label="Download Filtered Results as CSV",
        data=ranked.to_csv(index=False).encode('utf-8'),
        file_name='filtered_ipeds_results.csv',
        mime='text/csv'
    )
