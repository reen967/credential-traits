import streamlit as st
import pandas as pd

# Load data
df = pd.read_csv("Book3.csv")

st.title("University Trait Explorer for Employers")

st.markdown("Select your trait priorities and whether you'd like to consider context:")

# Context toggles
use_contextual_friction = st.checkbox("Apply Contextual Friction Score", value=True)
use_contextual_cognitive = st.checkbox("Use Contextual Cognitive Readiness", value=True)
use_contextual_communication = st.checkbox("Use Contextual Communication", value=True)

# Trait weight inputs
traits = [
    "Conscientiousness",
    "Resilience/Grit",
    "Adaptability",
    "Self-Direction",
    "Growth Mindset",
    "Cognitive Readiness (Contextual)" if use_contextual_cognitive else "Cognitive Readiness (Raw)",
    "Communication (Contextual)" if use_contextual_communication else "Communication (Raw)",
    "Written Component",
    "Navigational Component (Behavior)",
    "Quantitative Reasoning"
]

trait_weights = {}
st.sidebar.header("Trait Weightings (0 to 1)")

for trait in traits:
    weight = st.sidebar.slider(trait, 0.0, 1.0, 0.1)
    trait_weights[trait] = weight

# Normalize weights
total_weight = sum(trait_weights.values())
if total_weight == 0:
    st.warning("Please assign at least one non-zero weight.")
    st.stop()

normalized_weights = {k: v / total_weight for k, v in trait_weights.items()}

# Filter valid rows
valid_df = df.copy()
for trait in traits:
    valid_df = valid_df[valid_df[trait].apply(lambda x: isinstance(x, (int, float)))]

# Compute composite score
valid_df["Composite Score"] = valid_df.apply(
    lambda row: sum(row[trait] * normalized_weights[trait] for trait in traits), axis=1
)

# Apply Contextual Friction if selected
if use_contextual_friction:
    valid_df = valid_df[valid_df["Contextual Friction Score"].apply(lambda x: isinstance(x, (int, float)))]
    valid_df["Final Score"] = valid_df["Composite Score"] * (100 - valid_df["Contextual Friction Score"]) / 100
else:
    valid_df["Final Score"] = valid_df["Composite Score"]

# Show results
results = valid_df.sort_values("Final Score", ascending=False)[
    ["Institution Name", "State abbreviation (HD2023)", "Grand total (All students  Undergraduate total) EF2023", "Final Score"] + traits + (["Contextual Friction Score"] if use_contextual_friction else [])
]

st.dataframe(results.reset_index(drop=True), use_container_width=True)

