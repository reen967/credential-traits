import streamlit as st
import pandas as pd

# Load your data (replace with actual file path or upload method)
@st.cache_data
def load_data():
    return pd.read_csv("credential_traits.csv")  # Make sure this CSV has the columns listed below

df = load_data()

# Define trait columns
trait_columns = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

st.title("College Trait Explorer")

# Trait selection and weightings
st.header("Step 1: Choose Traits and Weightings")
selected_traits = st.multiselect("Select traits important to you", trait_columns)

weights = {
    trait: st.slider(f"Weight for {trait}", 0.0, 1.0, 0.2, 0.05)
    for trait in selected_traits
}

# State filter
st.header("Step 2: Filter by State")
states = sorted(df["State abbreviation (HD2023)"].dropna().unique())
selected_states = st.multiselect("Select states", states, default=states)

# Apply state filter
filtered_df = df[df["State abbreviation (HD2023)"].isin(selected_states)].copy()

# Drop rows with any non-numeric or missing data in selected traits
for trait in selected_traits:
    filtered_df = filtered_df[pd.to_numeric(filtered_df[trait], errors='coerce').notnull()]

# Compute overall weighted score
filtered_df["Score"] = filtered_df[selected_traits].apply(
    lambda row: sum(row[trait] * weights[trait] for trait in selected_traits), axis=1
)

# Split by institution control type
public_df = filtered_df[filtered_df["Control of institution (HD2023)"] == 1]
private_df = filtered_df[filtered_df["Control of institution (HD2023)"].isin([2, 3])]

# Display public institutions if 7 or more
if len(public_df) >= 7:
    st.subheader("Public Institutions")
    st.dataframe(
        public_df.sort_values(by="Score", ascending=False)[
            ["Institution Name", "State abbreviation (HD2023)", "Score"] + selected_traits
        ]
    )

# Display private institutions if 7 or more
if len(private_df) >= 7:
    st.subheader("Private Institutions")
    st.dataframe(
        private_df.sort_values(by="Score", ascending=False)[
            ["Institution Name", "State abbreviation (HD2023)", "Score"] + selected_traits
        ]
    )

# If fewer than 7 in either category
if len(public_df) < 7 and len(private_df) < 7:
    st.info("Not enough institutions in each category to display separate lists.")

