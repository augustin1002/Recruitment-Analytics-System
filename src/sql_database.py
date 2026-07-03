"""
sql_database.py
----------------
SQLite persistence layer using SQLAlchemy. Loads the cleaned/engineered
candidate dataset into a `candidates` table and exposes reusable SQL
queries for recruiter, skills, salary, hiring, and diversity analysis.

Author: Recruitment Analytics Team
"""

from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.utils import Paths, get_logger

logger = get_logger(__name__)


class RecruitmentDatabase:
    """Wraps a SQLite database (via SQLAlchemy) holding recruitment data."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or str(Paths.DATABASE)
        self.engine: Engine = create_engine(f"sqlite:///{self.db_path}")

    def load_dataframe(self, df: pd.DataFrame, table_name: str = "candidates") -> None:
        """Write a DataFrame into the SQLite database, replacing any existing table."""
        df.to_sql(table_name, con=self.engine, if_exists="replace", index=False)
        logger.info("Loaded %d rows into SQLite table '%s' (%s)", len(df), table_name, self.db_path)

    def run_query(self, query: str) -> pd.DataFrame:
        """Execute a raw SQL query and return the result as a DataFrame."""
        with self.engine.connect() as conn:
            result = pd.read_sql(text(query), conn)
        return result

    # ------------------------------------------------------------------
    # Pre-built analytical queries
    # ------------------------------------------------------------------
    def top_recruiters(self, limit: int = 10) -> pd.DataFrame:
        query = f"""
            SELECT Recruiter,
                   COUNT(*) AS Applications,
                   SUM(CASE WHEN Application_Status = 'Hired' THEN 1 ELSE 0 END) AS Hires
            FROM candidates
            GROUP BY Recruiter
            ORDER BY Hires DESC
            LIMIT {limit};
        """
        return self.run_query(query)

    def top_skills(self, limit: int = 15) -> pd.DataFrame:
        query = """
            SELECT Skills, COUNT(*) AS Frequency
            FROM candidates
            GROUP BY Skills
            ORDER BY Frequency DESC
            LIMIT {limit};
        """.format(limit=limit)
        return self.run_query(query)

    def average_salary(self) -> pd.DataFrame:
        query = """
            SELECT Department, ROUND(AVG(Salary_Offered), 2) AS Avg_Salary
            FROM candidates
            WHERE Salary_Offered IS NOT NULL
            GROUP BY Department
            ORDER BY Avg_Salary DESC;
        """
        return self.run_query(query)

    def monthly_hiring(self) -> pd.DataFrame:
        query = """
            SELECT strftime('%Y-%m', Hire_Date) AS Hire_Month,
                   COUNT(*) AS Hires
            FROM candidates
            WHERE Application_Status = 'Hired'
            GROUP BY Hire_Month
            ORDER BY Hire_Month;
        """
        return self.run_query(query)

    def department_hiring(self) -> pd.DataFrame:
        query = """
            SELECT Department,
                   COUNT(*) AS Applications,
                   SUM(CASE WHEN Application_Status = 'Hired' THEN 1 ELSE 0 END) AS Hires
            FROM candidates
            GROUP BY Department
            ORDER BY Hires DESC;
        """
        return self.run_query(query)

    def gender_diversity(self) -> pd.DataFrame:
        query = """
            SELECT Gender, COUNT(*) AS Count,
                   ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM candidates), 2) AS Percentage
            FROM candidates
            GROUP BY Gender
            ORDER BY Count DESC;
        """
        return self.run_query(query)

    def highest_hiring_source(self) -> pd.DataFrame:
        query = """
            SELECT Hiring_Source,
                   COUNT(*) AS Applications,
                   SUM(CASE WHEN Application_Status = 'Hired' THEN 1 ELSE 0 END) AS Hires
            FROM candidates
            GROUP BY Hiring_Source
            ORDER BY Hires DESC;
        """
        return self.run_query(query)
