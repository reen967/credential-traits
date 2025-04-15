import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    return df

df = load_data()

# Title
st.title("Institution Trait Filter Tool")

# Trait inputs
st.markdown("### Select Traits and Assign Weights")
trait_columns = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

weights = {}
for trait in trait_columns:
    weight = st.slider(f"{trait} Weight", min_value=0.0, max_value=1.0, step=0.1, value=0.0)
    if weight > 0:
        weights[trait] = weight

# Normalize weights
if weights:
    total_weight = sum(weights.values())
    weights = {trait: w / total_weight for trait, w in weights.items()}

# Column toggles
st.markdown("### Display Options")
col1, col2, col3 = st.columns(3)
with col1:
    show_score = st.checkbox("Show Score", value=False)
with col2:
    show_notes = st.checkbox("Show Missing Traits", value=False)
with col3:
    show_state = st.checkbox("Show State", value=False)

# State filter
selected_state = st.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))
if selected_state != "All":
    df = df[df['State abbreviation (HD2023)'] == selected_state]

# Score institutions
def score_institutions(df, weights):
    scores = []
    notes = []
    for idx, row in df.iterrows():
        score = 0
        total_weight = 0
        missing_traits = []
        for trait, weight in weights.items():
            value = row.get(trait)
            if isinstance(value, (int, float)):
                score += value * weight
                total_weight += weight
            else:
                missing_traits.append(trait)
        if total_weight > 0:
            final_score = round(score / total_weight, 1)
        else:
            final_score = None
        scores.append(final_score)
        notes.append(", ".join(missing_traits) if missing_traits else "")
    df["Score"] = scores
    df["Missing Traits"] = notes
    return df

if weights:
    df_scored = score_institutions(df.copy(), weights)
    df_scored = df_scored[df_scored["Score"].notna()]

    # Determine if we need to split by control
    public_df = df_scored[df_scored["Control of institution (HD2023)"] == 1]
    private_df = df_scored[df_scored["Control of institution (HD2023)"].isin([2, 3])]
    show_split = len(public_df) >= 7 and len(private_df) >= 7

    columns = ["Institution Name"]
    if show_score:
        columns.append("Score")
    if show_notes:
        columns.append("Missing Traits")
    if show_state:
        columns.append("State abbreviation (HD2023)")

    if show_split:
        st.subheader("Public Institutions")
        public_display = public_df[columns].sort_values(by="Score", ascending=False, na_position='last')
        st.dataframe(public_display)

        st.subheader("Private Institutions")
        private_display = private_df[columns].sort_values(by="Score", ascending=False, na_position='last')
        st.dataframe(private_display)

    else:
        st.subheader("Combined Results")
        combined_display = df_scored[columns].sort_values(by="Score", ascending=False, na_position='last')
        st.dataframe(combined_display)

else:
    st.info("Please select at least one trait with a weight greater than 0 to begin filtering.")

