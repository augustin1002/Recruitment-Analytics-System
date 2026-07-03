# 📊 Recruitment Analytics System

An end-to-end recruitment analytics pipeline and executive dashboard — built with Python, Pandas, SQLite, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?logo=pandas)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Interactive_Charts-3F4F75?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Portfolio_Project-orange)

---

## ⚠️ Important — Read Before Reviewing the Numbers

This project is built on a **public resume-matching dataset** (`job_applicant_dataset.csv`, 10,000 candidates) that contains candidate demographics, free-text resumes, job roles, and a `Best Match` label — **it is not a real recruitment funnel dataset**. It has no salary, recruiter, department, hiring source, or application-date fields.

To demonstrate a complete recruitment analytics system end-to-end, this project:

| Field type | Fields | Source |
|---|---|---|
| **Real** | Name, Age, Gender, Race, Ethnicity, Job Roles, Resume text, Best Match | Original dataset |
| **Real (extracted)** | Education, Experience Level, Skills, Certifications | Parsed from resume text with regex |
| **🔶 Simulated (fixed seed = 42)** | Department, Recruiter, Hiring Source, City, Application Status, all funnel dates, Salary Offered, Resume Score, Years of Experience, Cost per Hire basis | Generated in `src/feature_engineering.py` |

Every simulated column is explicitly listed in `SYNTHETIC_COLUMNS` in the code and flagged in the dashboard sidebar and every dashboard page. **This is intentional and disclosed** — the goal of this project is to demonstrate the full analytics engineering pipeline (cleaning → SQL → KPIs → dashboard → reporting), not to claim real hiring outcomes.

---

## 📌 Business Problem

Recruitment teams often lack a unified view of their pipeline — application volume, funnel conversion, recruiter performance, and hiring costs typically live in disconnected spreadsheets. This project simulates a **Recruitment Operations Analytics System** that a Data/People Analytics team could use to:

- Track applications from source to hire in one funnel view
- Identify which recruiters, departments, and hiring sources convert best
- Monitor time-to-hire and cost-per-hire against targets
- Export leadership-ready reports (Excel/PDF) on demand

---

## 🏗️ Architecture

```
Raw CSV → DataLoader → DataCleaner → FeatureEngineer → SQLite (SQLAlchemy)
                                            │
                        ┌───────────────────┼───────────────────┐
                        ▼                   ▼                   ▼
                 RecruitmentAnalytics   KPICalculator     ReportGenerator
                     (EDA)              (KPI Engine)     (Excel/PDF/CSV)
                        │                   │                   │
                        └─────────► Streamlit Dashboard ◄────────┘
                                  (Plotly interactive charts)
```

Each stage is a standalone, testable Python class (OOP) with type hints, docstrings, and logging — see `src/`.

---

## ✨ Features

- **Modular OOP pipeline**: `DataLoader`, `DataCleaner`, `FeatureEngineer`, `KPICalculator`, `RecruitmentAnalytics`, `RecruitmentDatabase`, `ReportGenerator`
- **Real resume-text parsing**: Education, Skills, Certifications, and Experience Level extracted with regex — not hardcoded
- **SQLite + SQLAlchemy** persistence layer with 7 pre-built analytical SQL queries
- **17 recruitment KPIs**: funnel conversion rates, time-to-hire, cost-per-hire, recruiter/department/source performance
- **5-page Streamlit dashboard**: Executive overview, Candidate Analysis, Recruitment Funnel, Recruiter Performance, Hiring Trends
- **Sidebar filters**: Job Role, Department, Experience Level, Gender, Date Range
- **One-click exports**: filtered data to CSV and Excel from the dashboard
- **Auto-generated reports**: `Recruitment_Report.xlsx` (multi-sheet, charted), `Recruitment_Report.pdf` (executive summary), `Recruitment_KPIs.csv`
- **Centralized logging** to `logs/pipeline.log` at every pipeline stage
- **5 Jupyter notebooks** mirroring each pipeline stage for exploratory work

---

## 📈 Recruitment KPIs Calculated

| KPI | KPI |
|---|---|
| Applications Received | Time to Hire |
| Candidates Screened | Time to Fill |
| Interview Conversion Rate | Cost per Hire (simulated cost basis) |
| Interview Pass Rate | Recruiter Performance |
| Offer Acceptance Rate | Department Hiring |
| Hiring Rate | Hiring Source Performance |
| Candidate Rejection Rate | Average Resume Score |
| Average Experience | Average Salary Offered |

---

## 🖼️ Screenshots

> Run the dashboard locally (`streamlit run dashboard/app.py`) and drop your own screenshots into `images/` — replace the placeholders below with `dashboard.png`, etc.

Sample static outputs generated by the pipeline are included in `images/`:
- `hiring_trend.png` — monthly hiring trend
- `funnel.png` — recruitment funnel by stage
- `recruiter_performance.png` — hires by recruiter

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/augustin1002/Recruitment-Analytics-System.git
cd Recruitment-Analytics-System

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the full analytics pipeline (cleaning, KPIs, SQLite, reports)
python main.py

# 5. Launch the interactive dashboard
streamlit run dashboard/app.py
```

Outputs after step 4:
- `data/processed/cleaned_candidates.csv`
- `data/processed/shortlisted_candidates.csv`
- `data/processed/recruitment_kpis.csv`
- `data/database/recruitment.db`
- `reports/Recruitment_Report.xlsx`
- `reports/Recruitment_Report.pdf`
- `reports/Recruitment_KPIs.csv`
- `logs/pipeline.log`

---

## 📂 Project Structure

```
Recruitment-Analytics-System/
├── data/
│   ├── raw/job_applicant_dataset.csv
│   ├── processed/               # cleaned_candidates, shortlisted_candidates, recruitment_kpis
│   └── database/recruitment.db
├── notebooks/                   # 01-05, mirror the pipeline stages
├── src/
│   ├── data_loader.py           # Step 1: load + profile
│   ├── preprocessing.py         # Step 2: cleaning
│   ├── feature_engineering.py   # Step 3: real resume parsing + simulated funnel
│   ├── analytics.py             # Step 3: EDA
│   ├── kpi.py                   # Step 4: KPI engine
│   ├── sql_database.py          # Step 5: SQLAlchemy + SQL queries
│   ├── visualization.py         # Matplotlib (reports) + Plotly (dashboard) charts
│   ├── report_generator.py      # Step 7: Excel/PDF/CSV reports
│   └── utils.py                 # logging + path config
├── dashboard/
│   ├── app.py                   # main Streamlit entry point
│   └── pages/                   # 5 additional dashboard pages
├── reports/                     # generated Excel/PDF/CSV
├── images/                      # sample chart exports
├── logs/pipeline.log
├── main.py                      # pipeline orchestrator
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🧰 Tech Stack

Python · Pandas · NumPy · SQLite · SQLAlchemy · Matplotlib · Plotly · Streamlit · OpenPyXL · Scikit-learn (optional) · Logging · OOP

---

## 🚀 Future Improvements

- Replace simulated funnel/salary data with a real ATS export (Greenhouse, Lever, Workday) for production use
- Add a Scikit-learn resume-to-job matching classifier using the real `Best Match` label
- Add bias/fairness analysis across Gender, Race, and Ethnicity in match outcomes (the dataset was originally designed for this)
- Containerize with Docker and deploy the dashboard to Streamlit Cloud
- Add automated tests (pytest) for each `src/` module
- Schedule the pipeline with Airflow/Prefect for recurring report generation

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 👤 Author

**Augustin Arul Raja** — Data Analyst / Data Scientist
[Portfolio](https://augustin1002.github.io/augustinportfolio/portfolio/) · [GitHub](https://github.com/augustin1002) · [LinkedIn](https://linkedin.com/in/augustinarulraja)
