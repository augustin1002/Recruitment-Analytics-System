"""
preprocessing.py
-----------------
Data cleaning routines for the recruitment dataset: deduplication, missing
value handling, type conversion, standardization, and validation.

Author: Recruitment Analytics Team
"""

import re
from typing import Optional

import numpy as np
import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)

MIN_PLAUSIBLE_AGE = 18
MAX_PLAUSIBLE_AGE = 70

GENDER_MAP = {
    "m": "Male",
    "male": "Male",
    "f": "Female",
    "female": "Female",
    "nonbinary": "Non-Binary",
    "non-binary": "Non-Binary",
    "non binary": "Non-Binary",
}


class DataCleaner:
    """
    Applies a professional, auditable cleaning pipeline to the raw
    job applicant dataset. Each step is logged and non-destructive
    (operates on a copy of the input DataFrame).
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()
        self._initial_rows = len(self.df)

    def remove_duplicates(self) -> "DataCleaner":
        """Remove exact duplicate candidate records."""
        before = len(self.df)
        self.df = self.df.drop_duplicates(
            subset=["Job Applicant Name", "Age", "Gender", "Job Roles", "Resume"]
        ).reset_index(drop=True)
        removed = before - len(self.df)
        logger.info("Removed %d duplicate candidate record(s)", removed)
        return self

    def handle_missing_values(self) -> "DataCleaner":
        """
        Handle missing values per column:
        - Critical text fields (Name, Resume, Job Roles): drop row if missing.
        - Categorical fields (Gender, Race, Ethnicity): fill with 'Unknown'.
        - Age: fill with median age.
        """
        critical_cols = ["Job Applicant Name", "Resume", "Job Roles"]
        before = len(self.df)
        self.df = self.df.dropna(subset=critical_cols)
        logger.info(
            "Dropped %d row(s) missing critical fields %s",
            before - len(self.df),
            critical_cols,
        )

        for col in ["Gender", "Race", "Ethnicity"]:
            if col in self.df.columns:
                n_missing = self.df[col].isnull().sum()
                self.df[col] = self.df[col].fillna("Unknown")
                if n_missing:
                    logger.info("Filled %d missing value(s) in '%s' with 'Unknown'", n_missing, col)

        if "Age" in self.df.columns:
            n_missing_age = self.df["Age"].isnull().sum()
            median_age = self.df["Age"].median()
            self.df["Age"] = self.df["Age"].fillna(median_age)
            if n_missing_age:
                logger.info("Filled %d missing Age value(s) with median (%.0f)", n_missing_age, median_age)

        return self

    def convert_dtypes(self) -> "DataCleaner":
        """Ensure Age is integer and text columns are stripped strings."""
        self.df["Age"] = pd.to_numeric(self.df["Age"], errors="coerce").astype("Int64")
        for col in ["Job Applicant Name", "Gender", "Race", "Ethnicity", "Job Roles"]:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip()
        logger.info("Data types converted/standardized")
        return self

    def standardize_gender(self) -> "DataCleaner":
        """Normalize free-text gender values into a consistent category set."""
        self.df["Gender"] = (
            self.df["Gender"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(GENDER_MAP)
            .fillna(self.df["Gender"])
        )
        logger.info("Gender values standardized | categories=%s", sorted(self.df["Gender"].unique().tolist()))
        return self

    def fix_inconsistent_job_titles(self) -> "DataCleaner":
        """
        Normalize job title formatting: strip whitespace, standardize
        capitalization (Title Case), and collapse repeated spaces.
        """
        self.df["Job Roles"] = (
            self.df["Job Roles"]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.title()
        )
        logger.info("Standardized %d unique job titles", self.df["Job Roles"].nunique())
        return self

    def remove_impossible_ages(self) -> "DataCleaner":
        """Remove candidates with implausible ages (outside 18-70)."""
        before = len(self.df)
        self.df = self.df[
            (self.df["Age"] >= MIN_PLAUSIBLE_AGE) & (self.df["Age"] <= MAX_PLAUSIBLE_AGE)
        ].reset_index(drop=True)
        removed = before - len(self.df)
        logger.info("Removed %d row(s) with implausible age (outside %d-%d)", removed, MIN_PLAUSIBLE_AGE, MAX_PLAUSIBLE_AGE)
        return self

    @staticmethod
    def _make_email(name: str) -> str:
        """Generate a plausible candidate email from their name (synthetic field)."""
        slug = re.sub(r"[^a-z.]", "", name.lower().replace(" ", "."))
        return f"{slug}@example-applicant.com"

    def add_and_validate_email(self) -> "DataCleaner":
        """
        NOTE (synthetic field): The source dataset has no email column.
        A demo email is derived from the candidate's name so downstream
        contact/CRM-style features can be demonstrated, then validated
        with a standard email regex.
        """
        self.df["Email"] = self.df["Job Applicant Name"].apply(self._make_email)
        pattern = re.compile(r"^[\w.\-]+@[\w\-]+\.[a-zA-Z]{2,}$")
        self.df["Email_Valid"] = self.df["Email"].apply(lambda x: bool(pattern.match(x)))
        invalid = (~self.df["Email_Valid"]).sum()
        logger.info("Generated synthetic emails | invalid_format_count=%d", invalid)
        return self

    def get_result(self) -> pd.DataFrame:
        """Return the cleaned DataFrame and log a before/after summary."""
        logger.info(
            "Cleaning Complete | rows_before=%d | rows_after=%d | rows_removed=%d",
            self._initial_rows,
            len(self.df),
            self._initial_rows - len(self.df),
        )
        return self.df

    def run_all(self) -> pd.DataFrame:
        """Run the full cleaning pipeline in the recommended order."""
        return (
            self.remove_duplicates()
            .handle_missing_values()
            .convert_dtypes()
            .standardize_gender()
            .fix_inconsistent_job_titles()
            .remove_impossible_ages()
            .add_and_validate_email()
            .get_result()
        )
