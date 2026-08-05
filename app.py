import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Page Config
st.set_page_config(
    page_title="Sales Operations Suite",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Sales Operations Intelligence Suite")

# Data Processing Engine
def process_data(file_source):
    df = pd.read_excel(file_source, sheet_name=0)
    df.columns = df.columns.astype(str).str.strip()
    
    mapping = {}
    for col in df.columns:
        c_upper = col.upper()
        if any(k in c_upper for k in ['USER', 'REP', 'AGENT', 'NAME']):
            mapping[col] = 'USER'
        elif any(k in c_upper for k in ['DISTRIBUTOR', 'DEALER', 'CLIENT', 'STORE']):
            mapping[col] = 'Distributor'
        elif any(k in c_upper for k in ['BEAT', 'ROUTE', 'AREA', 'CITY']):
            mapping[col] = 'Beat'
        elif any(k in c_upper for k in ['QTY', 'QUANTITY', 'VOLUME', 'UNITS', 'SALE']):
            mapping[col] = 'QTY'
        elif any(k in c_upper for k in ['CATEGORY', 'PRODUCT', 'BRAND', 'ITEM']):
            mapping[col] = 'PrimaryCategory'
        elif 'PERIOD 1' in c_upper or 'P1' in c_upper:
            mapping[col] = 'Period 1'
        elif 'PERIOD 2' in c_upper or 'P2' in c_upper:
            mapping[col] = 'Period 2'
            
    df = df.rename(columns=mapping)
    
    # Categorization fallback to Heartiva
    if 'PrimaryCategory' not in df.columns:
        df['PrimaryCategory'] = 'Heartiva'
    else:
        df['PrimaryCategory'] = df['PrimaryCategory'].fillna('Heartiva')

    # Defaults for missing mapped columns
    if 'QTY' not in df.columns:
        num_cols = df.select_dtypes(include=['number']).columns
        df['QTY'] = df[num_cols[0]] if len(num_cols) > 0 else 1

    if 'USER' not in df.columns:
        df['USER'] = 'Default Rep'
    if 'Distributor' not in df.columns:
        df['Distributor'] = 'Default Distributor'
    if 'Beat' not in df.columns:
        df['Beat'] = 'Default Beat'

    if 'Period 1' not in df.columns: 
        df['Period 1'] = df['QTY'] * 0.45
    if 'Period 2' not in df.columns: 
        df['Period 2'] = df['QTY'] * 0.55
        
    df['QTY'] = pd.to_numeric(df['QTY'], errors='coerce').fillna(0)
    df['Period 1'] = pd.to_numeric(df['Period 1'], errors='coerce').fillna(0)
    df['Period 2'] = pd.to_numeric(df['Period 2'], errors='coerce').fillna(0)
    return df

# File Upload Sidebar
st.sidebar.header("📂 Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Sales Excel Sheet (.xlsx)", type=["xlsx", "xls"])

raw_df = None

if uploaded_file is not None:
    try:
        raw_df = process_data(uploaded_file)
        st.sidebar.success("🎉 Data loaded & mapped!")
    except Exception as e:
        st.error(f"Error parsing uploaded file: {e}")

elif os.path.exists("Distributer wise sale.xlsx"):
    try:
        raw_df = process_data("Distributer wise sale.xlsx")
        st.sidebar.info("ℹ️ Loaded repository default dataset.")
    except Exception as e:
        st.warning("Default Excel file in repo could not be parsed.")

# Landing view if no file uploaded
if raw_df is None:
    st.info("👋 **Welcome! Please upload your sales Excel file in the sidebar to populate the dashboard.**")
    st.stop()

# Main Dashboard View
u_opts = ["All Users"] + sorted(raw_df["USER"].astype(str).unique().tolist())
sel_user = st.selectbox("Filter by Representative:", u_opts)

working_df = raw_df.copy()
if sel_user != "All Users":
    working_df = working_df[working_df["USER"] == sel_user]

col1, col2, col3 = st.columns(3)
col1.metric("Total QTY", f"{int(working_df['QTY'].sum()):,}")
col2.metric("Distributors", working_df["Distributor"].nunique())
col3.metric("Beats", working_df["Beat"].nunique())

st.subheader("📊 Category Summary")
cat_summary = working_df.groupby('PrimaryCategory')['QTY'].sum().reset_index()
fig = px.pie(cat_summary, values='QTY', names='PrimaryCategory', hole=0.3)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 Ledger Data")
st.dataframe(working_df[['USER', 'Distributor', 'Beat', 'PrimaryCategory', 'Period 1', 'Period 2', 'QTY']], use_container_width=True)
