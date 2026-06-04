import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Page setup


st.set_page_config(layout="wide")

st.title("📊 CopEx PAD Analystics Dashbpard (Companies OpEx Presentation and Disclosures Analytics Dashboard")

st.markdown("""
**Executive Overview:**  
This dashboard provides a high-level analysis of sample company distribution across sectors, geographies, and expense presentation and disclosure structures.
""")
# --- DATABASE CONNECTION ---
import os

@st.cache_data
def load_data():
    try:
        
        conn = psycopg2.connect(
            os.getenv("DB_URL"),
            sslmode="require"
        )


        query = "SELECT * FROM companies_staging;"
        df = pd.read_sql(query, conn)
        conn.close()

        df.columns = df.columns.str.strip().str.lower()
        return df

    except Exception as e:
        st.error(f"DB ERROR: {e}")
        return pd.DataFrame()

df = load_data()

# Clean column names (important)
df.columns = df.columns.str.strip().str.lower()

# Sidebar filters
st.sidebar.header("🎛️ Filters")

country_filter = st.sidebar.multiselect(
    "Select Country",
    options=df["country"].dropna().unique(),
    default=df["country"].dropna().unique()
)

sector_filter = st.sidebar.multiselect(
    "Select Sector",
    options=df["sector"].dropna().unique(),
    default=df["sector"].dropna().unique()
)

expense_filter = st.sidebar.multiselect(
    "Select Expense Type",
    options=df["expense_type"].dropna().unique(),
    default=df["expense_type"].dropna().unique()
)

# Filter data
filtered_df = df[
    (df["country"].isin(country_filter)) &
    (df["sector"].isin(sector_filter)) &
    (df["expense_type"].isin(expense_filter))
]

# KPIs
st.markdown("## 📌 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Companies", filtered_df["cid"].nunique())
col2.metric("Countries", filtered_df["country"].nunique())
col3.metric("Sectors", filtered_df["sector"].nunique())
col4.metric("Expense Types", filtered_df["expense_type"].nunique())

st.divider()

top_sector = filtered_df["sector"].value_counts().idxmax()
top_country = filtered_df["country"].value_counts().idxmax()

st.markdown(f"""

## 🔎 Key Insights

- The most represented **sector** is **{top_sector}**
- The highest concentration of companies is in **{top_country}**
- This suggests clustering in specific industries and regions
""")

st.markdown("## 📊 Distribution Analysis")

col4, col5 = st.columns(2)

with col4:
    sector_chart = px.bar(
        filtered_df["sector"].value_counts().reset_index(),
        x="count",
        y="sector",
        orientation="h",
        title="Companies by Sector"
    )
    st.plotly_chart(sector_chart, use_container_width=True)

with col5:
    country_chart = px.bar(
        filtered_df["country"].value_counts().reset_index(),
        x="count",
        y="country",
        orientation="h",
        title="Companies by Country"
    )
    st.plotly_chart(country_chart, use_container_width=True)


st.markdown("## 💰 Expense Structure")

expense_chart = px.pie(
    filtered_df,
    names="expense_type",
    title="Expense Type Distribution"
)


# Table
st.markdown("## 📋 Detailed Data")
st.dataframe(filtered_df, use_container_width=True)
