import streamlit as st
import pandas as pd

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("data/credential_traits.csv")
    df.replace("Unavailable", pd.NA, inplace=True)
    return df

df = load_data()

# Trait columns
trait_columns = [
    "Conscientiousness", "Resilience/Grit", "Adaptability", "Self Direction",
    "Growth Mindset", "Cognitive Readiness", "Communication", "Quantitative Reasoning"
]

# Sidebar: Trait weights
st.sidebar.header("Select Trait Weights")
weights = {trait: st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1) for trait in trait_columns}

include_partial = st.sidebar.checkbox("Include partial results", value=True)

# Optional navigation link
st.sidebar.markdown("[Go to Explanation Page](#)", unsafe_allow_html=True)

# Main Page: Display Options
st.title("Credential Traits by Institution")
st.markdown("Use the sidebar to adjust trait weightings and filter results.")

state_filter = st.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))
show_state = st.checkbox("Show State", value=True)
show_notes = st.checkbox("Show Notes (tooltips)", value=True)

# Scoring function
def score_institutions(df, weights, include_partial=True):
    results = []
    for _, row in df.iterrows():
        total_score = 0.0
        total_weight = 0.0
        missing_traits = []

        for trait, weight in weights.items():
            if weight == 0:
                continue
            try:
                val = float(row[trait])
                total_score += val * weight
                total_weight += weight
            except:
                missing_traits.append(trait)

        if total_weight == 0 or (missing_traits and not include_partial):
            continue

        final_score = round(total_score / total_weight, 1)

        notes = "All traits used" if not missing_traits else f"Missing: {', '.join(missing_traits)}"
        results.append({
            "Institution Name": row["Institution Name"],
            "State": row["State abbreviation (HD2023)"],
            "Score (out of 100)": final_score,
            "Notes": notes
        })

    return pd.DataFrame(results)

# Compute and filter
scored_df = score_institutions(df, weights, include_partial)
if state_filter != "All":
    scored_df = scored_df[scored_df["State"] == state_filter]

scored_df = scored_df.sort_values(by="Score (out of 100)", ascending=False).reset_index(drop=True)

# Display table
if not scored_df.empty:
    if show_notes:
        # Use HTML tooltip for notes
        scored_df["Institution Name"] = scored_df.apply(
            lambda row: f'<span title="{row["Notes"]}">{row["Institution Name"]}</span>', axis=1
        )
        scored_df.drop(columns=["Notes"], inplace=True)

    display_columns = ["Institution Name", "Score (out of 100)"]
    if show_state:
        display_columns.append("State")

    st.markdown("### Ranked Institutions")
    st.write("Hover over names to see missing traits if applicable." if show_notes else "")
    st.write(
        scored_df[display_columns].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
else:
    st.warning("No results to display. Try adjusting trait weights or filters.")

# Download option
st.download_button(
    label="Download Results as CSV",
    data=scored_df.to_csv(index=False).encode('utf-8'),
    file_name='trait_scores.csv',
    mime='text/csv'
)






