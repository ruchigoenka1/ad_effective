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
    
    # Define tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Budget Allocation", 
        "Bayesian Testing", 
        "Path Analysis", 
        "Fatigue Diagnosis",
        "Rolling Diagnostics"
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
                
                fig_mech.add_trace(go.Scatter(
                    x=weekly_df['Reporting starts'],
                    y=weekly_df['Frequency'],
                    mode='lines+markers',
                    name='Avg Frequency',
                    line=dict(color='#003366', width=2)
                ), secondary_y=False)
                
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
    # --- Tab 5: Rolling Diagnostics ---
    # --- Tab 5: Rolling Diagnostics ---
    # --- Tab 5: Rolling Diagnostics ---
    # --- Tab 5: Rolling Diagnostics ---
    # --- Tab 5: Rolling Diagnostics ---
    # --- Tab 5: Rolling Diagnostics ---
    with tab5:
        st.subheader("Dynamic Rolling Weighted Averages")
        
        col_ctrl1, col_ctrl2 = st.columns(2)
        with col_ctrl1:
            ad_options = ["Compare All Ads", "All Ads (Overall)"] + data['Ad name'].dropna().unique().tolist()
            selected_rolling_ad = st.selectbox("Select Ad/Scope:", options=ad_options, key="rolling_ad_select")
        with col_ctrl2:
            rolling_window = st.number_input("Daily Rolling Window (Days)", min_value=1, max_value=90, value=7, step=1)

        # Define the Dark Theme layout to be reused across all charts in this tab
        dark_layout = dict(
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            xaxis=dict(showgrid=True, gridcolor='#333333', title='Date'),
            yaxis=dict(showgrid=True, gridcolor='#333333'),
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
            
        if selected_rolling_ad == "Compare All Ads":
            # --- COMPARISON MODE ---
            st.markdown("---")
            st.markdown(f"### Visualizing {rolling_window}-Day Rolling Metrics Across All Ads")
            
            all_ads_rolled = []
            for ad in data['Ad name'].dropna().unique():
                ad_df = data[data['Ad name'] == ad].groupby('Reporting starts').agg({
                    'Amount spent (INR)': 'sum',
                    'Landing page views': 'sum',
                    'Results': 'sum'
                }).reset_index().sort_values('Reporting starts')
                
                if not ad_df.empty:
                    ad_df.set_index('Reporting starts', inplace=True)
                    idx = pd.date_range(ad_df.index.min(), ad_df.index.max())
                    ad_df = ad_df.reindex(idx, fill_value=0)
                    
                    ad_df['Roll Spend'] = ad_df['Amount spent (INR)'].rolling(window=rolling_window, min_periods=1).sum()
                    ad_df['Roll LPV'] = ad_df['Landing page views'].rolling(window=rolling_window, min_periods=1).sum()
                    ad_df['Roll Purch'] = ad_df['Results'].rolling(window=rolling_window, min_periods=1).sum()
                    
                    ad_df['Roll CPA'] = np.where(ad_df['Roll Purch'] > 0, ad_df['Roll Spend'] / ad_df['Roll Purch'], 0)
                    ad_df['Roll LPV->Purchase %'] = np.where(ad_df['Roll LPV'] > 0, (ad_df['Roll Purch'] / ad_df['Roll LPV']) * 100, 0)
                    ad_df['Roll Cost/LPV'] = np.where(ad_df['Roll LPV'] > 0, ad_df['Roll Spend'] / ad_df['Roll LPV'], 0)
                    
                    ad_df['Ad name'] = ad
                    all_ads_rolled.append(ad_df)
            
            if all_ads_rolled:
                combined_df = pd.concat(all_ads_rolled).reset_index()
                combined_df.rename(columns={'index': 'Date'}, inplace=True)
                
                # --- Tabular Data Audit for Comparison ---
                st.markdown(f"### 📋 {rolling_window}-Day Rolling Data Log (All Ads)")
                
                display_combined_df = combined_df[['Date', 'Ad name', 'Roll Spend', 'Roll LPV', 'Roll Purch', 'Roll Cost/LPV', 'Roll LPV->Purchase %', 'Roll CPA']].copy()
                display_combined_df = display_combined_df.sort_values(by=['Date', 'Ad name'], ascending=[False, True])
                
                st.dataframe(
                    display_combined_df.style.format({
                        'Date': lambda t: t.strftime('%Y-%m-%d'),
                        'Roll Spend': '₹{:,.2f}',
                        'Roll LPV': '{:,.0f}',
                        'Roll Purch': '{:,.0f}',
                        'Roll Cost/LPV': '₹{:,.2f}',
                        'Roll LPV->Purchase %': '{:.2f}%',
                        'Roll CPA': '₹{:,.2f}'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                
                # Chart 1: Rolling CPA with Trendlines
                st.markdown("#### Cost Per Acquisition (CPA)")
                fig_cpa = go.Figure()
                
                # Define a distinct color palette to pair ads with their trendlines
                color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
                
                for i, ad in enumerate(combined_df['Ad name'].unique()):
                    ad_data = combined_df[combined_df['Ad name'] == ad]
                    base_color = color_palette[i % len(color_palette)]
                    
                    # Actual Rolling Data
                    fig_cpa.add_trace(go.Scatter(
                        x=ad_data['Date'], 
                        y=ad_data['Roll CPA'], 
                        mode='lines', 
                        name=ad,
                        line=dict(color=base_color, width=2)
                    ))
                    
                    # Linear Trendline Calculation (OLS Regression)
                    if len(ad_data) > 1:
                        x_num = np.arange(len(ad_data))
                        z = np.polyfit(x_num, ad_data['Roll CPA'], 1)
                        p = np.poly1d(z)
                        fig_cpa.add_trace(go.Scatter(
                            x=ad_data['Date'], 
                            y=p(x_num), 
                            mode='lines', 
                            name=f"{ad} (Trend)",
                            line=dict(color=base_color, width=1.5, dash='dot'),
                            showlegend=False # Prevents legend clutter
                        ))
                        
                fig_cpa.update_layout(yaxis_title="Rolling CPA (INR)", **dark_layout)
                st.plotly_chart(fig_cpa, use_container_width=True)
                
                # Chart 2: Rolling Conversion Rate
                st.markdown("#### Conversion Rate (LPV -> Purchase)")
                fig_cvr = go.Figure()
                for ad in combined_df['Ad name'].unique():
                    ad_data = combined_df[combined_df['Ad name'] == ad]
                    fig_cvr.add_trace(go.Scatter(x=ad_data['Date'], y=ad_data['Roll LPV->Purchase %'], mode='lines', name=ad))
                fig_cvr.update_layout(yaxis_title="LPV -> Purchase (%)", **dark_layout)
                st.plotly_chart(fig_cvr, use_container_width=True)
                
                # Chart 3: Rolling Spend
                st.markdown("#### Budget Deployment (Spend)")
                fig_spend = go.Figure()
                for ad in combined_df['Ad name'].unique():
                    ad_data = combined_df[combined_df['Ad name'] == ad]
                    fig_spend.add_trace(go.Scatter(x=ad_data['Date'], y=ad_data['Roll Spend'], mode='lines', name=ad))
                fig_spend.update_layout(yaxis_title="Rolling Spend (INR)", **dark_layout)
                st.plotly_chart(fig_spend, use_container_width=True)
        
        else:
            # --- INDIVIDUAL OR OVERALL MODE ---
            if selected_rolling_ad == "All Ads (Overall)":
                df_filtered = data.copy()
            else:
                df_filtered = data[data['Ad name'] == selected_rolling_ad].copy()
                
            daily_df = df_filtered.groupby('Reporting starts').agg({
                'Amount spent (INR)': 'sum',
                'Landing page views': 'sum',
                'Results': 'sum'
            }).reset_index().sort_values('Reporting starts')
            
            if not daily_df.empty:
                daily_df.set_index('Reporting starts', inplace=True)
                
                # --- NEW LOGIC: Trim leading inactive days for individual ads ---
                if selected_rolling_ad != "All Ads (Overall)":
                    first_spend_date = daily_df[daily_df['Amount spent (INR)'] > 0].index.min()
                    if pd.notna(first_spend_date):
                        daily_df = daily_df.loc[first_spend_date:]
                # ---------------------------------------------------------------
                
                # Reindex creates a continuous timeline from the true start date to the max date
                idx = pd.date_range(daily_df.index.min(), daily_df.index.max())
                daily_df = daily_df.reindex(idx, fill_value=0)
                
                daily_df['Roll Spend'] = daily_df['Amount spent (INR)'].rolling(window=rolling_window, min_periods=1).sum()
                daily_df['Roll LPV'] = daily_df['Landing page views'].rolling(window=rolling_window, min_periods=1).sum()
                daily_df['Roll Purch'] = daily_df['Results'].rolling(window=rolling_window, min_periods=1).sum()
                
                daily_df['Roll Cost/LPV'] = np.where(daily_df['Roll LPV'] > 0, daily_df['Roll Spend'] / daily_df['Roll LPV'], 0)
                daily_df['Roll LPV->Purchase %'] = np.where(daily_df['Roll LPV'] > 0, (daily_df['Roll Purch'] / daily_df['Roll LPV']) * 100, 0)
                daily_df['Roll CPA'] = np.where(daily_df['Roll Purch'] > 0, daily_df['Roll Spend'] / daily_df['Roll Purch'], 0)
                
                latest_data = daily_df.iloc[-1]
                
                st.markdown("---")
                st.markdown(f"### Current {rolling_window}-Day Rolling Metrics")
                
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

                # --- Tabular Data Audit ---
                st.markdown("---")
                st.markdown(f"### 📋 {rolling_window}-Day Rolling Data Log")
                
                display_df = daily_df[['Roll Spend', 'Roll LPV', 'Roll Purch', 'Roll Cost/LPV', 'Roll LPV->Purchase %', 'Roll CPA']].copy()
                display_df = display_df.sort_index(ascending=False) 
                
                st.dataframe(
                    display_df.style.format({
                        'Roll Spend': '₹{:,.2f}',
                        'Roll LPV': '{:,.0f}',
                        'Roll Purch': '{:,.0f}',
                        'Roll Cost/LPV': '₹{:,.2f}',
                        'Roll LPV->Purchase %': '{:.2f}%',
                        'Roll CPA': '₹{:,.2f}'
                    }),
                    use_container_width=True
                )
                
                if show_rolling_charts:
                    st.markdown("---")
                    st.markdown(f"### Historical {rolling_window}-Day Efficiency Trajectory")
                    
                    st.markdown("#### Cost Per Acquisition (CPA)")
                    fig_cpa = go.Figure()
                    
                    # Actual Rolling Data
                    fig_cpa.add_trace(go.Scatter(
                        x=daily_df.index, 
                        y=daily_df['Roll CPA'], 
                        mode='lines', 
                        name='Rolling CPA (₹)', 
                        line=dict(color='#0066CC', width=3)
                    ))
                    
                    # Linear Trendline Calculation (OLS Regression)
                    if len(daily_df) > 1:
                        x_num = np.arange(len(daily_df))
                        z = np.polyfit(x_num, daily_df['Roll CPA'], 1)
                        p = np.poly1d(z)
                        fig_cpa.add_trace(go.Scatter(
                            x=daily_df.index, 
                            y=p(x_num), 
                            mode='lines', 
                            name='CPA Trend (Linear)', 
                            line=dict(color='#FF4B4B', width=2, dash='dash')
                        ))

                    fig_cpa.update_layout(yaxis_title="Rolling CPA (INR)", **dark_layout)
                    st.plotly_chart(fig_cpa, use_container_width=True)

                    st.markdown("#### Conversion Rate (LPV -> Purchase)")
                    fig_cvr = go.Figure()
                    fig_cvr.add_trace(go.Scatter(x=daily_df.index, y=daily_df['Roll LPV->Purchase %'], mode='lines', name='Rolling LPV->Purch %', line=dict(color='#A0C4FF', width=3)))
                    fig_cvr.update_layout(yaxis_title="LPV -> Purchase (%)", **dark_layout)
                    st.plotly_chart(fig_cvr, use_container_width=True)

                    st.markdown("#### Budget Deployment (Spend)")
                    fig_spend = go.Figure()
                    fig_spend.add_trace(go.Scatter(x=daily_df.index, y=daily_df['Roll Spend'], mode='lines', name='Rolling Spend (₹)', line=dict(color='#FFFFFF', width=3)))
                    fig_spend.update_layout(yaxis_title="Rolling Spend (INR)", **dark_layout)
                    st.plotly_chart(fig_spend, use_container_width=True)

        # --- SECTION: Performance Analysis (DOW & Weekly) ---
        st.markdown("---")
        st.subheader("📅 Time-Based Performance Analysis")
        st.markdown(f"Analyzing data for: **{selected_rolling_ad}**")
        
        if selected_rolling_ad == "Compare All Ads":
            time_base_df = data.copy()
        else:
            time_base_df = df_filtered.copy()
            
        # Ensure click metrics exist before grouping
        for col in ['Impressions', 'Link clicks']:
            if col not in time_base_df.columns:
                time_base_df[col] = 0
            else:
                time_base_df[col] = pd.to_numeric(time_base_df[col], errors='coerce').fillna(0)

        if not time_base_df.empty:
            min_date = time_base_df['Reporting starts'].min().date()
            max_date = time_base_df['Reporting starts'].max().date()
            
            # --- Global Date Inputs for both DOW and Weekly ---
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
            with col_d2:
                end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
                
            if start_date <= end_date:
                mask = (time_base_df['Reporting starts'].dt.date >= start_date) & (time_base_df['Reporting starts'].dt.date <= end_date)
                filtered_time_df = time_base_df[mask].copy()
                
                # --- 1. Static DOW Matrix ---
                st.markdown("### Absolute Date-Range Aggregation (Day of Week)")
                filtered_time_df['Day of Week'] = filtered_time_df['Reporting starts'].dt.day_name()
                
                dow_agg = filtered_time_df.groupby('Day of Week').agg({
                    'Amount spent (INR)': 'sum',
                    'Impressions': 'sum',
                    'Link clicks': 'sum',
                    'Landing page views': 'sum',
                    'Results': 'sum'
                }).reset_index()
                
                days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                dow_agg['Day of Week'] = pd.Categorical(dow_agg['Day of Week'], categories=days_order, ordered=True)
                dow_agg = dow_agg.sort_values('Day of Week')
                
                dow_agg['CTR (%)'] = np.where(dow_agg['Impressions'] > 0, (dow_agg['Link clicks'] / dow_agg['Impressions']) * 100, 0)
                dow_agg['Cost/LPV (INR)'] = np.where(dow_agg['Landing page views'] > 0, dow_agg['Amount spent (INR)'] / dow_agg['Landing page views'], 0)
                dow_agg['Link->LPV (%)'] = np.where(dow_agg['Link clicks'] > 0, (dow_agg['Landing page views'] / dow_agg['Link clicks']) * 100, 0)
                dow_agg['LPV->Purchase (%)'] = np.where(dow_agg['Landing page views'] > 0, (dow_agg['Results'] / dow_agg['Landing page views']) * 100, 0)
                dow_agg['CPA (INR)'] = np.where(dow_agg['Results'] > 0, dow_agg['Amount spent (INR)'] / dow_agg['Results'], 0)
                
                # Display DOW Table
                with st.expander("Show Raw Data Table (Day of Week)"):
                    st.dataframe(
                        dow_agg.style.format({
                            'Amount spent (INR)': '₹{:,.2f}',
                            'Impressions': '{:,.0f}',
                            'Link clicks': '{:,.0f}',
                            'Landing page views': '{:,.0f}',
                            'Results': '{:,.0f}',
                            'CTR (%)': '{:.2f}%',
                            'Cost/LPV (INR)': '₹{:,.2f}',
                            'Link->LPV (%)': '{:.2f}%',
                            'LPV->Purchase (%)': '{:.2f}%',
                            'CPA (INR)': '₹{:,.2f}'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                bar_layout = dark_layout.copy()
                bar_layout['xaxis'] = dict(showgrid=False, gridcolor='#333333')
                
                col_bar1, col_bar2, col_bar3 = st.columns(3)
                with col_bar1:
                    fig_dow_cpa = go.Figure(data=[go.Bar(x=dow_agg['Day of Week'], y=dow_agg['CPA (INR)'], marker_color='#FF4B4B')])
                    fig_dow_cpa.update_layout(title="Average CPA by Day", yaxis_title="CPA (INR)", **bar_layout)
                    st.plotly_chart(fig_dow_cpa, use_container_width=True)
                with col_bar2:
                    fig_dow_cplpv = go.Figure(data=[go.Bar(x=dow_agg['Day of Week'], y=dow_agg['Cost/LPV (INR)'], marker_color='#FFA500')])
                    fig_dow_cplpv.update_layout(title="Cost per LPV by Day", yaxis_title="Cost (INR)", **bar_layout)
                    st.plotly_chart(fig_dow_cplpv, use_container_width=True)
                with col_bar3:
                    fig_dow_ctr = go.Figure(data=[go.Bar(x=dow_agg['Day of Week'], y=dow_agg['CTR (%)'], marker_color='#0088CC')])
                    fig_dow_ctr.update_layout(title="Click-Through Rate (CTR)", yaxis_title="CTR (%)", **bar_layout)
                    st.plotly_chart(fig_dow_ctr, use_container_width=True)
                    
                
                # Row 2: Link->LPV, Spend, LPV->Purchase
                col_bar4, col_bar5, col_bar6 = st.columns(3)
                with col_bar4:
                    fig_dow_dropoff = go.Figure(data=[go.Bar(x=dow_agg['Day of Week'], y=dow_agg['Link->LPV (%)'], marker_color='#A0C4FF')])
                    fig_dow_dropoff.update_layout(title="Link Click to LPV (%)", yaxis_title="Percentage (%)", **bar_layout)
                    st.plotly_chart(fig_dow_dropoff, use_container_width=True)
                with col_bar5:
                    fig_dow_spend = go.Figure(data=[go.Bar(x=dow_agg['Day of Week'], y=dow_agg['Amount spent (INR)'], marker_color='#FFFFFF')])
                    fig_dow_spend.update_layout(title="Total Spend by Day", yaxis_title="Spend (INR)", **bar_layout)
                    st.plotly_chart(fig_dow_spend, use_container_width=True)
                with col_bar6:
                    fig_dow_lpv_purch = go.Figure(data=[go.Bar(x=dow_agg['Day of Week'], y=dow_agg['LPV->Purchase (%)'], marker_color='#32CD32')])
                    fig_dow_lpv_purch.update_layout(title="LPV -> Purchase (%)", yaxis_title="Percentage (%)", **bar_layout)
                    st.plotly_chart(fig_dow_lpv_purch, use_container_width=True)

                # --- 2. Static Weekly Matrix ---
                st.markdown("---")
                st.markdown("### Absolute Date-Range Aggregation (Weekly Breakdown)")
                
                # Assign week starting on Monday
                filtered_time_df['Week Start'] = filtered_time_df['Reporting starts'].dt.to_period('W-MON').dt.start_time.dt.date
                
                week_agg = filtered_time_df.groupby('Week Start').agg({
                    'Amount spent (INR)': 'sum',
                    'Impressions': 'sum',
                    'Link clicks': 'sum',
                    'Landing page views': 'sum',
                    'Results': 'sum'
                }).reset_index()
                
                week_agg = week_agg.sort_values('Week Start')
                
                week_agg['CTR (%)'] = np.where(week_agg['Impressions'] > 0, (week_agg['Link clicks'] / week_agg['Impressions']) * 100, 0)
                week_agg['Cost/LPV (INR)'] = np.where(week_agg['Landing page views'] > 0, week_agg['Amount spent (INR)'] / week_agg['Landing page views'], 0)
                week_agg['Link->LPV (%)'] = np.where(week_agg['Link clicks'] > 0, (week_agg['Landing page views'] / week_agg['Link clicks']) * 100, 0)
                week_agg['LPV->Purchase (%)'] = np.where(week_agg['Landing page views'] > 0, (week_agg['Results'] / week_agg['Landing page views']) * 100, 0)
                week_agg['CPA (INR)'] = np.where(week_agg['Results'] > 0, week_agg['Amount spent (INR)'] / week_agg['Results'], 0)
                
                # Format dates for plotting and tables
                week_agg['Week Label'] = week_agg['Week Start'].apply(lambda x: x.strftime('%b %d, %Y'))
                
                # Display Weekly Table
                with st.expander("Show Raw Data Table (Weekly Breakdown)"):
                    st.dataframe(
                        week_agg[['Week Label', 'Amount spent (INR)', 'Impressions', 'Link clicks', 'Landing page views', 'Results', 'CTR (%)', 'Cost/LPV (INR)', 'Link->LPV (%)', 'LPV->Purchase (%)', 'CPA (INR)']].style.format({
                            'Amount spent (INR)': '₹{:,.2f}',
                            'Impressions': '{:,.0f}',
                            'Link clicks': '{:,.0f}',
                            'Landing page views': '{:,.0f}',
                            'Results': '{:,.0f}',
                            'CTR (%)': '{:.2f}%',
                            'Cost/LPV (INR)': '₹{:,.2f}',
                            'Link->LPV (%)': '{:.2f}%',
                            'LPV->Purchase (%)': '{:.2f}%',
                            'CPA (INR)': '₹{:,.2f}'
                        }),
                        use_container_width=True,
                        hide_index=True
                    )

                weekly_bar_layout = dark_layout.copy()
                weekly_bar_layout['xaxis'] = dict(showgrid=False, gridcolor='#333333', tickangle=45)
                
                col_w1, col_w2, col_w3 = st.columns(3)
                with col_w1:
                    fig_w_cpa = go.Figure(data=[go.Bar(x=week_agg['Week Label'], y=week_agg['CPA (INR)'], marker_color='#FF4B4B')])
                    fig_w_cpa.update_layout(title="Average CPA by Week", yaxis_title="CPA (INR)", **weekly_bar_layout)
                    st.plotly_chart(fig_w_cpa, use_container_width=True)
                with col_w2:
                    fig_w_cplpv = go.Figure(data=[go.Bar(x=week_agg['Week Label'], y=week_agg['Cost/LPV (INR)'], marker_color='#FFA500')])
                    fig_w_cplpv.update_layout(title="Cost per LPV by Week", yaxis_title="Cost (INR)", **weekly_bar_layout)
                    st.plotly_chart(fig_w_cplpv, use_container_width=True)
                with col_w3:
                    fig_w_ctr = go.Figure(data=[go.Bar(x=week_agg['Week Label'], y=week_agg['CTR (%)'], marker_color='#0088CC')])
                    fig_w_ctr.update_layout(title="Click-Through Rate (CTR) by Week", yaxis_title="CTR (%)", **weekly_bar_layout)
                    st.plotly_chart(fig_w_ctr, use_container_width=True)
                    
                col_w4, col_w5, col_w6 = st.columns(3)
                with col_w4:
                    fig_w_dropoff = go.Figure(data=[go.Bar(x=week_agg['Week Label'], y=week_agg['Link->LPV (%)'], marker_color='#A0C4FF')])
                    fig_w_dropoff.update_layout(title="Link Click to LPV (%) by Week", yaxis_title="Percentage (%)", **weekly_bar_layout)
                    st.plotly_chart(fig_w_dropoff, use_container_width=True)
                with col_w5:
                    fig_w_spend = go.Figure(data=[go.Bar(x=week_agg['Week Label'], y=week_agg['Amount spent (INR)'], marker_color='#FFFFFF')])
                    fig_w_spend.update_layout(title="Total Spend by Week", yaxis_title="Spend (INR)", **weekly_bar_layout)
                    st.plotly_chart(fig_w_spend, use_container_width=True)
                with col_w6:
                    fig_w_lpv_purch = go.Figure(data=[go.Bar(x=week_agg['Week Label'], y=week_agg['LPV->Purchase (%)'], marker_color='#32CD32')])
                    fig_w_lpv_purch.update_layout(title="LPV -> Purchase (%) by Week", yaxis_title="Percentage (%)", **weekly_bar_layout)
                    st.plotly_chart(fig_w_lpv_purch, use_container_width=True)

            # --- 3. Rolling DOW Trends (Weighted Average of Last N specific days) ---
            st.markdown("---")
            st.markdown("#### 🔄 Rolling Day-of-the-Week Trends")
            st.markdown("*(e.g., The weighted average of the last 7 Tuesdays)*")
            
            col_roll1, col_roll2 = st.columns(2)
            with col_roll1:
                dow_roll_window = st.number_input("DOW Lookback Window (Weeks)", min_value=1, max_value=24, value=7, step=1)
            with col_roll2:
                metric_to_plot = st.selectbox(
                    "Select Metric to Plot Over Time:", 
                    ["Rolling CPA", "Rolling Cost/LPV", "Rolling CTR (%)", "Rolling LPV->Purchase (%)"]
                )

            daily_dow_df = time_base_df.groupby('Reporting starts').agg({
                'Amount spent (INR)': 'sum',
                'Impressions': 'sum',
                'Link clicks': 'sum',
                'Landing page views': 'sum',
                'Results': 'sum'
            }).reset_index().sort_values('Reporting starts')
            
            daily_dow_df['Day of Week'] = daily_dow_df['Reporting starts'].dt.day_name()
            
            rolled_dow_list = []
            for day, group in daily_dow_df.groupby('Day of Week'):
                group = group.sort_values('Reporting starts')
                
                group['Roll Spend'] = group['Amount spent (INR)'].rolling(window=dow_roll_window, min_periods=1).sum()
                group['Roll Imp'] = group['Impressions'].rolling(window=dow_roll_window, min_periods=1).sum()
                group['Roll Clicks'] = group['Link clicks'].rolling(window=dow_roll_window, min_periods=1).sum()
                group['Roll LPV'] = group['Landing page views'].rolling(window=dow_roll_window, min_periods=1).sum()
                group['Roll Purch'] = group['Results'].rolling(window=dow_roll_window, min_periods=1).sum()
                
                group['Rolling CPA'] = np.where(group['Roll Purch'] > 0, group['Roll Spend'] / group['Roll Purch'], 0)
                group['Rolling Cost/LPV'] = np.where(group['Roll LPV'] > 0, group['Roll Spend'] / group['Roll LPV'], 0)
                group['Rolling CTR (%)'] = np.where(group['Roll Imp'] > 0, (group['Roll Clicks'] / group['Roll Imp']) * 100, 0)
                group['Rolling LPV->Purchase (%)'] = np.where(group['Roll LPV'] > 0, (group['Roll Purch'] / group['Roll LPV']) * 100, 0)
                
                rolled_dow_list.append(group)
                
            trend_dow_df = pd.concat(rolled_dow_list)
            
            fig_dow_trend = go.Figure()
            colors = {
                'Monday': '#1f77b4', 'Tuesday': '#ff7f0e', 'Wednesday': '#2ca02c', 
                'Thursday': '#d62728', 'Friday': '#9467bd', 'Saturday': '#8c564b', 'Sunday': '#e377c2'
            }
            
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
                day_data = trend_dow_df[trend_dow_df['Day of Week'] == day]
                if not day_data.empty:
                    fig_dow_trend.add_trace(go.Scatter(
                        x=day_data['Reporting starts'], 
                        y=day_data[metric_to_plot], 
                        mode='lines+markers', 
                        name=day,
                        line=dict(color=colors.get(day, '#FFFFFF'), width=2)
                    ))
            
            fig_dow_trend.update_layout(
                title=f"{dow_roll_window}-Week Rolling Trend for {metric_to_plot}",
                yaxis_title=metric_to_plot,
                **dark_layout
            )
            st.plotly_chart(fig_dow_trend, use_container_width=True)

        else:
            st.warning("No data available for the selected scope.")


else:
    st.info("Upload your raw Facebook Ads CSV or XLSX in the sidebar to run the diagnostics.")
