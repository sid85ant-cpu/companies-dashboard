import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px

# Page setup

st.markdown("## 📊 Companies Analytics Dashboard")
st.write("This dashboard explores company distribution across sectors, countries, and expense presentation types.")

# Load data
# --- DATABASE CONNECTION ---
import os

@st.cache_data
def load_data():
    conn = psycopg2.connect(os.getenv("DB_URL"))

    query = "SELECT * FROM companies_staging;"
    df = pd.read_sql(query, conn)
    conn.close()

    df.columns = df.columns.str.strip().str.lower()
    return df

df = load_data()


# Clean column names (important)
df.columns = df.columns.str.strip().str.lower()
# Sidebar filters
st.sidebar.header("Filters")

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
col1, col2, col3 = st.columns(3)

col1.metric("Total Companies", filtered_df["cid"].nunique())
col2.metric("Total Countries", filtered_df["country"].nunique())
col3.metric("Total Sectors", filtered_df["sector"].nunique())

st.divider()

# Charts
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

# Expense type chart
expense_chart = px.pie(
    filtered_df,
    names="expense_type",
    title="Expense Type Distribution"
)
st.plotly_chart(expense_chart, use_container_width=True)

# Table
st.subheader("📋 Data Table")
st.dataframe(filtered_df)
