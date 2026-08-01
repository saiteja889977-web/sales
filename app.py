import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Distributor Wise Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS to style like a premium modern application
st.markdown("""
    <style>
    .main-title {
        font-size: 38px; color: #1E3A8A; font-weight: bold; margin-bottom: 5px;
    }
    .sub-title {
        font-size: 16px; color: #6B7280; margin-bottom: 25px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 28px; font-weight: bold; color: #0F766E;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Load and Cache the Data
@st.cache_data
def load_data():
    df = pd.read_excel("Distributer wise sale.xlsx", sheet_name="Sheet1")
    # Automatically clean up column names (remove hidden spaces and make uppercase for consistency)
    df.columns = df.columns.astype(str).str.strip()
    
    # Standardize column naming just in case it's lowercase in the sheet
    mapping = {}
    for col in df.columns:
        if col.upper() == 'USER': mapping[col] = 'USER'
        elif col.upper() == 'DISTRIBUTOR': mapping[col] = 'Distributor'
        elif col.upper() == 'BEAT': mapping[col] = 'Beat'
        elif col.upper() == 'QTY': mapping[col] = 'QTY'
    df = df.rename(columns=mapping)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading file: Ensure 'Distributer wise sale.xlsx' is in the same folder as this script. Details: {e}")
    st.stop()

# 4. Header Section
st.markdown('<div class="main-title">📊 Distributor Wise Sales Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive reporting tool for sales overview, filters, metrics, and breakdowns.</div>', unsafe_allow_html=True)

# 5. Sidebar Filters
st.sidebar.header("🎯 Filter Options")

# Safely check if core columns exist, otherwise fall back to whatever columns are available
user_col = "USER" if "USER" in df.columns else df.columns[0]
dist_col = "Distributor" if "Distributor" in df.columns else df.columns[1] if len(df.columns) > 1 else df.columns[0]
beat_col = "Beat" if "Beat" in df.columns else df.columns[2] if len(df.columns) > 2 else df.columns[0]
qty_col = "QTY" if "QTY" in df.columns else df.columns[-1]

# Build dropdown filters dynamically
user_list = ["All Users"] + sorted(df[user_col].dropna().unique().tolist())
selected_user = st.sidebar.selectbox(f"Filter by User ({user_col})", user_list)

dist_list = ["All Distributors"] + sorted(df[dist_col].dropna().unique().tolist())
selected_dist = st.sidebar.selectbox(f"Filter by Distributor ({dist_col})", dist_list)

beat_list = ["All Beats"] + sorted(df[beat_col].dropna().unique().tolist())
selected_beat = st.sidebar.selectbox(f"Filter by Beat ({beat_col})", beat_list)

# Apply filters sequentially
filtered_df = df.copy()
if selected_user != "All Users":
    filtered_df = filtered_df[filtered_df[user_col] == selected_user]
if selected_dist != "All Distributors":
    filtered_df = filtered_df[filtered_df[dist_col] == selected_dist]
if selected_beat != "All Beats":
    filtered_df = filtered_df[filtered_df[beat_col] == selected_beat]

# 6. Top Level Performance Metrics (KPI Cards)
# Try to sum the numeric columns safely
try:
    total_qty = int(pd.to_numeric(filtered_df[qty_col], errors='coerce').sum())
except:
    total_qty = len(filtered_df)

unique_dists = filtered_df[dist_col].nunique()
unique_beats = filtered_df[beat_col].nunique()
unique_users = filtered_df[user_col].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Order Volume", f"{total_qty:,}")
with col2:
    st.metric("Active Distributors", unique_dists)
with col3:
    st.metric("Covered Beats", unique_beats)
with col4:
    st.metric("Unique Sales Reps", unique_users)

st.markdown("---")

# 7. Layout Split: Charts & Tables
chart_col, table_col = st.columns([1.1, 0.9])

with chart_col:
    st.subheader("📈 Top Distribution Points")
    try:
        dist_summary = filtered_df.groupby(dist_col)[qty_col].sum().reset_index()
        dist_summary = dist_summary.sort_values(by=qty_col, ascending=False).head(10)
        
        if not dist_summary.empty:
            fig = px.bar(
                dist_summary, 
                x=qty_col, 
                y=dist_col, 
                orientation='h',
                text=qty_col,
                color=qty_col,
                color_continuous_scale="Blues",
                labels={qty_col: "Total Sales Volume"}
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data matching current criteria.")
    except Exception as e:
        st.info("Select standard numerical columns to display visual graphs.")

with table_col:
    st.subheader("👥 Sales Rep Breakdown")
    try:
        user_summary = filtered_df.groupby(user_col)[qty_col].sum().reset_index()
        user_summary = user_summary.sort_values(by=qty_col, ascending=False)
        st.dataframe(user_summary, use_container_width=True, height=400, hide_index=True)
    except:
        st.dataframe(filtered_df[[user_col]].value_counts().reset_index(), use_container_width=True, height=400)

st.markdown("---")

# 8. Complete Filtered Data Table View
st.subheader("📋 Detailed Breakdown Ledger")
st.dataframe(filtered_df, use_container_width=True)

# 9. Download Option
st.sidebar.markdown("---")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Download Filtered CSV Data",
    data=csv,
    file_name='Filtered_Sales_Report.csv',
    mime='text/csv',
)
