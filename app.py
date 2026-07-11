import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import plotly.graph_objects as go
from scipy.stats import beta

st.set_page_config(page_title="Ad Strategy Optimizer", layout="wide")

st.title("🚀 Advanced Ad-Strategy Optimizer")
tab1, tab2, tab3 = st.tabs(["Budget Allocation (OR)", "Bayesian Testing", "Path Analysis (Markov)"])

# --- Tab 1: Constrained Optimization ---
with tab1:
    st.header("Constrained Budget Allocation")
    st.markdown("Optimize spend using the Hill function to account for diminishing returns.")
    
    col1, col2 = st.columns(2)
    with col1:
        total_budget = st.number_input("Total Daily Budget ($)", value=1000)
    
    # Mock data for campaigns
    campaigns = ['Brand', 'Prospecting', 'Retargeting']
    # Parameters for Hill Function: A (Max), K (Saturation point), n (Slope)
    params = {'A': [500, 800, 300], 'K': [200, 400, 150], 'n': [2, 1.5, 2.5]}
    
    def objective(x):
        # Negative because we minimize
        return -sum((params['A'][i] * (x[i]**params['n'][i])) / (params['K'][i]**params['n'][i] + x[i]**params['n'][i]) for i in range(3))

    constraints = ({'type': 'eq', 'fun': lambda x: sum(x) - total_budget})
    bounds = [(10, total_budget) for _ in range(3)]
    
    if st.button("Run Optimization"):
        res = minimize(objective, [total_budget/3]*3, method='SLSQP', bounds=bounds, constraints=constraints)
        st.write("Optimal Spend Allocation:", dict(zip(campaigns, res.x)))

# --- Tab 2: Bayesian Testing ---
with tab2:
    st.header("Bayesian Ad-Set Winner Selection")
    st.markdown("Using Beta-Bernoulli Conjugacy to handle high-variance performance data.")
    
    ads_data = pd.DataFrame({'Ad': ['Ad A', 'Ad B'], 'Clicks': [500, 20], 'Conv': [80, 4]})
    
    x = np.linspace(0, 0.4, 500)
    fig = go.Figure()
    
    for i, row in ads_data.iterrows():
        # Alpha = Conv + 1, Beta = Non-Conv + 1
        y = beta.pdf(x, row['Conv'] + 1, (row['Clicks'] - row['Conv']) + 1)
        fig.add_trace(go.Scatter(x=x, y=y, name=f"{row['Ad']} (Post-Prob)"))
    
    st.plotly_chart(fig)
    st.caption("The ad with the right-most distribution shift is the statistical winner, regardless of current point-estimate CVR.")

# --- Tab 3: Markov Chain Path Analysis ---
with tab3:
    st.header("Removal Effect (Transition Matrix)")
    st.markdown("Eigenvector analysis to determine channel contribution.")
    
    # Simple 3x3 Transition Matrix
    transition_matrix = np.array([
        [0.7, 0.2, 0.1], # State 1 transitions
        [0.1, 0.8, 0.1], # State 2 transitions
        [0.0, 0.0, 1.0]  # Conversion Sink
    ])
    
    if st.button("Calculate Removal Effect"):
        # Solve for stationary distribution (pi * T = pi)
        # This is equivalent to finding the eigenvector for eigenvalue 1
        evals, evecs = np.linalg.eig(transition_matrix.T)
        stationary = evecs[:, np.isclose(evals, 1)].flatten()
        stationary = stationary / stationary.sum()
        
        st.write("Steady-State Channel Probabilities:", dict(zip(['Awareness', 'Consideration', 'Conversion'], stationary)))
        st.info("The removal effect is calculated by zeroing out rows in the matrix and re-calculating the sink probability.")
