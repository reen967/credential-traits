import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def load_data():
    pd.read_csv("data/credential_traits.csv")

    return df

def filter_by_state(df, state):
    if state != "All":
        return df[df['State abbreviation (HD2023)'] == state]
    return df

def score_institutions(df, weights):
    score = sum(df[trait] * weight for trait, weight in weights.items())
    df = df.copy()
    df["Score"] = score
    df = df.dropna(subset=["Score"])
    return df.sort_values("Score", ascending=False)

def plot_radar(row, traits):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[row[trait] for trait in traits],
        theta=traits,
        fill='toself',
        name=row['Institution Name']
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False
    )
    return fig

st.title("Credential Traits Explorer")

with st.sidebar:
    st.header("Select Trait Weights")
    traits = [
        "Conscientiousness", "Resilience/Grit", "Adaptability",
        "Self Direction", "Growth Mindset", "Cognitive Readiness",
        "Communication", "Quantitative Reasoning"
    ]
    weights = {trait: st.slider(trait, 0.0, 1.0, 0.0, 0.1) for trait in traits}
    total_weight = sum(weights.values())
    if total_weight == 0:
        st.warning("Please assign weights to at least one trait.")
    else:
        weights = {trait: w / total_weight for trait, w in weights.items() if w > 0}

    state_filter = st.selectbox("Filter by State", ["All"] + sorted(load_data()['State abbreviation (HD2023)'].dropna().unique()))
    view_option = st.radio("View Options", ["Combined", "Split by Public/Private"])

st.markdown("### Trait Descriptions")
with st.expander("How are these traits calculated?"):
    st.markdown("""
    **Conscientiousness**: Based on adjusted graduation timelines, separating Pell and non-Pell pathways.
    
    **Resilience/Grit**: Captures longer graduation timelines, age diversity, GI Bill utilization, and transfer-in enrollment.

    **Adaptability**: Measures participation in online/hybrid learning, transfer paths, GI Bill, and older learners.

    **Self Direction**: Includes older learners, hybrid participation, and late graduations.

    **Growth Mindset**: Includes hybrid learning and improved graduation rates over time.

    **Cognitive Readiness**: Based on standardized test performance, adjusted for Pell population.

    **Communication**: Includes SAT English score, timely graduation, and international student enrollment (adjusted by institution type).

    **Quantitative Reasoning**: Based on SAT Math scores and ACT Math where available.
    """)

if total_weight > 0:
    df = load_data()
    df = filter_by_state(df, state_filter)
    df = df.dropna(subset=weights.keys())
    df_scored = score_institutions(df, weights)

    pub_df = df_scored[df_scored["Control of institution (HD2023)"] == 1]
    priv_df = df_scored[df_scored["Control of institution (HD2023)"].isin([2, 3])]

    if view_option == "Split by Public/Private" and len(pub_df) >= 7 and len(priv_df) >= 7:
        st.subheader("Top Public Institutions")
        st.dataframe(pub_df[["Institution Name", "State abbreviation (HD2023)", "Score"]].reset_index(drop=True))

        st.subheader("Top Private Institutions")
        st.dataframe(priv_df[["Institution Name", "State abbreviation (HD2023)", "Score"]].reset_index(drop=True))
    else:
        st.subheader("Top Institutions")
        st.dataframe(df_scored[["Institution Name", "State abbreviation (HD2023)", "Score"]].reset_index(drop=True))

    selected_school = st.selectbox("Select an institution to view trait radar", df_scored["Institution Name"])
    selected_row = df_scored[df_scored["Institution Name"] == selected_school].iloc[0]
    radar_fig = plot_radar(selected_row, list(weights.keys()))
    st.plotly_chart(radar_fig)

    csv = df_scored.to_csv(index=False)
    st.download_button("Download Results", csv, "institution_traits.csv", "text/csv")


