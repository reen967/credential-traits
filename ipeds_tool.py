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

# Sidebar for navigation
page = st.sidebar.radio("Navigate", ["Main", "Explanations"])

if page == "Explanations":
    st.title("Trait Explanations")
    st.markdown("""
    - **Conscientiousness**: Based on timely graduation rates adjusted for context.
    - **Resilience/Grit**: Captures delayed graduation, older students, and veterans.
    - **Adaptability**: Involves hybrid/online learners, transfers, and nontraditional students.
    - **Self Direction**: Reflects older learners, hybrid learners, and late graduates.
    - **Growth Mindset**: Focuses on learners who re-engage and evolve over time.
    - **Cognitive Readiness**: Derived from test scores, adjusted for socioeconomic friction.
    - **Communication**: Based on English scores, timely graduation, and nonresident student mix.
    - **Quantitative Reasoning**: Based on math and composite test scores.
    """)
else:
    st.title("Credential Traits by Institution")
    st.markdown("Use the sidebar to adjust trait weightings and filter results.")

    # Trait weighting
    st.sidebar.header("Select Trait Weights")
    weights = {}
    for trait in trait_columns:
        weights[trait] = st.sidebar.slider(trait, 0.0, 1.0, 0.0, 0.1)

    include_partial = st.sidebar.checkbox("Include partial results", value=True)
    state_filter = st.selectbox("Filter by State", ["All"] + sorted(df['State abbreviation (HD2023)'].dropna().unique()))
    if state_filter != "All":
        df = df[df['State abbreviation (HD2023)'] == state_filter]

    # Function to calculate scores
    def score_institutions(df, weights):
        results = []
        for _, row in df.iterrows():
            total_score = 0
            total_weight = 0
            missing_traits = []

            for trait, weight in weights.items():
                try:
                    val = float(row[trait])
                    total_score += val * weight
                    total_weight += weight
                except:
                    if weight > 0:
                        missing_traits.append(trait)

            if total_weight == 0 or (missing_traits and not include_partial):
                continue

            final_score = round(total_score / total_weight, 1)
            notes = "Partial data" if missing_traits else "All traits used"
            if missing_traits:
                notes += f" (Missing: {', '.join(missing_traits)})"

            results.append({
                "Institution Name": row["Institution Name"],
                "State": row["State abbreviation (HD2023)"],
                "Score": final_score,
                "Notes": notes
            })

        return pd.DataFrame(results)

    # Only score if at least one trait has weight
    if sum(weights.values()) == 0:
        st.warning("Please select at least one trait to calculate scores.")
    else:
        scored_df = score_institutions(df, weights)
        if not scored_df.empty and "Score" in scored_df.columns:
            scored_df = scored_df.sort_values(by="Score", ascending=False).reset_index(drop=True)
            st.dataframe(scored_df[["Institution Name", "State", "Score", "Notes"]])
            st.download_button(
                label="Download Results as CSV",
                data=scored_df.to_csv(index=False).encode('utf-8'),
                file_name='trait_scores.csv',
                mime='text/csv'
            )
        else:
            st.info("No institutions to display with the selected filters.")





