import streamlit as st
import pandas as pd

# Load your data
df = pd.read_csv("Book3.csv")
df.columns = df.columns.str.strip()  # Strip extra whitespace

# Let user select traits and weights
traits = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self-Direction",
    "Cognitive Readiness (Contextual)", "Growth Mindset", "Written Component",
    "Navigational Component (Behavior)", "Communication (Contextual)", "Quantitative Reasoning"
]

st.sidebar.title("Trait Weighting")
selected_traits = {}
for trait in traits:
    use_trait = st.sidebar.checkbox(f"Include {trait}?", value=False)
    if use_trait:
        weight = st.sidebar.slider(f"Weight for {trait}", 0.0, 1.0, 0.1, 0.05)
        selected_traits[trait] = weight

# Normalize weights to sum to 1 if needed
total_weight = sum(selected_traits.values())
if total_weight == 0:
    st.warning("Please select and assign weights to at least one trait.")
    st.stop()

# Filter valid rows and calculate score
valid_df = df.copy()
score_column = []

for index, row in valid_df.iterrows():
    score = 0
    valid = True
    for trait, weight in selected_traits.items():
        if trait in valid_df.columns and pd.notnull(row[trait]) and isinstance(row[trait], (int, float)):
            score += weight * row[trait]
        else:
            valid = False
            break
    score_column.append(score if valid else None)

valid_df["Match Score"] = score_column
valid_df = valid_df.dropna(subset=["Match Score"]).sort_values("Match Score", ascending=False)

# Show results
st.title("Top Matching Institutions")
st.dataframe(valid_df[["Institution Name", "State abbreviation (HD2023)", "Grand total (All students  Undergraduate total) EF2023", "Match Score"] + list(selected_traits.keys())])

