import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    return df

df = load_data()

st.title("Institution Trait Finder")

# Filter by State
state_filter = st.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))
if state_filter != "All":
    df = df[df['State abbreviation (HD2023)'] == state_filter]

# Trait Weight Inputs
st.markdown("### Select Trait Weights")
traits = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

weights = {}
for trait in traits:
    weights[trait] = st.slider(trait, 0.0, 1.0, 0.0, 0.1)

# Normalize weights
total_weight = sum(weights.values())
if total_weight > 0:
    weights = {k: v / total_weight for k, v in weights.items()}
else:
    weights = {k: 0 for k in weights}

include_partial = st.toggle("Include partial results", value=True)

# Columns visibility toggle
show_score = st.checkbox("Show overall score", value=False)
show_notes = st.checkbox("Show notes on missing data", value=False)
show_state = st.checkbox("Show State", value=True)

# Scoring Logic
def score_institutions(df, weights, include_partial):
    results = []
    for _, row in df.iterrows():
        available_traits = {
            trait: float(row[trait]) if str(row[trait]).replace('.', '', 1).isdigit() else None
            for trait in weights
        }
        valid_traits = {k: v for k, v in available_traits.items() if v is not None}
        
        if not valid_traits and not include_partial:
            continue

        applied_weights = {k: weights[k] for k in valid_traits}
        total_trait_score = sum(valid_traits[k] * applied_weights[k] for k in valid_traits)
        total_weight_used = sum(applied_weights.values())

        score = round(total_trait_score / total_weight_used, 1) if total_weight_used else None
        missing = [k for k in weights if available_traits[k] is None and weights[k] > 0]

        results.append({
            "Institution Name": row["Institution Name"],
            "Control": row["Control of institution (HD2023)"],
            "State": row["State abbreviation (HD2023)"],
            "Score": score,
            "Missing Traits": ", ".join(missing) if missing else "",
            **({trait: available_traits[trait] for trait in traits} if include_partial else {})
        })

    return pd.DataFrame(results)

# Generate scored results
df_scored = score_institutions(df, weights, include_partial)

# Handle institution type split
if len(df_scored) >= 7:
    public_df = df_scored[df_scored['Control'] == 1]
    private_df = df_scored[df_scored['Control'].isin([2, 3])]

    if len(public_df) >= 7 and len(private_df) >= 7:
        st.subheader("Public Institutions")
        st.dataframe(
    public_df[
        [c for c in ["Institution Name"] +
         (["Score"] if show_score else []) +
         (["Missing Traits"] if show_notes else []) +
         (["State"] if show_state else [])
         if c in public_df.columns]
    ].sort_values(by="Score", ascending=False, na_position='last')
)


        st.subheader("Private Institutions")
        st.dataframe(private_df[[c for c in ["Institution Name"] + (["Score"] if show_score else []) + (["Missing Traits"] if show_notes else []) + (["State"] if show_state else [])] if c in private_df.columns]].sort_values(by="Score", ascending=False, na_position='last'))
    else:
        st.subheader("All Institutions")
        st.dataframe(df_scored[[c for c in ["Institution Name"] + (["Score"] if show_score else []) + (["Missing Traits"] if show_notes else []) + (["State"] if show_state else [])] if c in df_scored.columns]].sort_values(by="Score", ascending=False, na_position='last'))
else:
    st.subheader("All Institutions")
    st.dataframe(df_scored[[c for c in ["Institution Name"] + (["Score"] if show_score else []) + (["Missing Traits"] if show_notes else []) + (["State"] if show_state else [])] if c in df_scored.columns]].sort_values(by="Score", ascending=False, na_position='last'))



