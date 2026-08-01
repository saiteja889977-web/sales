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
    # Reads the uploaded excel file
    df = pd.read_excel("Distributer wise sale.xlsx", sheet_name="Sheet1")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading file: Ensure 'Distributer wise sale.xlsx' is in the same folder as this script.")
    st.stop()

# 4. Header Section
st.markdown('<div class="main-title">📊 Distributor Wise Sales Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Interactive reporting tool for sales overview, filters, metrics, and breakdowns.</div>', unsafe_allow_html=True)

# 5. Sidebar Filters
st.sidebar.header("🎯 Filter Options")

# Search / Filter by User
user_list = ["All Users"] + sorted(df["USER"].dropna().unique().tolist())
selected_user = st.sidebar.selectbox("Filter by Sales Representative (USER)", user_list)

# Filter by Distributor
dist_list = ["All Distributors"] + sorted(df["Distributor"].dropna().unique().tolist())
selected_dist = st.sidebar.selectbox("Filter by Distributor", dist_list)

# Filter by Beat
beat_list = ["All Beats"] + sorted(df["Beat"].dropna().unique().tolist())
selected_beat = st.sidebar.selectbox("Filter by Beat", beat_list)

# Apply filters sequentially
filtered_df = df.copy()
if selected_user != "All Users":
    filtered_df = filtered_df[filtered_df["USER"] == selected_user]
if selected_dist != "All Distributors":
    filtered_df = filtered_df[filtered_df["Distributor"] == selected_dist]
if selected_beat != "All Beats":
    filtered_df = filtered_df[filtered_df["Beat"] == selected_beat]

# 6. Top Level Performance Metrics (KPI Cards)
total_qty = int(filtered_df["QTY"].sum())
unique_dists = filtered_df["Distributor"].nunique()
unique_beats = filtered_df["Beat"].nunique()
unique_users = filtered_df["USER"].nunique()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Order Qty", f"{total_qty:,}")
with col2:
    st.metric("Active Distributors", unique_dists)
with col3:
    st.metric("Covered Beats", unique_beats)
with col4:
    st.metric("Sales Users", unique_users)

st.markdown("---")

# 7. Layout Split: Charts & Tables
chart_col, table_col = st.columns([1.1, 0.9])

with chart_col:
    st.subheader("📈 Top Distributors by Sales Quantity")
    # Group by Distributor for visualization
    dist_summary = filtered_df.groupby("Distributor")["QTY"].sum().reset_index()
    dist_summary = dist_summary.sort_values(by="QTY", ascending=False).head(10)
    
    if not dist_summary.empty:
        fig = px.bar(
            dist_summary, 
            x="QTY", 
            y="Distributor", 
            orientation='h',
            text="QTY",
            color="QTY",
            color_continuous_scale="Blues",
            labels={"QTY": "Total Quantity (Units)"}
        )
        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the chosen filters.")

with table_col:
    st.subheader("👥 Sales Rep Breakdown")
    user_summary = filtered_df.groupby("USER")["QTY"].sum().reset_index()
    user_summary = user_summary.sort_values(by="QTY", ascending=False)
    st.dataframe(user_summary, use_container_width=True, height=400, hide_index=True)

st.markdown("---")

# 8. Complete Filtered Data Table View
st.subheader("📋 Detailed Breakdown Ledger")
st.markdown("Use the global search below to immediately filter any text row dynamically.")

# Let's show clean column view (identifying primary text columns + total quantity)
columns_to_show = ["USER", "Distributor", "Beat", "FIRST", "SECOND", "THIRD", "FOURTH", "QTY"]
# Filter columns list dynamically based on availability
columns_to_show = [c for c in columns_to_show if c in filtered_df.columns]

st.dataframe(
    filtered_df[columns_to_show + [col for col in filtered_df.columns if col not in columns_to_show and filtered_df[col].sum() > 0]], 
    use_container_width=True
)

# 9. Download Option
st.sidebar.markdown("---")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="📥 Download Filtered CSV Data",
    data=csv,
    file_name='Filtered_Sales_Report.csv',
    mime='text/csv',
)
