"""Executive Dashboard page — high-level KPI overview for leadership."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.kpi import KPICalculator
from src.sql_database import RecruitmentDatabase
from src.visualization import InteractiveCharts

st.set_page_config(page_title="Executive Dashboard", page_icon="📈", layout="wide")
st.title("📈 Executive Dashboard")


@st.cache_data
def load_data() -> pd.DataFrame:
    db = RecruitmentDatabase()
    df = db.run_query("SELECT * FROM candidates;")
    for col in ["Application_Date", "Hire_Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


df = load_data()
kpi_calc = KPICalculator(df)
core = kpi_calc.calculate_core_kpis()
time_metrics = kpi_calc.calculate_time_metrics()

cols = st.columns(4)
cols[0].metric("Applications", f"{core['Applications_Received']:,}")
cols[1].metric("Hiring Rate", f"{core['Hiring_Rate_%']}%")
cols[2].metric("Avg Salary Offered", f"₹{core['Average_Salary_Offered']:,.0f}")
cols[3].metric("Time to Hire (days)", time_metrics["Time_to_Hire_Days"])

charts = InteractiveCharts()
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(charts.bar(df["Department"].value_counts(), "Applications by Department"), use_container_width=True)
with c2:
    monthly = df["Application_Date"].dt.to_period("M").astype(str).value_counts().sort_index()
    st.plotly_chart(charts.line(monthly, "Monthly Application Volume"), use_container_width=True)

st.caption("⚠️ Department, salary, and dates are simulated demo fields — see README for details.")
