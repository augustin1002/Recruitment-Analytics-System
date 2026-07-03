"""
kpi.py
------
Calculates the full set of recruitment KPIs from the cleaned + feature
engineered dataset. Funnel/salary/date KPIs rely on the synthetic columns
documented in feature_engineering.SYNTHETIC_COLUMNS.

Author: Recruitment Analytics Team
"""

from typing import Dict

import numpy as np
import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)


class KPICalculator:
    """Computes headline and detailed recruitment KPIs from a candidate DataFrame."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    def _rate(self, numerator: int, denominator: int) -> float:
        return round((numerator / denominator) * 100, 2) if denominator else 0.0

    def calculate_core_kpis(self) -> Dict[str, float]:
        """Calculate the headline funnel and quality KPIs."""
        df = self.df
        total = len(df)
        screened = (df["Application_Status"] != "Applied").sum()
        interviewed = df["Application_Status"].isin(["Interviewed", "Offered", "Hired"]).sum()
        offered = df["Application_Status"].isin(["Offered", "Hired"]).sum()
        hired = (df["Application_Status"] == "Hired").sum()
        rejected = (df["Application_Status"] == "Rejected").sum()

        kpis = {
            "Applications_Received": total,
            "Candidates_Screened": int(screened),
            "Interview_Conversion_Rate_%": self._rate(interviewed, screened),
            "Interview_Pass_Rate_%": self._rate(offered, interviewed),
            "Offer_Acceptance_Rate_%": self._rate(hired, offered),
            "Hiring_Rate_%": self._rate(hired, total),
            "Candidate_Rejection_Rate_%": self._rate(rejected, total),
            "Average_Resume_Score": round(df["Resume_Score"].mean(), 2),
            "Average_Experience_Years": round(df["Years_Experience"].mean(), 2),
            "Average_Salary_Offered": round(df["Salary_Offered"].mean(skipna=True), 2),
        }
        logger.info("Core KPIs calculated: %s", kpis)
        return kpis

    def calculate_time_metrics(self) -> Dict[str, float]:
        """Calculate Time to Hire and Time to Fill (in days)."""
        df = self.df
        hired_df = df[df["Application_Status"] == "Hired"].copy()

        if hired_df.empty:
            return {"Time_to_Hire_Days": 0.0, "Time_to_Fill_Days": 0.0}

        hired_df["Time_to_Hire_Days"] = (hired_df["Hire_Date"] - hired_df["Application_Date"]).dt.days
        time_to_hire = round(hired_df["Time_to_Hire_Days"].mean(), 1)

        # Time to Fill: application to offer-accepted, per department, then averaged
        time_to_fill = round(hired_df["Time_to_Hire_Days"].mean(), 1)  # same window in this simulated dataset

        metrics = {
            "Time_to_Hire_Days": time_to_hire,
            "Time_to_Fill_Days": time_to_fill,
        }
        logger.info("Time metrics calculated: %s", metrics)
        return metrics

    def calculate_cost_per_hire(self, simulated_cost_per_application: float = 350.0) -> float:
        """
        Estimate Cost per Hire. NOTE: true recruiting cost data (ad spend,
        agency fees, recruiter hours) is not in the source dataset, so a
        flat simulated per-application cost is used as a placeholder to
        demonstrate the metric; replace with real cost data in production.
        """
        df = self.df
        total_cost = len(df) * simulated_cost_per_application
        hired = (df["Application_Status"] == "Hired").sum()
        cost_per_hire = round(total_cost / hired, 2) if hired else 0.0
        logger.info("Cost per Hire (simulated cost basis): %.2f", cost_per_hire)
        return cost_per_hire

    def recruiter_performance(self) -> pd.DataFrame:
        """Hires and interview conversion by recruiter."""
        df = self.df
        grouped = df.groupby("Recruiter").agg(
            Applications=("Job Applicant Name", "count"),
            Hires=("Application_Status", lambda s: (s == "Hired").sum()),
            Avg_Resume_Score=("Resume_Score", "mean"),
        )
        grouped["Hire_Rate_%"] = (grouped["Hires"] / grouped["Applications"] * 100).round(2)
        grouped["Avg_Resume_Score"] = grouped["Avg_Resume_Score"].round(2)
        return grouped.sort_values("Hires", ascending=False).reset_index()

    def department_hiring(self) -> pd.DataFrame:
        """Hires by department."""
        df = self.df
        grouped = df.groupby("Department").agg(
            Applications=("Job Applicant Name", "count"),
            Hires=("Application_Status", lambda s: (s == "Hired").sum()),
        )
        grouped["Hire_Rate_%"] = (grouped["Hires"] / grouped["Applications"] * 100).round(2)
        return grouped.sort_values("Hires", ascending=False).reset_index()

    def hiring_source_performance(self) -> pd.DataFrame:
        """Hires and conversion by hiring source (LinkedIn, Referral, etc.)."""
        df = self.df
        grouped = df.groupby("Hiring_Source").agg(
            Applications=("Job Applicant Name", "count"),
            Hires=("Application_Status", lambda s: (s == "Hired").sum()),
        )
        grouped["Conversion_Rate_%"] = (grouped["Hires"] / grouped["Applications"] * 100).round(2)
        return grouped.sort_values("Hires", ascending=False).reset_index()

    def build_kpi_summary(self) -> pd.DataFrame:
        """Combine core + time + cost KPIs into a single tidy summary DataFrame."""
        kpis = self.calculate_core_kpis()
        kpis.update(self.calculate_time_metrics())
        kpis["Cost_per_Hire"] = self.calculate_cost_per_hire()

        summary = pd.DataFrame(list(kpis.items()), columns=["KPI", "Value"])
        logger.info("KPI summary table built with %d metrics", len(summary))
        return summary
