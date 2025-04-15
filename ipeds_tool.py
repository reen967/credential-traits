import streamlit as st
import pandas as pd

# Load and clean data
@st.cache_data

def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    df.replace("Unavailable", pd.NA, inplace=True)
    return df

df = load_data()

trait_columns = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

st.title("Credential Traits Explorer")
st.markdown("Use the sidebar to select traits. Scores reflect estimated percentage of graduates demonstrating selected traits.")

# Sidebar: Trait Weights
st.sidebar.header("Select Trait Weights")
weights = {}
for trait in trait_columns:
    weights[trait] = st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1)

# Sidebar: Additional Options
include_partial = st.sidebar.checkbox("Include partial results", value=True)
states = ["All"] + sorted(df['State'].dropna().unique())
state_filter = st.selectbox("Filter by State", states)

# Display options
st.subheader("Display Options")
show_score = st.checkbox("Show Score", value=False)
show_notes = st.checkbox("Show Notes", value=False)
show_state = st.checkbox("Show State", value=False)

# Apply filters
if state_filter != "All":
    df = df[df['State'] == state_filter]

# Score calculation
def score_institutions(df, weights, include_partial):
    results = []
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
                if weight > 0:
                    missing.append(trait)

        if total_weight == 0 or (missing and not include_partial):
            continue

        normalized_score = round(total_score / total_weight, 1)
        notes = "Partial data" if missing else "All traits used"
        if missing:
            notes += f" (Missing: {', '.join(missing)})"

        results.append({
            "Institution Name": row["Institution Name"],
            "State": row["State"],
            "Score (out of 100)": normalized_score,
            "Notes": notes
        })
    return pd.DataFrame(results)

# Score and sort
if any(weight > 0 for weight in weights.values()):
    scored_df = score_institutions(df, weights, include_partial)
    scored_df = scored_df.sort_values(by="Score (out of 100)", ascending=False).reset_index(drop=True)

    # Column visibility toggles
    selected_cols = ["Institution Name"]
    if show_state:
        selected_cols.append("State")
    if show_score:
        selected_cols.append("Score (out of 100)")
    if show_notes:
        selected_cols.append("Notes")

    # Tooltips
    st.dataframe(
        scored_df[selected_cols],
        column_config={
            "Institution Name": st.column_config.TextColumn("Institution Name"),
            "Score (out of 100)": st.column_config.NumberColumn("Score (out of 100)", help="Weighted average score out of 100."),
            "Notes": st.column_config.TextColumn("Notes", help="Indicates missing traits used in the calculation."),
            "State": st.column_config.TextColumn("State")
        },
        use_container_width=True
    )

    # Download option
    st.download_button(
        label="Download Results as CSV",
        data=scored_df.to_csv(index=False).encode('utf-8'),
        file_name='trait_scores.csv',
        mime='text/csv'
    )
else:
    st.warning("Please assign weight to at least one trait in the sidebar.")
