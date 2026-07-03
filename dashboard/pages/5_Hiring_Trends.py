"""Hiring Trends page — time-series trends and department comparisons."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.sql_database import RecruitmentDatabase
from src.visualization import InteractiveCharts

st.set_page_config(page_title="Hiring Trends", page_icon="📅", layout="wide")
st.title("📅 Hiring Trends")


@st.cache_data
def load_data() -> pd.DataFrame:
    db = RecruitmentDatabase()
    df = db.run_query("SELECT * FROM candidates;")
    for col in ["Application_Date", "Hire_Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


df = load_data()
charts = InteractiveCharts()

monthly_apps = df["Application_Date"].dt.to_period("M").astype(str).value_counts().sort_index()
st.plotly_chart(charts.line(monthly_apps, "Monthly Applications Over Time"), use_container_width=True)

hired = df[df["Application_Status"] == "Hired"]
monthly_hires = hired["Hire_Date"].dt.to_period("M").astype(str).value_counts().sort_index()
st.plotly_chart(charts.line(monthly_hires, "Monthly Hires Over Time"), use_container_width=True)

st.subheader("Department Hiring Comparison")
dept_hires = df.groupby("Department").apply(lambda g: (g["Application_Status"] == "Hired").sum())
st.plotly_chart(charts.bar(dept_hires.sort_values(ascending=False), "Hires by Department"), use_container_width=True)
