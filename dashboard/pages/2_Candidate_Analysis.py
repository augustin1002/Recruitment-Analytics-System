"""Candidate Analysis page — demographics, education, skills, resume scores."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from src.sql_database import RecruitmentDatabase
from src.visualization import InteractiveCharts

st.set_page_config(page_title="Candidate Analysis", page_icon="🧑‍🤝‍🧑", layout="wide")
st.title("🧑‍🤝‍🧑 Candidate Analysis")
st.caption("Education, Skills, Certifications, and Experience Level below are extracted from real resume text.")


@st.cache_data
def load_data() -> pd.DataFrame:
    db = RecruitmentDatabase()
    return db.run_query("SELECT * FROM candidates;")


df = load_data()
charts = InteractiveCharts()

c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(charts.pie(df["Education"].value_counts(), "Education Distribution"), use_container_width=True)
with c2:
    st.plotly_chart(charts.pie(df["Experience_Level"].value_counts(), "Experience Level Distribution"), use_container_width=True)

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(charts.histogram(df["Age"], "Age Distribution"), use_container_width=True)
with c4:
    st.plotly_chart(charts.histogram(df["Resume_Score"], "Resume Score Distribution"), use_container_width=True)

st.subheader("Top Skills")
top_skills = df["Skills"].str.split(",").explode().str.strip().value_counts().head(20)
st.plotly_chart(charts.bar(top_skills, "Top 20 Skills Across Candidates"), use_container_width=True)

st.subheader("Top Cities (simulated)")
st.plotly_chart(charts.bar(df["City"].value_counts(), "Applications by City"), use_container_width=True)
