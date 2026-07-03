"""Recruitment Funnel page — application-to-hire conversion (simulated funnel)."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.kpi import KPICalculator
from src.sql_database import RecruitmentDatabase
from src.visualization import InteractiveCharts

st.set_page_config(page_title="Recruitment Funnel", page_icon="🔻", layout="wide")
st.title("🔻 Recruitment Funnel")
st.caption("⚠️ Application Status and funnel dates are simulated demo data (fixed random seed).")


@st.cache_data
def load_data() -> pd.DataFrame:
    db = RecruitmentDatabase()
    df = db.run_query("SELECT * FROM candidates;")
    for col in ["Application_Date", "Hire_Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


df = load_data()
charts = InteractiveCharts()

funnel_order = ["Applied", "Screened", "Interviewed", "Offered", "Hired"]
funnel_counts = pd.Series(
    {stage: (df["Application_Status"].isin(funnel_order[funnel_order.index(stage):])).sum() for stage in funnel_order}
)
st.plotly_chart(charts.funnel(funnel_counts), use_container_width=True)

kpi_calc = KPICalculator(df)
core = kpi_calc.calculate_core_kpis()
time_metrics = kpi_calc.calculate_time_metrics()

cols = st.columns(4)
cols[0].metric("Interview Conversion", f"{core['Interview_Conversion_Rate_%']}%")
cols[1].metric("Interview Pass Rate", f"{core['Interview_Pass_Rate_%']}%")
cols[2].metric("Offer Acceptance Rate", f"{core['Offer_Acceptance_Rate_%']}%")
cols[3].metric("Time to Fill (days)", time_metrics["Time_to_Fill_Days"])

st.subheader("Status Breakdown")
st.plotly_chart(charts.bar(df["Application_Status"].value_counts(), "Candidates by Status"), use_container_width=True)
