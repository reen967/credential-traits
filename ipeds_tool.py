import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/credential_traits.csv")

df = load_data()

# Trait names and weighting input
traits = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

st.sidebar.header("Select Trait Weights")
weights = {trait: st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1) for trait in traits}
include_partial = st.sidebar.checkbox("Include partial results", value=True)
selected_state = st.sidebar.selectbox("Filter by State", ["All"] + sorted(df["State abbreviation (HD2023)"].dropna().unique()))

# Apply state filter
if selected_state != "All":
    df = df[df["State abbreviation (HD2023)"] == selected_state]

# Scoring logic
def score_institutions(df, weights):
    results = []
    for _, row in df.iterrows():
        score = 0
        total_weight = 0
        missing = []
        for trait, weight in weights.items():
            if weight == 0:
                continue
            try:
                value = float(row[trait])
                score += value * weight
                total_weight += weight
            except:
                missing.append(trait)
        if total_weight > 0 and (include_partial or not missing):
            results.append({
                "Institution Name": row["Institution Name"],
                "Control": row["Control of institution (HD2023)"],
                "State": row["State abbreviation (HD2023)"],
                "Match %": round(score / total_weight, 1),
                "Missing": missing
            })
    return pd.DataFrame(results)

scored_df = score_institutions(df, weights)
scored_df = scored_df.sort_values(by="Match %", ascending=False)

# Auto-split if needed
control_counts = scored_df["Control"].value_counts()
split = any(control_counts[c] >= 7 for c in [1, 2, 3])

# UI display
def render_table(df, label):
    st.subheader(label)
    for _, row in df.iterrows():
        highlight = " 🔍" if row["Missing"] else ""
        with st.expander(f"{row['Institution Name']} ({row['Match %']}%){highlight}"):
            st.markdown(f"**State:** {row['State']}")
            if row["Missing"]:
                st.markdown(f"*Partial data — missing:* {', '.join(row['Missing'])}")

if split:
    if control_counts.get(1, 0) >= 7:
        render_table(scored_df[scored_df["Control"] == 1], "Public Institutions")
    if control_counts.get(2, 0) + control_counts.get(3, 0) >= 7:
        render_table(scored_df[scored_df["Control"].isin([2, 3])], "Private Institutions")
else:
    render_table(scored_df, "All Institutions")



