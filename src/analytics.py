"""
analytics.py
------------
Exploratory Data Analysis: generates the insight tables that back the
charts in visualization.py and the Streamlit dashboard.

Author: Recruitment Analytics Team
"""

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)


class RecruitmentAnalytics:
    """Generates EDA insight tables from the engineered candidate dataset."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    def applications_by_job_role(self, top_n: int = 15) -> pd.Series:
        return self.df["Job Roles"].value_counts().head(top_n)

    def applications_by_source(self) -> pd.Series:
        return self.df["Hiring_Source"].value_counts()

    def applications_by_gender(self) -> pd.Series:
        return self.df["Gender"].value_counts()

    def applications_by_education(self) -> pd.Series:
        return self.df["Education"].value_counts()

    def applications_by_experience(self) -> pd.Series:
        return self.df["Experience_Level"].value_counts()

    def salary_distribution(self) -> pd.Series:
        return self.df["Salary_Offered"].dropna()

    def monthly_applications(self) -> pd.Series:
        return (
            self.df["Application_Date"]
            .dt.to_period("M")
            .value_counts()
            .sort_index()
        )

    def hiring_trend(self) -> pd.Series:
        hired = self.df[self.df["Application_Status"] == "Hired"]
        return hired["Hire_Date"].dt.to_period("M").value_counts().sort_index()

    def top_skills(self, top_n: int = 15) -> pd.Series:
        all_skills = (
            self.df["Skills"]
            .str.split(",")
            .explode()
            .str.strip()
        )
        return all_skills.value_counts().head(top_n)

    def top_cities(self, top_n: int = 10) -> pd.Series:
        return self.df["City"].value_counts().head(top_n)

    def age_distribution(self) -> pd.Series:
        return self.df["Age"]

    def correlation_matrix(self) -> pd.DataFrame:
        numeric_cols = self.df.select_dtypes(include="number")
        return numeric_cols.corr()

    def generate_all_insights(self) -> dict:
        """Run every EDA function and return a dict of results (for logging/reporting)."""
        insights = {
            "applications_by_job_role": self.applications_by_job_role(),
            "applications_by_source": self.applications_by_source(),
            "applications_by_gender": self.applications_by_gender(),
            "applications_by_education": self.applications_by_education(),
            "applications_by_experience": self.applications_by_experience(),
            "monthly_applications": self.monthly_applications(),
            "hiring_trend": self.hiring_trend(),
            "top_skills": self.top_skills(),
            "top_cities": self.top_cities(),
        }
        logger.info("EDA Complete | %d insight tables generated", len(insights))
        return insights
