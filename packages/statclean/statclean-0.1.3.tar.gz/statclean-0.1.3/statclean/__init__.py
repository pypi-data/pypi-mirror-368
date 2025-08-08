"""
StatClean - A comprehensive statistical data preprocessing and outlier detection library

This package provides advanced statistical methods for data cleaning including:
- Formal statistical testing (Grubbs' test, Dixon's Q-test)
- Multiple outlier detection methods (IQR, Z-score, Modified Z-score, Mahalanobis)
- Treatment options (removal, winsorizing, transformations)
- Publication-quality reporting with p-values and effect sizes
- Method chaining for streamlined workflows

Designed for academic research, data science, and statistical analysis.
"""

__version__ = '0.1.3'
__author__ = 'Subashanan Nair'

from .cleaner import StatClean
from .utils import plot_outliers, plot_distribution, plot_boxplot, plot_qq, plot_outlier_analysis

# Backwards compatibility alias (to be removed in future versions)
OutlierCleaner = StatClean

__all__ = ['StatClean', 'OutlierCleaner', 'plot_outliers', 'plot_distribution', 'plot_boxplot', 'plot_qq', 'plot_outlier_analysis']