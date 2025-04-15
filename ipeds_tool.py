import streamlit as st
import pandas as pd
import numpy as np

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    df.replace("Unavailable", pd.NA, inplace=True)
    return df

# Normalize each trait column to 0–100
def normalize_traits(df, traits):
    df = df.copy()
    for trait in traits:
        numeric_values = pd.to_numeric(df[trait], errors='coerce')
        min_val = numeric_values.min()
        max_val = numeric_values.max()
        # Apply min-max scaling only to valid numbers
        scaled = ((numeric_values - min_val) / (max_val - min_val)) * 100
        df[trait] = scaled.round(1)
        # Preserve original "Unavailable"
        df.loc[df[trait].isna(), trait] = pd.NA
    return df

# Score institutions
def score_institutions(df, weights, include_partial):
    results = []
    for _, row in df.iterrows():
        score = 0.0
        total_weight = 0.0
        missing = []

        for trait, weight in weights.items():
            try:
                val = float(row[trait])
                score += val * weight
                total_weight += weight
            except:
                if weight > 0:
                    missing.append(trait)

        if total_weight == 0 or (missing and not include_partial):
            continue

        final_score = round(score / total_weight, 1)
        note = "Partial data" if missing else "All traits used"
        if missing:
            note += f" (Missing: {', '.join(missing)})"

        results.append({
            "Institution Name": row["Institution Name"],
            "State": row["State abbreviation (HD2023)"],
            "Score (out of 100)": final_score,
            "Notes": note
        })

    return pd.DataFrame(results)

# Initialize app
st.title("Credential Traits Explorer")

# Load and normalize data
df = load_data()
trait_columns = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]
df = normalize_traits(df, trait_columns)

# Sidebar: trait weightings
st.sidebar.header("Trait Weightings")
weights = {}
for trait in trait_columns:
    weight = st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1)
    if weight > 0:
        weights[trait] = weight

# Sidebar: filters and navigation
include_partial = st.sidebar.checkbox("Include partial results", value=True)
state_filter = st.sidebar.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))
if state_filter != "All":
    df = df[df['State abbreviation (HD2023)'] == state_filter]

# Display options
st.subheader("Display Options")
show_state = st.checkbox("Show State", value=True)
show_notes = st.checkbox("Show Notes", value=True)

# If weights are selected, calculate and show results
if weights:
    scored_df = score_institutions(df, weights, include_partial)
    scored_df = scored_df.sort_values(by="Score (out of 100)", ascending=False).reset_index(drop=True)

    # Display
    st.subheader("Top Institutions")
    columns_to_show = ["Institution Name"]
    if show_state:
        columns_to_show.append("State")
    if show_notes:
        columns_to_show.append("Notes")
    columns_to_show.append("Score (out of 100)")
    st.dataframe(scored_df[columns_to_show])

    # Download
    st.download_button(
        label="Download Results as CSV",
        data=scored_df.to_csv(index=False).encode('utf-8'),
        file_name='scored_institutions.csv',
        mime='text/csv'
    )
else:
    st.warning("Please assign weight to at least one trait to generate results.")



