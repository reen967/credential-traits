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

# Navigation Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Trait Explorer", "Explanations"])

if page == "Explanations":
    st.title("Trait Definitions and Methodology")
    st.markdown("""
    - **Conscientiousness**: Based on graduation rates and adjusted by Pell/Non-Pell status.
    - **Resilience/Grit**: Emphasizes extended completion timelines and nontraditional routes.
    - **Adaptability**: Reflects students who adapt to new environments and formats.
    - **Self Direction**: Indicates high-agency behaviors like hybrid course selection.
    - **Growth Mindset**: Measures trajectory of improvement over time and learning flexibility.
    - **Cognitive Readiness**: SAT/ACT scores adjusted for Pell percentage.
    - **Communication**: Combines English test scores, graduation timelines, and international presence.
    - **Quantitative Reasoning**: Based on math-related test scores, adjusted contextually.
    """)
else:
    st.title("Credential Traits by Institution")

    # Trait weight sliders
    st.sidebar.header("Select Trait Weights")
    weights = {}
    for trait in trait_columns:
        weights[trait] = st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1)

    # Filter and display settings
    include_partial = st.checkbox("Include partial results", value=True)
    state_filter = st.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))

    if state_filter != "All":
        df = df[df['State abbreviation (HD2023)'] == state_filter]

    # Score function
    def score_institutions(df, weights, include_partial):
        results = []
        for _, row in df.iterrows():
            score = 0.0
            total_weight = 0.0
            missing_traits = []
            for trait, weight in weights.items():
                val = row.get(trait)
                if pd.notna(val):
                    score += float(val) * weight
                    total_weight += weight
                else:
                    if weight > 0:
                        missing_traits.append(trait)

            if total_weight == 0 or (missing_traits and not include_partial):
                continue

            normalized_score = round((score / total_weight) * 100, 1)
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

    scored_df = score_institutions(df, weights, include_partial)
    scored_df = scored_df.sort_values(by="Score", ascending=False).reset_index(drop=True)

    top10 = scored_df.head(10)
    public_top10 = top10[top10["Control"] == 1]
    private_top10 = top10[top10["Control"].isin([2, 3])]

    # Tooltips via help columns
    show_state = st.checkbox("Show State", value=False)
    show_score = st.checkbox("Show Score", value=False)
    show_notes = st.checkbox("Show Notes", value=False)

    base_cols = ["Institution Name"]
    if show_state: base_cols.append("State")
    if show_score: base_cols.append("Score")
    if show_notes: base_cols.append("Notes")

    if len(public_top10) >= 7:
        st.subheader("Top Public Institutions")
        st.dataframe(scored_df[scored_df["Control"] == 1][base_cols].head(10))

    if len(private_top10) >= 7:
        st.subheader("Top Private Institutions")
        st.dataframe(scored_df[scored_df["Control"].isin([2, 3])][base_cols].head(10))

    if len(public_top10) < 7 and len(private_top10) < 7:
        st.subheader("Top Institutions")
        st.dataframe(scored_df[base_cols].head(10))

    st.download_button(
        label="Download Full Results as CSV",
        data=scored_df.to_csv(index=False).encode('utf-8'),
        file_name='trait_scores.csv',
        mime='text/csv'
    )




