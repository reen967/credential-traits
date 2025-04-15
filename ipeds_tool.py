import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    df.replace("Unavailable", pd.NA, inplace=True)
    return df

def score_institutions(df, weights, include_partial):
    rows = []
    for _, row in df.iterrows():
        total_score = 0
        total_weight = 0
        missing = []
        for trait, weight in weights.items():
            try:
                val = float(row[trait])
                total_score += val * weight
                total_weight += weight
            except:
                missing.append(trait)

        if total_weight == 0 or (missing and not include_partial):
            continue

        row_copy = row.copy()
        row_copy["Score"] = total_score / total_weight
        row_copy["Missing Traits"] = ", ".join(missing)
        rows.append(row_copy)

    return pd.DataFrame(rows)

df = load_data()

st.title("Credential Trait Explorer")

# Sidebar for trait selection
st.sidebar.header("Select Trait Weightings")
traits = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]
weights = {}
for trait in traits:
    weight = st.sidebar.slider(f"{trait}", 0.0, 1.0, 0.0, 0.05)
    if weight > 0:
        weights[trait] = weight

include_partial = st.sidebar.checkbox("Include partial results", value=True)

# Display options (Main page)
st.subheader("Display Options")
show_score = st.checkbox("Show Score", value=False)
show_state = st.checkbox("Show State", value=False)
show_notes = st.checkbox("Show Notes", value=False)

# Filter by state
state_filter = st.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))

if weights:
    df_scored = score_institutions(df, weights, include_partial)

    if state_filter != "All":
        df_scored = df_scored[df_scored["State abbreviation (HD2023)"] == state_filter]

    df_scored["Control Type"] = df_scored["Control of institution (HD2023)"].map({1: "Public", 2: "Private", 3: "Private"})

    # Select columns dynamically
    display_cols = ["Institution Name"]
    if show_score and "Score" in df_scored.columns:
        display_cols.append("Score")
    if show_notes and "Missing Traits" in df_scored.columns:
        display_cols.append("Missing Traits")
    if show_state and "State abbreviation (HD2023)" in df_scored.columns:
        display_cols.append("State abbreviation (HD2023)")

    public_df = df_scored[df_scored["Control Type"] == "Public"]
    private_df = df_scored[df_scored["Control Type"] == "Private"]

    if len(public_df) >= 7 and len(private_df) >= 7:
        st.markdown("### Public Institutions")
        st.dataframe(public_df[display_cols].sort_values(by="Score" if "Score" in display_cols else "Institution Name", ascending=False))

        st.markdown("### Private Institutions")
        st.dataframe(private_df[display_cols].sort_values(by="Score" if "Score" in display_cols else "Institution Name", ascending=False))
    else:
        st.markdown("### All Institutions")
        combined_display = df_scored[display_cols].sort_values(by="Score" if "Score" in display_cols else "Institution Name", ascending=False)
        st.dataframe(combined_display)
else:
    st.warning("Please assign weight to at least one trait in the sidebar to see results.")



