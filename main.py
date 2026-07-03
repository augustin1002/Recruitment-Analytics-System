"""
main.py
-------
End-to-end pipeline orchestrator for the Recruitment Analytics System.

Run with:
    python main.py

Pipeline stages:
    1. Load raw data + profile
    2. Clean data
    3. Feature engineering (real resume features + synthetic funnel data)
    4. Exploratory Data Analysis
    5. KPI calculation
    6. Load into SQLite
    7. Generate reports (Excel, PDF, CSV)

Author: Recruitment Analytics Team
"""

import sys

from src.analytics import RecruitmentAnalytics
from src.data_loader import DataLoader
from src.feature_engineering import FeatureEngineer
from src.kpi import KPICalculator
from src.preprocessing import DataCleaner
from src.report_generator import ReportGenerator
from src.sql_database import RecruitmentDatabase
from src.utils import Paths, get_logger

logger = get_logger(__name__)


def run_pipeline() -> None:
    """Execute the full recruitment analytics pipeline end-to-end."""
    logger.info("=" * 60)
    logger.info("RECRUITMENT ANALYTICS PIPELINE — START")
    logger.info("=" * 60)

    try:
        # Step 1: Load + profile
        loader = DataLoader(Paths.RAW_DATA)
        raw_df = loader.load()
        loader.print_profile()

        # Step 2: Clean
        cleaner = DataCleaner(raw_df)
        cleaned_df = cleaner.run_all()
        Paths.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        cleaned_df.to_csv(Paths.CLEANED_DATA, index=False)
        logger.info("Cleaned dataset saved to %s", Paths.CLEANED_DATA)

        # Step 3: Feature engineering (real + synthetic)
        engineer = FeatureEngineer(cleaned_df)
        enriched_df = engineer.run_all()

        # Save a "shortlisted" view (Resume_Score >= 70) as an example downstream artifact
        shortlisted_df = enriched_df[enriched_df["Resume_Score"] >= 70]
        shortlisted_df.to_csv(Paths.SHORTLISTED_DATA, index=False)
        logger.info("Shortlisted candidates (score >= 70) saved: %d rows", len(shortlisted_df))

        # Step 4: EDA
        analytics = RecruitmentAnalytics(enriched_df)
        analytics.generate_all_insights()

        # Step 5: KPIs
        kpi_calc = KPICalculator(enriched_df)
        kpi_summary = kpi_calc.build_kpi_summary()
        kpi_summary.to_csv(Paths.KPI_DATA, index=False)
        logger.info("KPI summary saved to %s", Paths.KPI_DATA)

        # Step 6: SQLite
        db = RecruitmentDatabase()
        db.load_dataframe(enriched_df)

        # Step 7: Reports
        reporter = ReportGenerator(enriched_df, kpi_summary)
        reporter.generate_all()

        logger.info("=" * 60)
        logger.info("RECRUITMENT ANALYTICS PIPELINE — COMPLETE")
        logger.info("=" * 60)

    except Exception as exc:  # noqa: BLE001 - top-level pipeline guard
        logger.exception("Pipeline failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
