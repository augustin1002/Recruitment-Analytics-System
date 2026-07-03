"""
app.py
------
Recruitment Analytics — Executive Dashboard (Streamlit entry point).

Run with:
    streamlit run dashboard/app.py

Author: Recruitment Analytics Team
"""

import sys
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.kpi import KPICalculator
from src.sql_database import RecruitmentDatabase
from src.utils import Paths
from src.visualization import InteractiveCharts

st.set_page_config(
    page_title="Recruitment Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Data loading (cached)
# ----------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    db = RecruitmentDatabase()
    df = db.run_query("SELECT * FROM candidates;")
    for col in ["Application_Date", "Screening_Date", "Interview_Date", "Offer_Date", "Hire_Date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


df = load_data()

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.title("🔎 Filters")
st.sidebar.caption(
    "⚠️ Department, Recruiter, Hiring Source, dates, Salary, and Resume Score "
    "are **simulated demo data** (fixed seed) — the source dataset had no "
    "recruitment funnel. Education, Skills, Certifications, and Experience "
    "Level are extracted from real resume text."
)

job_roles = st.sidebar.multiselect("Job Role", sorted(df["Job Roles"].unique()))
departments = st.sidebar.multiselect("Department", sorted(df["Department"].unique()))
experience_levels = st.sidebar.multiselect("Experience Level", sorted(df["Experience_Level"].unique()))
genders = st.sidebar.multiselect("Gender", sorted(df["Gender"].unique()))

min_date, max_date = df["Application_Date"].min(), df["Application_Date"].max()
date_range = st.sidebar.date_input("Application Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

filtered = df.copy()
if job_roles:
    filtered = filtered[filtered["Job Roles"].isin(job_roles)]
if departments:
    filtered = filtered[filtered["Department"].isin(departments)]
if experience_levels:
    filtered = filtered[filtered["Experience_Level"].isin(experience_levels)]
if genders:
    filtered = filtered[filtered["Gender"].isin(genders)]
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[(filtered["Application_Date"] >= start) & (filtered["Application_Date"] <= end)]

st.sidebar.markdown("---")
st.sidebar.metric("Filtered Candidates", len(filtered))

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("📊 Recruitment Analytics — Executive Dashboard")
st.caption(
    "Data source: `job_applicant_dataset.csv` (10,000 candidates) · "
    "Real fields: Name, Age, Gender, Race, Ethnicity, Resume, Job Roles, Best Match, "
    "plus Education/Skills/Certifications/Experience Level extracted from resume text · "
    "Simulated fields: Department, Recruiter, Hiring Source, City, funnel dates, Application Status, "
    "Salary Offered, Resume Score, Years of Experience."
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ----------------------------------------------------------------------
# Executive KPI cards
# ----------------------------------------------------------------------
kpi_calc = KPICalculator(filtered)
core = kpi_calc.calculate_core_kpis()
time_metrics = kpi_calc.calculate_time_metrics()
cost_per_hire = kpi_calc.calculate_cost_per_hire()

row1 = st.columns(5)
row1[0].metric("Applications", f"{core['Applications_Received']:,}")
row1[1].metric("Screened", f"{core['Candidates_Screened']:,}")
row1[2].metric("Interview Conversion", f"{core['Interview_Conversion_Rate_%']}%")
row1[3].metric("Offer Acceptance", f"{core['Offer_Acceptance_Rate_%']}%")
row1[4].metric("Hiring Rate", f"{core['Hiring_Rate_%']}%")

row2 = st.columns(5)
row2[0].metric("Avg Resume Score", core["Average_Resume_Score"])
row2[1].metric("Avg Experience (yrs)", core["Average_Experience_Years"])
row2[2].metric("Avg Salary Offered", f"₹{core['Average_Salary_Offered']:,.0f}")
row2[3].metric("Time to Hire (days)", time_metrics["Time_to_Hire_Days"])
row2[4].metric("Cost per Hire (sim.)", f"₹{cost_per_hire:,.0f}")

st.markdown("---")

# ----------------------------------------------------------------------
# Charts
# ----------------------------------------------------------------------
charts = InteractiveCharts()

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(charts.bar(filtered["Job Roles"].value_counts().head(10), "Top 10 Job Roles by Applications"), use_container_width=True)
with c2:
    st.plotly_chart(charts.pie(filtered["Hiring_Source"].value_counts(), "Applications by Hiring Source"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(charts.pie(filtered["Gender"].value_counts(), "Applications by Gender"), use_container_width=True)
with c4:
    st.plotly_chart(charts.bar(filtered["Education"].value_counts(), "Applications by Education"), use_container_width=True)

c5, c6 = st.columns(2)
with c5:
    monthly = filtered["Application_Date"].dt.to_period("M").astype(str).value_counts().sort_index()
    st.plotly_chart(charts.line(monthly, "Monthly Applications"), use_container_width=True)
with c6:
    hired = filtered[filtered["Application_Status"] == "Hired"]
    hiring_trend = hired["Hire_Date"].dt.to_period("M").astype(str).value_counts().sort_index()
    st.plotly_chart(charts.line(hiring_trend, "Hiring Trend"), use_container_width=True)

st.subheader("🔻 Hiring Funnel")
funnel_order = ["Applied", "Screened", "Interviewed", "Offered", "Hired"]
funnel_counts = pd.Series(
    {stage: (filtered["Application_Status"].isin(funnel_order[funnel_order.index(stage):])).sum() for stage in funnel_order}
)
st.plotly_chart(charts.funnel(funnel_counts), use_container_width=True)

c7, c8 = st.columns(2)
with c7:
    st.plotly_chart(charts.histogram(filtered["Salary_Offered"].dropna(), "Salary Distribution"), use_container_width=True)
with c8:
    st.plotly_chart(charts.histogram(filtered["Age"], "Age Distribution"), use_container_width=True)

c9, c10 = st.columns(2)
with c9:
    st.plotly_chart(
        charts.scatter(filtered.dropna(subset=["Salary_Offered"]), "Years_Experience", "Salary_Offered", "Experience_Level", "Experience vs Salary"),
        use_container_width=True,
    )
with c10:
    numeric_df = filtered.select_dtypes(include="number")
    st.plotly_chart(charts.heatmap(numeric_df.corr()), use_container_width=True)

st.subheader("🛠️ Top Skills")
top_skills = filtered["Skills"].str.split(",").explode().str.strip().value_counts().head(15)
st.plotly_chart(charts.bar(top_skills, "Top 15 Skills"), use_container_width=True)

st.subheader("🧑‍💼 Recruiter Performance")
rec_perf = KPICalculator(filtered).recruiter_performance()
st.dataframe(rec_perf, use_container_width=True)

# ----------------------------------------------------------------------
# Downloads
# ----------------------------------------------------------------------
st.markdown("---")
st.subheader("⬇️ Export Filtered Data")

dl1, dl2 = st.columns(2)
with dl1:
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", data=csv_bytes, file_name="filtered_candidates.csv", mime="text/csv")

with dl2:
    excel_buffer = BytesIO()
    filtered.to_excel(excel_buffer, index=False, engine="openpyxl")
    st.download_button(
        "Download Excel",
        data=excel_buffer.getvalue(),
        file_name="filtered_candidates.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.caption("Built with Python, Pandas, SQLAlchemy, Plotly, and Streamlit · Recruitment Analytics System")
