"""
data_loader.py
---------------
Handles loading the raw job applicant dataset and reporting an initial
data-quality profile (shape, dtypes, missing values, duplicates).

Author: Recruitment Analytics Team
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union

import pandas as pd

from src.utils import get_logger

logger = get_logger(__name__)


@dataclass
class DatasetProfile:
    """Container for a dataset's structural profile."""

    shape: tuple
    columns: list
    dtypes: pd.Series
    summary_statistics: pd.DataFrame
    missing_values: pd.Series
    duplicate_records: int


class DataLoader:
    """
    Loads the raw recruitment CSV file and produces a structural profile
    of the dataset before any cleaning is applied.
    """

    def __init__(self, file_path: Union[str, Path]) -> None:
        """
        Args:
            file_path: Path to the raw CSV file.
        """
        self.file_path = Path(file_path)
        self.df: pd.DataFrame | None = None

    def load(self) -> pd.DataFrame:
        """
        Load the CSV file into a DataFrame.

        Returns:
            The loaded DataFrame.

        Raises:
            FileNotFoundError: If the CSV file does not exist.
            pd.errors.EmptyDataError: If the CSV file is empty.
        """
        if not self.file_path.exists():
            logger.error("Dataset not found at %s", self.file_path)
            raise FileNotFoundError(f"Dataset not found at {self.file_path}")

        try:
            self.df = pd.read_csv(self.file_path)
            logger.info(
                "Data Loaded | rows=%d | columns=%d | source=%s",
                self.df.shape[0],
                self.df.shape[1],
                self.file_path.name,
            )
            return self.df
        except pd.errors.EmptyDataError as exc:
            logger.error("The dataset file is empty: %s", self.file_path)
            raise exc

    def profile(self) -> DatasetProfile:
        """
        Generate a structural profile of the loaded dataset: shape, columns,
        dtypes, summary statistics, missing values, and duplicate count.

        Returns:
            A DatasetProfile instance.

        Raises:
            ValueError: If called before load().
        """
        if self.df is None:
            raise ValueError("Call load() before profile().")

        profile = DatasetProfile(
            shape=self.df.shape,
            columns=list(self.df.columns),
            dtypes=self.df.dtypes,
            summary_statistics=self.df.describe(include="all").transpose(),
            missing_values=self.df.isnull().sum(),
            duplicate_records=int(self.df.duplicated().sum()),
        )
        logger.info(
            "Profile generated | missing_cells=%d | duplicates=%d",
            int(profile.missing_values.sum()),
            profile.duplicate_records,
        )
        return profile

    def print_profile(self) -> None:
        """Print a human-readable summary of the dataset profile to console."""
        p = self.profile()
        print("=" * 70)
        print("DATASET PROFILE")
        print("=" * 70)
        print(f"Shape               : {p.shape[0]} rows x {p.shape[1]} columns")
        print(f"Columns             : {p.columns}")
        print("-" * 70)
        print("Data Types:")
        print(p.dtypes)
        print("-" * 70)
        print("Missing Values:")
        print(p.missing_values[p.missing_values > 0])
        print("-" * 70)
        print(f"Duplicate Records   : {p.duplicate_records}")
        print("-" * 70)
        print("Summary Statistics:")
        print(p.summary_statistics)
        print("=" * 70)
