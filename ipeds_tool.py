import streamlit as st
import pandas as pd

# Load your cleaned dataset
@st.cache_data
def load_data():
    df = pd.read_csv("Book3.csv")
    return df

df = load_data()

# Define the traits available
traits = [
    "Contextual Friction Score",
    "Conscientiousness",
    "Resilience/Grit",
    "Adaptability",
    "Self-Direction",
    "Cognitive Readiness (Raw)",
    "Growth Mindset",
    "Written Component",
    "Navigational Component (Behavior)",
    "Communication (Raw)",
    "Cognitive Readiness (Contextual)",
    "Communication (Contextual)",
    "Quantitative Reasoning"
]

# Clean the data: convert all traits to numeric, coercing errors to NaN
df_clean = df.copy()
for trait in traits:
    if trait in df_clean.columns:
        df_clean[trait] = pd.to_numeric(df_clean[trait], errors="coerce")

# Sidebar: trait weight sliders and context inclusion toggles
st.sidebar.header("Trait Preferences")

use_contextual_friction = st.sidebar.checkbox("Apply Contextual Friction", value=True)
use_contextual_cognitive = st.sidebar.checkbox("Use Contextual Cognitive Readiness", value=True)
use_contextual_communication = st.sidebar.checkbox("Use Contextual Communication", value=True)

selected_traits = {}

for trait in traits:
    if trait.startswith("Cognitive Readiness"):
        if (use_contextual_cognitive and "Contextual" not in trait) or (not use_contextual_cognitive and "Contextual" in trait):
            continue
    if trait.startswith("Communication"):
        if (use_contextual_communication and "Contextual" not in trait) or (not use_contextual_communication and "Contextual" in trait):
            continue
    if trait == "Contextual Friction Score" and not use_contextual_friction:
        continue

    include = st.sidebar.checkbox(f"Include {trait}?", value=False)
    if include:
        weight = st.sidebar.slider(f"Weight for {trait}", 0.0, 1.0, 0.1, 0.05)
        selected_traits[trait] = weight

if not selected_traits:
    st.warning("Please select at least one trait to score institutions.")
    st.stop()

# Normalize weights
total_weight = sum(selected_traits.values())
selected_traits = {k: v / total_weight for k, v in selected_traits.items()}

# Calculate match scores
scores = []

for idx, row in df_clean.iterrows():
    if all(pd.notna(row[trait]) for trait in selected_traits):
        score = sum(row[trait] * weight for trait, weight in selected_traits.items())
        scores.append(score)
    else:
        scores.append(None)

# Add match scores to DataFrame
df_clean["Match Score"] = scores

# Filter valid scores
df_results = df_clean.dropna(subset=["Match Score"]).copy()
df_results = df_results.sort_values("Match Score", ascending=False)

# Display results
st.title("Credential Trait Matcher")
st.markdown("### Results Based on Your Preferences")
st.dataframe(df_results[[
    "Institution Name", 
    "State abbreviation (HD2023)", 
    "Grand total (All students  Undergraduate total) EF2023",
    "Match Score"
] + list(selected_traits.keys())])
