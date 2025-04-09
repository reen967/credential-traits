import streamlit as st
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

st.title("IPEDS Trait-Based College Explorer")

# Upload CSV
uploaded_file = st.file_uploader("Upload your IPEDS CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Step 1: Select Variables and Assign Weights")
    
    # Select variables and assign weights
    default_vars = ['Graduation rate - Bachelor degree within 4 years, total',
                    'SAT Math 75th percentile score',
                    'SAT Evidence-Based Reading and Writing 75th percentile score',
                    'Undergraduate enrollment']

    selected_vars = st.multiselect(
        "Choose variables to include in scoring",
        options=list(df.columns),
        default=default_vars
    )

    weights = {}
    for var in selected_vars:
        weights[var] = st.slider(f"Weight for {var}", min_value=0.0, max_value=1.0, value=0.25, step=0.05)

    # Normalize and calculate score
    if selected_vars:
        st.subheader("Step 2: Filter and Rank")
        
        # Optional filters
        grad_min = st.slider("Minimum graduation rate (%)", 0, 100, 0)
        
        filtered_df = df.copy()
        if 'Graduation rate - Bachelor degree within 4 years, total' in filtered_df.columns:
            filtered_df = filtered_df[
                filtered_df['Graduation rate - Bachelor degree within 4 years, total'].fillna(0) >= grad_min
            ]

        # Normalize selected columns
        scaler = MinMaxScaler()
        norm_df = pd.DataFrame(scaler.fit_transform(filtered_df[selected_vars].fillna(0)), columns=selected_vars)

        # Composite score
        composite_score = sum(norm_df[var] * weights[var] for var in selected_vars)
        filtered_df['Composite Score'] = composite_score

        # Display results
        ranked = filtered_df.sort_values("Composite Score", ascending=False)
        st.write(ranked[['Institution (entity) name', 'Composite Score'] + selected_vars].reset_index(drop=True))

        # Download button
        st.download_button(
            label="Download Results as CSV",
            data=ranked.to_csv(index=False).encode('utf-8'),
            file_name='filtered_ipeds_results.csv',
            mime='text/csv'
        )
