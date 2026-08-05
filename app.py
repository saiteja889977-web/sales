import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# 1. Page Configuration
st.set_page_config(
    page_title="Sales Operations Intelligence Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Theme Engine
st.sidebar.markdown("### 🎨 Visual Theme")
dark_mode = st.sidebar.toggle("🌌 Night Ledger (Dark Mode)", value=False)

if dark_mode:
    primary_color = "#A78BFA"
    bg_color = "#0F172A"
    card_bg = "#1E293B"
    text_color = "#F8FAFC"
    plotly_template = "plotly_dark"
    accent_gradient = "linear-gradient(135deg, #1E1B4B 0%, #311042 100%)"
else:
    primary_color = "#1E40AF"
    bg_color = "#F8FAFC"
    card_bg = "#FFFFFF"
    text_color = "#0F172A"
    plotly_template = "plotly_white"
    accent_gradient = "linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%)"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .hero-banner {{ background: {accent_gradient}; padding: 25px; border-radius: 12px; color: #FFFFFF; margin-bottom: 25px; }}
    .kpi-card {{ background-color: {card_bg}; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-top: 4px solid {primary_color}; text-align: center; color: {text_color}; }}
    </style>
""", unsafe_allow_html=True)

# 3. Dynamic Column Matching Engine
def process_data(file_source):
    df = pd.read_excel(file_source, sheet_name=0)
    df.columns = df.columns.astype(str).str.strip()
    
    mapping = {}
    for col in df.columns:
        c_upper = col.upper()
        if 'USER' in c_upper or 'REP' in c_upper or 'AGENT' in c_upper:
            mapping[col] = 'USER'
        elif 'DISTRIBUTOR' in c_upper or 'DEALER' in c_upper or 'CLIENT' in c_upper:
            mapping[col] = 'Distributor'
        elif 'BEAT' in c_upper or 'ROUTE' in c_upper or 'AREA' in c_upper:
            mapping[col] = 'Beat'
        elif 'QTY' in c_upper or 'QUANTITY' in c_upper or 'VOLUME' in c_upper or 'UNITS' in c_upper:
            mapping[col] = 'QTY'
        elif 'CATEGORY' in c_upper or 'PRODUCT' in c_upper or 'BRAND' in c_upper:
            mapping[col] = 'PrimaryCategory'
        elif 'PERIOD 1' in c_upper or 'P1' in c_upper:
            mapping[col] = 'Period 1'
        elif 'PERIOD 2' in c_upper or 'P2' in c_upper:
            mapping[col] = 'Period 2'
        elif 'DATE' in c_upper or 'MONTH' in c_upper:
            mapping[col] = 'Date'
        
    df = df.rename(columns=mapping)
    
    # Set default primary category to 'Heartiva' if not specified or empty
    if 'PrimaryCategory' not in df.columns:
        df['PrimaryCategory'] = 'Heartiva'
    else:
        df['PrimaryCategory'] = df['PrimaryCategory'].fillna('Heartiva')

    # Defaults for other required fields
    if 'QTY' not in df.columns:
        num_cols = df.select_dtypes(include=['number']).columns
        df['QTY'] = df[num_cols[0]] if len(num_cols) > 0 else 1

    if 'USER' not in df.columns:
        df['USER'] = 'Default User'
    if 'Distributor' not in df.columns:
        df['Distributor'] = 'Default Distributor'
    if 'Beat' not in df.columns:
        df['Beat'] = 'Default Beat'

    if 'Period 1' not in df.columns: 
        df['Period 1'] = df['QTY'] * 0.45
    if 'Period 2' not in df.columns: 
        df['Period 2'] = df['QTY'] * 0.55
    if 'Date' not in df.columns: 
        df['Date'] = pd.Timestamp('2026-08-01')
        
    df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce').fillna(0)
    df['Period 1'] = pd.to_numeric(df['Period 1'], errors='coerce').fillna(0)
    df['Period 2'] = pd.to_numeric(df['Period 2'], errors='coerce').fillna(0)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').fillna(pd.Timestamp('2026-08-01'))
    return df

# App Banner Header
st.markdown("""
    <div class="hero-banner">
        <h1>⚡ Enterprise Sales Command Suite</h1>
        <p>Operational execution matrix featuring live user dashboard uploads, period tracking, and dynamic analytics.</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar Uploader
st.sidebar.markdown("### 📂 Data Source Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Sales Excel Sheet:", type=["xlsx", "xls"], key="sidebar_uploader")

raw_df = None

if uploaded_file is not None:
    try:
        raw_df = process_data(uploaded_file)
        st.sidebar.success("🎉 Data loaded & mapped!")
    except Exception as e:
        st.sidebar.error(f"Error parsing uploaded file: {e}")

elif os.path.exists("Distributer wise sale.xlsx"):
    try:
        raw_df = process_data("Distributer wise sale.xlsx")
        st.sidebar.info("ℹ️ Loaded default repository file.")
    except Exception:
        pass

# Landing page if no data loaded yet
if raw_df is None:
    st.info("👋 **Welcome! Please drop your Excel sheet below to launch the dashboard.**")
    main_uploaded_file = st.file_uploader("Drop your Sales Excel file (.xlsx) here:", type=["xlsx", "xls"], key="main_uploader")
    if main_uploaded_file is not None:
        try:
            raw_df = process_data(main_uploaded_file)
            st.rerun()
        except Exception as e:
            st.error(f"Error processing file: {e}")
    st.stop()

# Assign mapped target columns
user_col = "USER"
dist_col = "Distributor"
beat_col = "Beat"

# Main Navigation Hub
tab_main, tab_compare = st.tabs(["📊 Multi-Level Analysis", "🔀 Leaderboard"])

with tab_main:
    st.markdown("### 🎛️ Navigation Deck")
    c_search, c_toggle = st.columns([2, 1])
    with c_search:
        global_search = st.text_input("🔍 Search (User, Distributor, Category, Beat):", "")
    with c_toggle:
        st.write("")
        st.write("")
        hide_inactive = st.checkbox("🚫 Filter Out Zero Orders", value=False)

    u_opts = ["📊 Show All System Users"] + sorted(raw_df[user_col].dropna().unique().tolist())
    sel_user = st.selectbox("1. Filter by Representative:", u_opts)

    if sel_user != "📊 Show All System Users":
        sub_df1 = raw_df[raw_df[user_col] == sel_user]
        d_opts = ["📊 Show All Rep Distributors"] + sorted(sub_df1[dist_col].dropna().unique().tolist())
    else:
        sub_df1 = raw_df.copy()
        d_opts = ["Select a User first to filter targets"]

    sel_dist = st.selectbox("2. Filter by Distribution Node:", d_opts, disabled=(sel_user == "📊 Show All System Users"))

    working_df = sub_df1.copy()
    if sel_user != "📊 Show All System Users":
        working_df = working_df[working_df[user_col] == sel_user]
    if sel_dist != "📊 Show All Rep Distributors" and sel_dist in sub_df1[dist_col].values:
        working_df = working_df[working_df[dist_col] == sel_dist]

    if hide_inactive:
        working_df = working_df[working_df['QTY'] > 0]
    if global_search:
        working_df = working_df[
            working_df[user_col].astype(str).str.contains(global_search, case=False) |
            working_df[dist_col].astype(str).str.contains(global_search, case=False) |
            working_df[beat_col].astype(str).str.contains(global_search, case=False) |
            working_df['PrimaryCategory'].astype(str).str.contains(global_search, case=False)
        ]

    # Metrics Row
    gl_tot = working_df['QTY'].sum()
    p1_tot = working_df['Period 1'].sum()
    p2_tot = working_df['Period 2'].sum()

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(f'<div class="kpi-card"><p style="color:#6B7280;margin:0;">📦 Segment Volume</p><h2>{int(gl_tot):,}</h2></div>', unsafe_allow_html=True)
    with k2: st.markdown(f'<div class="kpi-card"><p style="color:#6B7280;margin:0;">🏢 Active Accounts</p><h2>{working_df[dist_col].nunique()}</h2></div>', unsafe_allow_html=True)
    with k3: st.markdown(f'<div class="kpi-card"><p style="color:#6B7280;margin:0;">📍 Micro Beats</p><h2>{working_df[beat_col].nunique()}</h2></div>', unsafe_allow_html=True)
    with k4: st.markdown(f'<div class="kpi-card"><p style="color:#6B7280;margin:0;">📦 Period Delta</p><h2>{int(p2_tot - p1_tot):+,}</h2></div>', unsafe_allow_html=True)

    st.write("")

    # Visual Charts
    g_left, g_right = st.columns(2)
    with g_left:
        st.subheader("📊 Category Breakdown")
        cat_df = working_df.groupby('PrimaryCategory')['QTY'].sum().reset_index()
        fig_cat = px.pie(cat_df, values='QTY', names='PrimaryCategory', hole=0.3, template=plotly_template)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with g_right:
        st.subheader("📈 Period Trend Evaluation")
        agg_col = user_col if sel_user == "📊 Show All System Users" else dist_col
        trend_df = working_df.groupby(agg_col)[['Period 1', 'Period 2']].sum().reset_index().head(15)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=trend_df[agg_col], y=trend_df['Period 1'], name='Period 1', marker_color='#93C5FD'))
        fig_trend.add_trace(go.Bar(x=trend_df[agg_col], y=trend_df['Period 2'], name='Period 2', marker_color='#1E40AF'))
        fig_trend.update_layout(template=plotly_template, barmode='group')
        st.plotly_chart(fig_trend, use_container_width=True)

    # Data Table Display
    st.subheader("📋 Ledger Dashboard")
    styled_view = working_df[[user_col, dist_col, beat_col, 'PrimaryCategory', 'Period 1', 'Period 2', 'QTY']].copy()
    st.dataframe(styled_view, use_container_width=True)

with tab_compare:
    st.subheader("🔀 User Leaderboard")
    leaderboard = raw_df.groupby(user_col).agg(Total_Volume=('QTY', 'sum')).reset_index().sort_values(by='Total_Volume', ascending=False)
    st.table(leaderboard)
