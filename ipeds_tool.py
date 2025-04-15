import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    df.replace("Unavailable", pd.NA, inplace=True)  # Clean non-numeric entries
    return df

df = load_data()

# Trait columns
trait_columns = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

# Sidebar UI
st.sidebar.header("Select Trait Weights")
weights = {}
for trait in trait_columns:
    weights[trait] = st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1)

# Filter by State
state_filter = st.sidebar.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))
if state_filter != "All":
    df = df[df['State abbreviation (HD2023)'] == state_filter]

# Function to calculate score and missing traits
def score_institutions(df, weights):
    results = []
    for _, row in df.iterrows():
        available_traits = []
        missing_traits = []
        score = 0.0
        total_weight = 0.0

        for trait, weight in weights.items():
            val = row.get(trait)
            if pd.notna(val):
                available_traits.append(trait)
                score += float(val) * weight
                total_weight += weight
            else:
                if weight > 0:
                    missing_traits.append(trait)

        if total_weight > 0:
            normalized_score = round(score / total_weight, 1)
        else:
            normalized_score = "Unavailable"

        notes = "Partial data" if missing_traits else "All traits used"
        if missing_traits:
            notes += f" (Missing: {', '.join(missing_traits)})"

        results.append({
            "Institution Name": row["Institution Name"],
            "State": row["State abbreviation (HD2023)"],
            "Control": row["Control of institution (HD2023)"],
            "Score": normalized_score,
            "Notes": notes
        })
    return pd.DataFrame(results)

# Score and sort
scored_df = score_institutions(df, weights)
scored_df = scored_df[scored_df["Score"] != "Unavailable"]
scored_df = scored_df.sort_values(by="Score", ascending=False)

# Split by control
public = scored_df[scored_df["Control"] == 1]
private = scored_df[scored_df["Control"].isin([2, 3])]

# Display results
st.title("Credential Traits by Institution")
st.markdown("Use the sidebar to adjust trait weightings and filter results.")

if len(public) >= 7:
    st.subheader("Top Public Institutions")
    st.dataframe(public[["Institution Name", "State", "Score", "Notes"]])

if len(private) >= 7:
    st.subheader("Top Private Institutions")
    st.dataframe(private[["Institution Name", "State", "Score", "Notes"]])

if len(public) < 7 and len(private) < 7:
    st.subheader("Top Institutions")
    st.dataframe(scored_df[["Institution Name", "State", "Score", "Notes"]])

# Optional: Download button
st.download_button(
    label="Download Results as CSV",
    data=scored_df.to_csv(index=False).encode('utf-8'),
    file_name='trait_scores.csv',
    mime='text/csv'
)


