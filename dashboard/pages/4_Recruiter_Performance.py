"""Recruiter Performance page — hires and conversion by recruiter (simulated)."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.kpi import KPICalculator
from src.sql_database import RecruitmentDatabase
from src.visualization import InteractiveCharts

st.set_page_config(page_title="Recruiter Performance", page_icon="🧑‍💼", layout="wide")
st.title("🧑‍💼 Recruiter Performance")
st.caption("⚠️ Recruiter names are simulated demo data.")


@st.cache_data
def load_data() -> pd.DataFrame:
    db = RecruitmentDatabase()
    return db.run_query("SELECT * FROM candidates;")


df = load_data()
kpi_calc = KPICalculator(df)
rec_perf = kpi_calc.recruiter_performance()
charts = InteractiveCharts()

st.dataframe(rec_perf, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(
        charts.bar(rec_perf.set_index("Recruiter")["Hires"], "Hires by Recruiter"),
        use_container_width=True,
    )
with c2:
    st.plotly_chart(
        charts.bar(rec_perf.set_index("Recruiter")["Hire_Rate_%"], "Hire Rate % by Recruiter"),
        use_container_width=True,
    )

st.subheader("Hiring Source Performance")
source_perf = kpi_calc.hiring_source_performance()
st.dataframe(source_perf, use_container_width=True)
st.plotly_chart(charts.pie(df["Hiring_Source"].value_counts(), "Applications by Hiring Source"), use_container_width=True)
