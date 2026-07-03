"""
feature_engineering.py
-----------------------
Two responsibilities, kept deliberately separate:

1. REAL feature extraction from the 'Resume' free text column
   (Education, Skills, Certifications, Experience Level) — genuine
   signal parsed from the source data.

2. SYNTHETIC recruitment-funnel augmentation (Department, Recruiter,
   Hiring Source, funnel dates, Application Status, Salary Offered,
   Resume Score, City, Years of Experience) — generated with a fixed
   random seed because the source dataset does not contain a real
   recruitment funnel. Every synthetic column is listed explicitly in
   SYNTHETIC_COLUMNS and flagged in the dashboard and README so nobody
   mistakes it for real hiring data.

Author: Recruitment Analytics Team
"""

import re
from typing import List

import numpy as np
import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

RANDOM_SEED = 42

# Columns that are SIMULATED for demo purposes because the raw dataset
# does not include a real recruitment funnel or compensation data.
SYNTHETIC_COLUMNS: List[str] = [
    "Department",
    "Recruiter",
    "Hiring_Source",
    "City",
    "Application_Date",
    "Screening_Date",
    "Interview_Date",
    "Offer_Date",
    "Hire_Date",
    "Application_Status",
    "Salary_Offered",
    "Resume_Score",
    "Years_Experience",
]

DEPARTMENTS = ["Engineering", "Sales", "Marketing", "Finance", "Operations", "Healthcare", "HR", "Customer Support"]
RECRUITERS = ["Aisha Khan", "David Lee", "Priya Nair", "Carlos Mendes", "Emma Wilson", "Ravi Shankar", "Lena Fischer"]
HIRING_SOURCES = ["LinkedIn", "Referral", "Job Portal", "Career Fair", "Company Website", "Recruitment Agency"]
CITIES = ["Chennai", "Bangalore", "Coimbatore", "Mumbai", "Hyderabad", "Pune", "Delhi", "Remote"]
STATUS_FLOW = ["Applied", "Screened", "Interviewed", "Offered", "Hired", "Rejected"]

EDU_PATTERN = re.compile(r"Holds an?\s+([A-Za-z]+)\s+degree", re.IGNORECASE)
CERT_PATTERN = re.compile(r"certifications such as (.+?)\.\s", re.IGNORECASE)
LEVEL_PATTERN = re.compile(r"with\s+([a-zA-Z\-]+)-level experience", re.IGNORECASE)
SKILLS_PATTERN = re.compile(r"Proficient in (.+?), with", re.IGNORECASE)


class FeatureEngineer:
    """Extracts real resume-based features and appends synthetic demo data."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()
        self._rng = np.random.default_rng(RANDOM_SEED)

    # ------------------------------------------------------------------
    # REAL features parsed from Resume text
    # ------------------------------------------------------------------
    def extract_education(self) -> "FeatureEngineer":
        """Extract highest stated degree from the Resume text (real data)."""
        self.df["Education"] = self.df["Resume"].apply(
            lambda text: (EDU_PATTERN.search(text).group(1).title() if EDU_PATTERN.search(text) else "Unknown")
        )
        logger.info("Extracted Education from resume text | levels=%s", sorted(self.df["Education"].unique().tolist()))
        return self

    def extract_experience_level(self) -> "FeatureEngineer":
        """Extract stated experience level (Entry/Mid/Senior) (real data)."""
        self.df["Experience_Level"] = self.df["Resume"].apply(
            lambda text: (LEVEL_PATTERN.search(text).group(1).title() if LEVEL_PATTERN.search(text) else "Unknown")
        )
        logger.info("Extracted Experience_Level from resume text")
        return self

    def extract_skills(self) -> "FeatureEngineer":
        """Extract the comma-separated skill list stated in the resume (real data)."""
        def parse_skills(text: str) -> str:
            match = SKILLS_PATTERN.search(text)
            return match.group(1).strip() if match else "Unspecified"

        self.df["Skills"] = self.df["Resume"].apply(parse_skills)
        logger.info("Extracted Skills column from resume text")
        return self

    def extract_certifications(self) -> "FeatureEngineer":
        """Extract stated certifications from the resume (real data)."""
        def parse_cert(text: str) -> str:
            match = CERT_PATTERN.search(text)
            return match.group(1).strip() if match else "None"

        self.df["Certifications"] = self.df["Resume"].apply(parse_cert)
        logger.info("Extracted Certifications column from resume text")
        return self

    # ------------------------------------------------------------------
    # SYNTHETIC recruitment funnel augmentation (clearly labeled)
    # ------------------------------------------------------------------
    def add_synthetic_funnel_data(self) -> "FeatureEngineer":
        """
        Generate a simulated recruitment funnel so downstream KPI/dashboard
        code can be demonstrated end-to-end. Uses a fixed random seed for
        reproducibility. See SYNTHETIC_COLUMNS for the full list of fields
        this touches.
        """
        n = len(self.df)
        rng = self._rng

        self.df["Department"] = rng.choice(DEPARTMENTS, size=n)
        self.df["Recruiter"] = rng.choice(RECRUITERS, size=n)
        self.df["Hiring_Source"] = rng.choice(HIRING_SOURCES, size=n)
        self.df["City"] = rng.choice(CITIES, size=n)

        # Funnel status weighted so it looks like a realistic drop-off funnel
        status_weights = [0.30, 0.28, 0.20, 0.12, 0.07, 0.03]
        self.df["Application_Status"] = rng.choice(STATUS_FLOW, size=n, p=status_weights)

        # Application dates across an 18-month simulated hiring window
        start_date = pd.Timestamp("2025-01-01")
        offsets = rng.integers(0, 545, size=n)
        self.df["Application_Date"] = start_date + pd.to_timedelta(offsets, unit="D")

        # Downstream funnel dates only populated if candidate progressed that far
        status_rank = {s: i for i, s in enumerate(STATUS_FLOW[:-2])}  # Applied..Offered/Hired chain
        rank_map = {"Applied": 0, "Screened": 1, "Interviewed": 2, "Offered": 3, "Hired": 4, "Rejected": -1}
        ranks = self.df["Application_Status"].map(rank_map)

        self.df["Screening_Date"] = np.where(
            ranks >= 1, self.df["Application_Date"] + pd.to_timedelta(rng.integers(2, 10, size=n), unit="D"), pd.NaT
        )
        self.df["Interview_Date"] = np.where(
            ranks >= 2, self.df["Application_Date"] + pd.to_timedelta(rng.integers(10, 25, size=n), unit="D"), pd.NaT
        )
        self.df["Offer_Date"] = np.where(
            ranks >= 3, self.df["Application_Date"] + pd.to_timedelta(rng.integers(25, 40, size=n), unit="D"), pd.NaT
        )
        self.df["Hire_Date"] = np.where(
            ranks == 4, self.df["Application_Date"] + pd.to_timedelta(rng.integers(40, 55, size=n), unit="D"), pd.NaT
        )
        for col in ["Screening_Date", "Interview_Date", "Offer_Date", "Hire_Date"]:
            self.df[col] = pd.to_datetime(self.df[col])

        # Salary offered: base by experience level + noise, only for Offered/Hired
        level_base = {"Entry": 400000, "Mid": 800000, "Senior": 1500000, "Unknown": 600000}
        base = self.df.get("Experience_Level", pd.Series(["Unknown"] * n)).map(level_base).fillna(600000)
        noise = rng.normal(0, 50000, size=n)
        salary = (base + noise).round(-3).clip(lower=250000)
        self.df["Salary_Offered"] = np.where(ranks >= 3, salary, np.nan)

        # Resume match/quality score (0-100), correlated loosely with real Best Match label if present
        base_score = rng.normal(65, 15, size=n)
        if "Best Match" in self.df.columns:
            base_score = base_score + self.df["Best Match"].fillna(0).astype(float) * 15
        self.df["Resume_Score"] = np.clip(base_score, 0, 100).round(1)

        # Years of experience derived loosely from Experience_Level + noise
        exp_level_years = {"Entry": (0, 2), "Mid": (3, 7), "Senior": (8, 20), "Unknown": (0, 15)}
        years = self.df.get("Experience_Level", pd.Series(["Unknown"] * n)).map(
            lambda lvl: rng.integers(*exp_level_years.get(lvl, (0, 15)))
        )
        self.df["Years_Experience"] = years

        logger.info("Synthetic recruitment funnel data generated | seed=%d | columns=%s", RANDOM_SEED, SYNTHETIC_COLUMNS)
        return self

    def get_result(self) -> pd.DataFrame:
        return self.df

    def run_all(self) -> pd.DataFrame:
        """Run real extraction first, then synthetic augmentation."""
        return (
            self.extract_education()
            .extract_experience_level()
            .extract_skills()
            .extract_certifications()
            .add_synthetic_funnel_data()
            .get_result()
        )
