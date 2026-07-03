"""
visualization.py
-----------------
Chart-building functions used by both the static report generator
(Matplotlib, saved as PNG for the PDF/Excel reports) and the interactive
Streamlit dashboard (Plotly).

Author: Recruitment Analytics Team
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless rendering for report generation
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.utils import Paths, get_logger

logger = get_logger(__name__)

plt.style.use("seaborn-v0_8-whitegrid")


class ChartFactory:
    """Static-image (Matplotlib) chart builders used for the offline reports."""

    @staticmethod
    def save_bar_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, filename: str) -> Path:
        fig, ax = plt.subplots(figsize=(9, 5))
        series.plot(kind="bar", ax=ax, color="#2E86AB")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        out_path = Paths.IMAGES_DIR / filename
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        logger.info("Saved chart: %s", out_path)
        return out_path

    @staticmethod
    def save_line_chart(series: pd.Series, title: str, xlabel: str, ylabel: str, filename: str) -> Path:
        fig, ax = plt.subplots(figsize=(9, 5))
        series.index = series.index.astype(str)
        series.plot(kind="line", marker="o", ax=ax, color="#F18F01")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        out_path = Paths.IMAGES_DIR / filename
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        logger.info("Saved chart: %s", out_path)
        return out_path

    @staticmethod
    def save_heatmap(corr: pd.DataFrame, filename: str = "correlation_heatmap.png") -> Path:
        fig, ax = plt.subplots(figsize=(7, 6))
        im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right")
        ax.set_yticklabels(corr.columns)
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=8)
        fig.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title("Correlation Heatmap", fontsize=13, fontweight="bold")
        plt.tight_layout()
        out_path = Paths.IMAGES_DIR / filename
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        logger.info("Saved chart: %s", out_path)
        return out_path


class InteractiveCharts:
    """Plotly chart builders used inside the Streamlit dashboard."""

    @staticmethod
    def bar(series: pd.Series, title: str) -> go.Figure:
        fig = px.bar(x=series.index.astype(str), y=series.values, title=title, color=series.values,
                     color_continuous_scale="Blues", labels={"x": "", "y": "Count"})
        fig.update_layout(showlegend=False, coloraxis_showscale=False)
        return fig

    @staticmethod
    def pie(series: pd.Series, title: str) -> go.Figure:
        fig = px.pie(names=series.index.astype(str), values=series.values, title=title, hole=0.4)
        return fig

    @staticmethod
    def line(series: pd.Series, title: str) -> go.Figure:
        fig = px.line(x=series.index.astype(str), y=series.values, title=title, markers=True,
                       labels={"x": "", "y": "Count"})
        return fig

    @staticmethod
    def scatter(df: pd.DataFrame, x: str, y: str, color: str, title: str) -> go.Figure:
        fig = px.scatter(df, x=x, y=y, color=color, title=title, opacity=0.6)
        return fig

    @staticmethod
    def heatmap(corr: pd.DataFrame, title: str = "Correlation Heatmap") -> go.Figure:
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", title=title, zmin=-1, zmax=1)
        return fig

    @staticmethod
    def funnel(stage_counts: pd.Series, title: str = "Hiring Funnel") -> go.Figure:
        fig = go.Figure(go.Funnel(y=stage_counts.index.tolist(), x=stage_counts.values.tolist()))
        fig.update_layout(title=title)
        return fig

    @staticmethod
    def histogram(series: pd.Series, title: str, nbins: int = 30) -> go.Figure:
        fig = px.histogram(series, nbins=nbins, title=title)
        fig.update_layout(showlegend=False)
        return fig
