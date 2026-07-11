import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---
st.set_page_config(page_title="Ad Strategy Optimizer", layout="wide")

# --- Helper Functions ---
@st.cache_data
def load_and_clean_data(file):
    df = pd.read_csv(file)
    
    # Standardize column types based on FB export
    df['Reporting starts'] = pd.to_datetime(df['Reporting starts'])
    df['Amount spent (INR)'] = pd.to_numeric(df['Amount spent (INR)'], errors='coerce').fillna(0)
    df['Results'] = pd.to_numeric(df['Results'], errors='coerce').fillna(0)
    df['Frequency'] = pd.to_numeric(df['Frequency'], errors='coerce').fillna(1.0)
    df['CTR'] = pd.to_numeric(df['CTR (link click-through rate)'], errors='coerce').fillna(0)
    
    return df

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Data Ingestion")
    uploaded_file = st.file_uploader("Upload Facebook Ads CSV", type=["csv"])
    
    st.markdown("---")
    st.subheader("Display Settings")
    # Toggle to hide secondary metrics and prevent visual clutter
    show_advanced_fatigue = st.checkbox("Show Advanced Mechanical Indicators", value=False)

# --- Main Application ---
st.title("🚀 Advanced Ad-Strategy Optimizer")

if uploaded_file:
    data = load_and_clean_data(uploaded_file)
    
    # Define tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Budget Allocation", 
        "Bayesian Testing", 
        "Path Analysis", 
        "Fatigue Diagnosis" # New Tab
    ])
    
    # --- Tab 4: Fatigue Diagnosis ---
    with tab4:
        st.subheader("Creative Fatigue & Saturation Analysis")
        
        # Ad Selector
        ad_list = data['Ad name'].dropna().unique().tolist()
        selected_ad = st.selectbox("Select Ad to Diagnose:", options=ad_list)
        
        if selected_ad:
            # Filter and sort chronological data for the selected ad
            ad_df = data[data['Ad name'] == selected_ad].sort_values('Reporting starts')
            
            # Aggregate by week to smooth out daily variance
            weekly_df = ad_df.set_index('Reporting starts').resample('W').agg({
                'Amount spent (INR)': 'sum',
                'Results': 'sum',
                'Frequency': 'mean',
                'CTR': 'mean'
            }).dropna().reset_index()
            
            weekly_df['Cumulative Spend'] = weekly_df['Amount spent (INR)'].cumsum()
            weekly_df['Cumulative Results'] = weekly_df['Results'].cumsum()
            
            # --- Absolute Value KPIs ---
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Absolute Total Spend (INR)", value=f"₹{weekly_df['Amount spent (INR)'].sum():,.2f}")
            with col2:
                st.metric(label="Absolute Total Conversions", value=f"{weekly_df['Results'].sum():,.0f}")
                
            st.markdown("---")
            
            # --- Primary Chart: Cumulative Saturation ---
            st.markdown("### Cumulative Performance (Saturation Check)")
            
            fig_cum = go.Figure()
            
            # Actual Performance Line
            fig_cum.add_trace(go.Scatter(
                x=weekly_df['Cumulative Spend'], 
                y=weekly_df['Cumulative Results'],
                mode='lines',
                name='Actual Performance',
                line=dict(color='#0066CC', width=3)
            ))
            
            # Theoretical Constant Efficiency (Dashed)
            if len(weekly_df) > 1 and weekly_df['Cumulative Spend'].iloc[1] > 0:
                baseline_eff = weekly_df['Cumulative Results'].iloc[1] / weekly_df['Cumulative Spend'].iloc[1]
                fig_cum.add_trace(go.Scatter(
                    x=weekly_df['Cumulative Spend'],
                    y=weekly_df['Cumulative Spend'] * baseline_eff,
                    mode='lines',
                    name='Theoretical (No Fatigue)',
                    line=dict(color='#A0C4FF', width=2, dash='dash')
                ))
                
            fig_cum.update_layout(
                plot_bgcolor='white',
                xaxis=dict(title='Cumulative Spend (INR)', showgrid=True, gridcolor='#E0E0E0'),
                yaxis=dict(title='Cumulative Conversions', showgrid=True, gridcolor='#E0E0E0'),
                hovermode='x unified'
            )
            st.plotly_chart(fig_cum, use_container_width=True)
            
            # --- Secondary Chart: Mechanical Indicators (Toggled) ---
            if show_advanced_fatigue:
                st.markdown("### Mechanical Indicators (Frequency vs. CTR)")
                
                fig_mech = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Frequency Line
                fig_mech.add_trace(go.Scatter(
                    x=weekly_df['Reporting starts'],
                    y=weekly_df['Frequency'],
                    mode='lines+markers',
                    name='Avg Frequency',
                    line=dict(color='#003366', width=2)
                ), secondary_y=False)
                
                # CTR Line
                fig_mech.add_trace(go.Scatter(
                    x=weekly_df['Reporting starts'],
                    y=weekly_df['CTR'],
                    mode='lines+markers',
                    name='CTR (%)',
                    line=dict(color='#0088CC', width=2, dash='dot')
                ), secondary_y=True)
                
                fig_mech.update_layout(
                    plot_bgcolor='white',
                    xaxis=dict(title='Timeline', showgrid=True, gridcolor='#E0E0E0'),
                    hovermode='x unified'
                )
                fig_mech.update_yaxes(title_text="Frequency", secondary_y=False, showgrid=False)
                fig_mech.update_yaxes(title_text="Click-Through Rate (%)", secondary_y=True, showgrid=False)
                
                st.plotly_chart(fig_mech, use_container_width=True)

else:
    st.info("Upload your raw Facebook Ads CSV in the sidebar to run the diagnostics.")
