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
    # Support both CSV and XLSX
    if file.name.endswith('.csv'):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    
    # Standardize column types based on FB export
    df['Reporting starts'] = pd.to_datetime(df['Reporting starts'])
    df['Amount spent (INR)'] = pd.to_numeric(df['Amount spent (INR)'], errors='coerce').fillna(0)
    df['Results'] = pd.to_numeric(df['Results'], errors='coerce').fillna(0)
    df['Frequency'] = pd.to_numeric(df['Frequency'], errors='coerce').fillna(1.0)
    df['CTR'] = pd.to_numeric(df['CTR (link click-through rate)'], errors='coerce').fillna(0)
    
    # Safely add Landing page views for Tab 5
    if 'Landing page views' in df.columns:
        df['Landing page views'] = pd.to_numeric(df['Landing page views'], errors='coerce').fillna(0)
    else:
        df['Landing page views'] = 0
    
    return df

# --- Sidebar Controls ---
with st.sidebar:
    st.header("Data Ingestion")
    # Updated to accept xlsx
    uploaded_file = st.file_uploader("Upload Facebook Ads Data", type=["csv", "xlsx"])
    
    st.markdown("---")
    st.subheader("Display Settings")
    # Toggles to hide secondary metrics and prevent visual clutter
    show_advanced_fatigue = st.checkbox("Show Advanced Mechanical Indicators", value=False)
    show_rolling_charts = st.checkbox("Show Rolling Diagnostic Charts", value=True)

# --- Main Application ---
st.title("🚀 Advanced Ad-Strategy Optimizer")

if uploaded_file:
    data = load_and_clean_data(uploaded_file)
    
    # Define tabs (Added Tab 5)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Budget Allocation", 
        "Bayesian Testing", 
        "Path Analysis", 
        "Fatigue Diagnosis",
        "Rolling Diagnostics" # New Tab
    ])
    
    # --- Tab 1 to 3 Placeholders ---
    with tab1:
        st.info("Constrained Optimization logic goes here.")
    with tab2:
        st.info("Bayesian Testing logic goes here.")
    with tab3:
        st.info("Markov Chain Path Analysis logic goes here.")
    
    # --- Tab 4: Fatigue Diagnosis ---
    with tab4:
        st.subheader("Creative Fatigue & Saturation Analysis")
        
        # Ad Selector
        ad_list = data['Ad name'].dropna().unique().tolist()
        selected_ad = st.selectbox("Select Ad to Diagnose:", options=ad_list, key="fatigue_ad_select")
        
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

    # --- Tab 5: Rolling Diagnostics ---
    with tab5:
        st.subheader("Dynamic Rolling Weighted Averages")
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            # Added "All Ads" to view overall account health
            ad_options = ["All Ads (Overall)"] + data['Ad name'].dropna().unique().tolist()
            selected_rolling_ad = st.selectbox("Select Ad/Scope:", options=ad_options, key="rolling_ad_select")
        with col_ctrl2:
            rolling_window = st.number_input("Rolling Window (Days)", min_value=1, max_value=90, value=7, step=1)
            
        if selected_rolling_ad == "All Ads (Overall)":
            df_filtered = data.copy()
        else:
            df_filtered = data[data['Ad name'] == selected_rolling_ad].copy()
            
        # Group by day to create a continuous time series
        daily_df = df_filtered.groupby('Reporting starts').agg({
            'Amount spent (INR)': 'sum',
            'Landing page views': 'sum',
            'Results': 'sum'
        }).reset_index().sort_values('Reporting starts')
        
        # Reindex to fill missing days with 0 (critical for accurate rolling averages)
        if not daily_df.empty:
            daily_df.set_index('Reporting starts', inplace=True)
            idx = pd.date_range(daily_df.index.min(), daily_df.index.max())
            daily_df = daily_df.reindex(idx, fill_value=0)
            
            # Roll absolute values first
            daily_df['Roll Spend'] = daily_df['Amount spent (INR)'].rolling(window=rolling_window, min_periods=1).sum()
            daily_df['Roll LPV'] = daily_df['Landing page views'].rolling(window=rolling_window, min_periods=1).sum()
            daily_df['Roll Purch'] = daily_df['Results'].rolling(window=rolling_window, min_periods=1).sum()
            
            # Calculate ratios from the rolled absolute values
            daily_df['Roll Cost/LPV'] = np.where(daily_df['Roll LPV'] > 0, daily_df['Roll Spend'] / daily_df['Roll LPV'], 0)
            daily_df['Roll LPV->Purchase %'] = np.where(daily_df['Roll LPV'] > 0, (daily_df['Roll Purch'] / daily_df['Roll LPV']) * 100, 0)
            daily_df['Roll CPA'] = np.where(daily_df['Roll Purch'] > 0, daily_df['Roll Spend'] / daily_df['Roll Purch'], 0)
            
            latest_data = daily_df.iloc[-1]
            
            st.markdown("---")
            st.markdown(f"### Current {rolling_window}-Day Rolling Metrics")
            
            # Display absolute values alongside ratios
            kpi1, kpi2, kpi3 = st.columns(3)
            with kpi1:
                st.metric("Roll Spend", f"₹{latest_data['Roll Spend']:,.2f}")
                st.metric("Roll CPA", f"₹{latest_data['Roll CPA']:,.2f}")
            with kpi2:
                st.metric("Roll LPVs (Absolute)", f"{latest_data['Roll LPV']:,.0f}")
                st.metric("Roll Cost/LPV", f"₹{latest_data['Roll Cost/LPV']:,.2f}")
            with kpi3:
                st.metric("Roll Purchases (Absolute)", f"{latest_data['Roll Purch']:,.0f}")
                st.metric("Roll LPV -> Purchase %", f"{latest_data['Roll LPV->Purchase %']:.2f}%")
            
            # --- Diagnostic Visualization ---
            if show_rolling_charts:
                st.markdown("---")
                st.markdown(f"### Historical {rolling_window}-Day Efficiency Trajectory")
                
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig.add_trace(go.Scatter(
                    x=daily_df.index,
                    y=daily_df['Roll CPA'],
                    mode='lines',
                    name='Rolling CPA (₹)',
                    line=dict(color='#0066CC', width=3)
                ), secondary_y=False)
                
                fig.add_trace(go.Scatter(
                    x=daily_df.index,
                    y=daily_df['Roll LPV->Purchase %'],
                    mode='lines',
                    name='Rolling LPV->Purch %',
                    line=dict(color='#A0C4FF', width=2, dash='dash')
                ), secondary_y=True)
                
                fig.update_layout(
                    plot_bgcolor='white',
                    xaxis=dict(title='Date', showgrid=True, gridcolor='#E0E0E0'),
                    hovermode='x unified'
                )
                fig.update_yaxes(title_text="Rolling CPA (INR)", secondary_y=False, showgrid=False)
                fig.update_yaxes(title_text="Conversion Rate (%)", secondary_y=True, showgrid=False)
                
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Upload your raw Facebook Ads CSV or XLSX in the sidebar to run the diagnostics.")
