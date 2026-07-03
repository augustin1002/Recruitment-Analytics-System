"""
utils.py
--------
Shared utility functions: logging configuration and common helpers used
across the Recruitment Analytics System.

Author: Recruitment Analytics Team
"""

import logging
import os
from pathlib import Path

# Project root is one level above src/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(name: str, log_file: str = "pipeline.log") -> logging.Logger:
    """
    Create and configure a logger that writes to both console and a
    shared log file.

    Args:
        name: Name of the logger (typically __name__ of the caller).
        log_file: File name (relative to logs/) to write log records to.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        # Avoid duplicate handlers if the logger has already been configured
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (shared pipeline.log)
    file_handler = logging.FileHandler(LOG_DIR / log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def ensure_dir(path: str) -> None:
    """Create a directory (and parents) if it does not already exist."""
    os.makedirs(path, exist_ok=True)


# Centralized path constants used across the project
class Paths:
    """Central registry of project file paths."""

    ROOT = PROJECT_ROOT
    RAW_DATA = PROJECT_ROOT / "data" / "raw" / "job_applicant_dataset.csv"
    PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
    CLEANED_DATA = PROCESSED_DIR / "cleaned_candidates.csv"
    SHORTLISTED_DATA = PROCESSED_DIR / "shortlisted_candidates.csv"
    KPI_DATA = PROCESSED_DIR / "recruitment_kpis.csv"
    DATABASE = PROJECT_ROOT / "data" / "database" / "recruitment.db"
    REPORTS_DIR = PROJECT_ROOT / "reports"
    IMAGES_DIR = PROJECT_ROOT / "images"
