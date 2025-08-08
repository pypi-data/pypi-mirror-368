"""
StatClean - A comprehensive statistical data preprocessing and outlier detection library

This module provides advanced statistical methods for data cleaning, outlier detection,
and data preprocessing. Features include formal statistical testing (Grubbs', Dixon's),
multivariate outlier detection (Mahalanobis), winsorizing, data transformations,
and publication-quality statistical reporting.

Statistical Methods Available:
- Univariate: IQR, Z-score, Modified Z-score, Grubbs' test, Dixon's Q-test
- Multivariate: Mahalanobis distance
- Treatments: Removal, Winsorizing, Box-Cox/Log/Square-root transformations
- Testing: P-values, confidence intervals, effect sizes
"""

from typing import Optional, List, Dict, Tuple, Union, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2, t, boxcox
# from scipy.special import ndtri  # Currently unused
from tqdm import tqdm
import warnings
import math


class StatClean:
    """
    A comprehensive statistical data preprocessing and outlier detection toolkit.
    
    StatClean provides advanced statistical methods for data cleaning including:
    - Formal statistical testing (Grubbs' test, Dixon's Q-test)
    - Multiple outlier detection methods (IQR, Z-score, Modified Z-score, Mahalanobis)
    - Treatment options (removal, winsorizing, transformations)
    - Publication-quality reporting with p-values and effect sizes
    - Method chaining for streamlined workflows
    
    Designed for academic research, data science, and statistical analysis
    where rigorous statistical methods and reproducible results are essential.
    """
    
    def __init__(self, df: Optional[pd.DataFrame] = None, preserve_index: bool = True) -> None:
        """
        Initialize StatClean with an optional DataFrame.
        
        Parameters:
        -----------
        df : pandas.DataFrame, optional
            The DataFrame to clean
        preserve_index : bool, default=True
            Whether to preserve the original index after cleaning
        
        Raises:
        -------
        ValueError
            If the provided DataFrame is empty
        """
        if df is not None and df.empty:
            raise ValueError("Cannot initialize with an empty DataFrame")
        
        self.original_df: Optional[pd.DataFrame] = df.copy() if df is not None else None
        self.clean_df: Optional[pd.DataFrame] = df.copy() if df is not None else None
        self.outlier_info: Dict[str, Dict[str, Any]] = {}
        self.preserve_index: bool = preserve_index
        
        # Default thresholds configuration
        self._default_thresholds = {
            'iqr_lower_factor': 1.5,
            'iqr_upper_factor': 1.5,
            'zscore_threshold': 3.0,
            'modified_zscore_threshold': 3.5
        }
        
    def set_data(self, df: pd.DataFrame, preserve_index: Optional[bool] = None) -> None:
        """
        Set or update the DataFrame to be cleaned.
        
        Parameters:
        -----------
        df : pandas.DataFrame
            The DataFrame to clean
        preserve_index : bool, optional
            Whether to preserve the original index after cleaning.
            If None, uses the value set in __init__
        
        Raises:
        -------
        ValueError
            If the provided DataFrame is empty or None
        """
        if df is None:
            raise ValueError("DataFrame cannot be None")
        if df.empty:
            raise ValueError("Cannot set an empty DataFrame")
        
        self.original_df = df.copy()
        self.clean_df = df.copy()
        self.outlier_info = {}
        if preserve_index is not None:
            self.preserve_index = preserve_index
    
    # Statistical utility methods
    def _calculate_iqr_bounds(self, column: str, lower_factor: Optional[float] = None, 
                             upper_factor: Optional[float] = None) -> Tuple[float, float, Dict[str, float]]:
        """
        Calculate IQR bounds for outlier detection.
        
        Returns:
        --------
        tuple
            (lower_bound, upper_bound, stats_dict)
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        lower_factor = lower_factor or self._default_thresholds['iqr_lower_factor']
        upper_factor = upper_factor or self._default_thresholds['iqr_upper_factor']
        
        Q1 = self.clean_df[column].quantile(0.25)
        Q3 = self.clean_df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - (lower_factor * IQR)
        upper_bound = Q3 + (upper_factor * IQR)
        
        stats = {
            'Q1': Q1,
            'Q3': Q3,
            'IQR': IQR,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'lower_factor': lower_factor,
            'upper_factor': upper_factor
        }
        
        return lower_bound, upper_bound, stats
    
    def _calculate_zscore_stats(self, column: str, threshold: Optional[float] = None) -> Tuple[float, float, float]:
        """
        Calculate Z-score statistics.
        
        Returns:
        --------
        tuple
            (mean, std, threshold)
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        threshold = threshold or self._default_thresholds['zscore_threshold']
        
        # Use cached stats if available
        if hasattr(self, '_stats_cache') and column in self._stats_cache:
            mean = self._stats_cache[column]['mean']
            std = self._stats_cache[column]['std']
        else:
            mean = self.clean_df[column].mean()
            std = self.clean_df[column].std()
        
        return mean, std, threshold
    
    def _calculate_modified_zscore_stats(self, column: str, threshold: Optional[float] = None) -> Tuple[float, float, float]:
        """
        Calculate Modified Z-score statistics using MAD.
        
        Returns:
        --------
        tuple
            (median, mad, threshold)
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        threshold = threshold or self._default_thresholds['modified_zscore_threshold']
        
        median = self.clean_df[column].median()
        mad = stats.median_abs_deviation(self.clean_df[column])
        
        return median, mad, threshold
    
    # Formal statistical testing methods
    def grubbs_test(self, column: str, alpha: float = 0.05, two_sided: bool = True) -> Dict[str, Any]:
        """
        Perform Grubbs' test for outliers with formal statistical testing.
        
        Parameters:
        -----------
        column : str
            The name of the column to test
        alpha : float, default=0.05
            Significance level for the test
        two_sided : bool, default=True
            Whether to perform two-sided test (True) or one-sided (False)
            
        Returns:
        --------
        dict
            Dictionary containing test results:
            - 'statistic': Test statistic value
            - 'p_value': P-value of the test
            - 'critical_value': Critical value for comparison
            - 'is_outlier': Boolean indicating if extreme value is an outlier
            - 'outlier_value': The most extreme value tested
            - 'outlier_index': Index of the outlier (if found)
            - 'method': 'Grubbs test'
        """
        self._validate_column(column)
        data = self.clean_df[column].dropna()
        n = len(data)
        
        if n < 3:
            raise ValueError("Grubbs' test requires at least 3 observations")
        
        # Calculate test statistic
        mean = data.mean()
        std = data.std(ddof=1)  # Sample standard deviation
        
        if std == 0:
            return {
                'statistic': 0.0,
                'p_value': 1.0,
                'critical_value': np.nan,
                'is_outlier': False,
                'outlier_value': np.nan,
                'outlier_index': None,
                'method': 'Grubbs test',
                'warning': 'Zero standard deviation - no outliers detected'
            }
        
        # Find most extreme value
        z_scores = np.abs((data - mean) / std)
        max_z_idx = z_scores.idxmax()
        max_z = z_scores.loc[max_z_idx]
        outlier_value = data.loc[max_z_idx]
        
        # Grubbs test statistic
        G = max_z
        
        # Critical value calculation
        t_val = t.ppf(1 - alpha/(2*n if two_sided else n), n-2)
        critical_value = ((n-1) / np.sqrt(n)) * np.sqrt(t_val**2 / (n-2 + t_val**2))
        
        # P-value calculation (approximate)
        if two_sided:
            p_value = n * (1 - t.cdf(G * np.sqrt((n-2)/(n-1-G**2)), n-2))
        else:
            p_value = (n/2) * (1 - t.cdf(G * np.sqrt((n-2)/(n-1-G**2)), n-2))
        
        p_value = min(p_value, 1.0)  # Ensure p-value doesn't exceed 1
        
        is_outlier = G > critical_value
        
        return {
            'statistic': G,
            'p_value': p_value,
            'critical_value': critical_value,
            'is_outlier': is_outlier,
            'outlier_value': outlier_value,
            'outlier_index': max_z_idx,
            'method': 'Grubbs test',
            'alpha': alpha,
            'n_observations': n
        }
    
    def dixon_q_test(self, column: str, alpha: float = 0.05) -> Dict[str, Any]:
        """
        Perform Dixon's Q-test for outliers (suitable for small samples, n < 30).
        
        Parameters:
        -----------
        column : str
            The name of the column to test
        alpha : float, default=0.05
            Significance level for the test
            
        Returns:
        --------
        dict
            Dictionary containing test results similar to Grubbs' test
        """
        self._validate_column(column)
        data = self.clean_df[column].dropna().sort_values()
        n = len(data)
        
        if n < 3:
            raise ValueError("Dixon's Q-test requires at least 3 observations")
        if n >= 30:
            warnings.warn("Dixon's Q-test is designed for small samples (n < 30). Consider using Grubbs' test.")
        
        # Critical values table for Dixon's Q-test (5% significance level)
        critical_values = {
            3: 0.970, 4: 0.829, 5: 0.710, 6: 0.625, 7: 0.568, 8: 0.526,
            9: 0.493, 10: 0.466, 11: 0.444, 12: 0.426, 13: 0.410, 14: 0.396,
            15: 0.384, 16: 0.374, 17: 0.365, 18: 0.356, 19: 0.349, 20: 0.342,
            21: 0.337, 22: 0.331, 23: 0.326, 24: 0.321, 25: 0.317, 26: 0.312,
            27: 0.308, 28: 0.305, 29: 0.301, 30: 0.290
        }
        
        if n not in critical_values:
            raise ValueError(f"Critical values not available for n={n}")
        
        data_array = data.values
        
        # Test both ends
        Q_low = (data_array[1] - data_array[0]) / (data_array[-1] - data_array[0])
        Q_high = (data_array[-1] - data_array[-2]) / (data_array[-1] - data_array[0])
        
        critical_value = critical_values[n]
        
        # Determine which end has the outlier
        if Q_low > Q_high:
            Q_stat = Q_low
            outlier_idx = data.index[0]
            outlier_value = data_array[0]
        else:
            Q_stat = Q_high
            outlier_idx = data.index[-1]
            outlier_value = data_array[-1]
        
        is_outlier = Q_stat > critical_value
        
        # Approximate p-value (simplified)
        p_value = alpha if Q_stat > critical_value else (1 - alpha)
        
        return {
            'statistic': Q_stat,
            'p_value': p_value,
            'critical_value': critical_value,
            'is_outlier': is_outlier,
            'outlier_value': outlier_value,
            'outlier_index': outlier_idx,
            'method': 'Dixon Q-test',
            'alpha': alpha,
            'n_observations': n,
            'Q_low': Q_low,
            'Q_high': Q_high
        }
    
    # Configuration methods
    def set_thresholds(self, iqr_lower_factor: Optional[float] = None, 
                      iqr_upper_factor: Optional[float] = None,
                      zscore_threshold: Optional[float] = None,
                      modified_zscore_threshold: Optional[float] = None) -> 'StatClean':
        """
        Set default thresholds for outlier detection methods.
        
        Parameters:
        -----------
        iqr_lower_factor : float, optional
            Lower factor for IQR method
        iqr_upper_factor : float, optional
            Upper factor for IQR method
        zscore_threshold : float, optional
            Threshold for Z-score method
        modified_zscore_threshold : float, optional
            Threshold for Modified Z-score method
            
        Returns:
        --------
        StatClean
            Self for method chaining
        """
        if iqr_lower_factor is not None:
            self._default_thresholds['iqr_lower_factor'] = iqr_lower_factor
        if iqr_upper_factor is not None:
            self._default_thresholds['iqr_upper_factor'] = iqr_upper_factor
        if zscore_threshold is not None:
            self._default_thresholds['zscore_threshold'] = zscore_threshold
        if modified_zscore_threshold is not None:
            self._default_thresholds['modified_zscore_threshold'] = modified_zscore_threshold
        
        return self
    
    def get_thresholds(self) -> Dict[str, float]:
        """
        Get current default thresholds.
        
        Returns:
        --------
        dict
            Dictionary of current threshold settings
        """
        return self._default_thresholds.copy()
    
    # Outlier detection methods (non-destructive)
    def detect_outliers_iqr(self, column: str, lower_factor: Optional[float] = None, 
                           upper_factor: Optional[float] = None) -> pd.Series:
        """
        Detect outliers using IQR method without removing them.
        
        Returns:
        --------
        pandas.Series
            Boolean mask where True indicates outliers
        """
        self._validate_column(column)
        lower_bound, upper_bound, _ = self._calculate_iqr_bounds(column, lower_factor, upper_factor)
        return (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
    
    def detect_outliers_zscore(self, column: str, threshold: Optional[float] = None) -> pd.Series:
        """
        Detect outliers using Z-score method without removing them.
        
        Returns:
        --------
        pandas.Series
            Boolean mask where True indicates outliers
        """
        self._validate_column(column)
        mean, std, threshold = self._calculate_zscore_stats(column, threshold)
        
        if std == 0 or pd.isna(std):
            return pd.Series(False, index=self.clean_df.index)
        
        z_scores = np.abs((self.clean_df[column] - mean) / std)
        return z_scores > threshold
    
    def detect_outliers_modified_zscore(self, column: str, threshold: Optional[float] = None) -> pd.Series:
        """
        Detect outliers using Modified Z-score method without removing them.
        
        Returns:
        --------
        pandas.Series
            Boolean mask where True indicates outliers
        """
        self._validate_column(column)
        median, mad, threshold = self._calculate_modified_zscore_stats(column, threshold)
        
        if mad == 0:
            return pd.Series(False, index=self.clean_df.index)
        
        modified_zscores = 0.6745 * (self.clean_df[column] - median) / mad
        return np.abs(modified_zscores) > threshold
    
    def _validate_column(self, column: str) -> None:
        """
        Validate that a column exists and is numeric.
        
        Raises:
        -------
        ValueError
            If column doesn't exist or isn't numeric
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        if column not in self.clean_df.columns:
            available_cols = ", ".join(self.clean_df.columns.tolist())
            raise ValueError(f"Column '{column}' not found in DataFrame. Available columns: {available_cols}")
        
        if not pd.api.types.is_numeric_dtype(self.clean_df[column]):
            raise ValueError(f"Column '{column}' must be numeric for outlier detection")
        
    def add_zscore_columns(self, columns: Optional[List[str]] = None, cache_stats: bool = True) -> 'StatClean':
        """
        Add Z-score columns to the DataFrame for specified columns.
        The new columns will have '_zscore' appended to the original column names.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to calculate Z-scores for. If None, all numeric columns will be used.
        cache_stats : bool, default=True
            Whether to cache mean and std for later use in outlier detection
            
        Returns:
        --------
        StatClean
            Self for method chaining
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
        
        # Initialize stats cache if requested
        if cache_stats and not hasattr(self, '_stats_cache'):
            self._stats_cache: Dict[str, Dict[str, float]] = {}
        
        # Process each column
        for col in columns:
            if col not in self.clean_df.columns:
                warnings.warn(f"Column '{col}' not found in DataFrame. Skipping.")
                continue
                
            if not np.issubdtype(self.clean_df[col].dtype, np.number):
                warnings.warn(f"Column '{col}' is not numeric. Skipping.")
                continue
            
            # Calculate Z-scores
            zscore_col = f"{col}_zscore"
            col_mean = self.clean_df[col].mean()
            col_std = self.clean_df[col].std()
            
            # Cache stats if requested
            if cache_stats:
                self._stats_cache[col] = {'mean': col_mean, 'std': col_std}
            
            # Handle zero standard deviation
            if col_std == 0 or pd.isna(col_std):
                warnings.warn(f"Column '{col}' has zero or NaN standard deviation. Setting Z-scores to 0.")
                self.clean_df[zscore_col] = 0.0
            else:
                self.clean_df[zscore_col] = (self.clean_df[col] - col_mean) / col_std
        
        return self
        
    def clean_zscore_columns(self, threshold: float = 3.0) -> Tuple[pd.DataFrame, Dict[str, Dict[str, Any]]]:
        """
        Clean all columns that have associated Z-score columns.
        This method will remove outliers from all columns that have '_zscore' columns.
        
        Parameters:
        -----------
        threshold : float, default=3.0
            The Z-score threshold above which to consider a point an outlier
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame with outliers removed from all Z-score columns
        dict
            Information about outliers removed from each column
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        # Find all columns with Z-scores
        zscore_cols = [col for col in self.clean_df.columns if col.endswith('_zscore')]
        original_cols = [col[:-7] for col in zscore_cols]  # Remove '_zscore' suffix
        
        if not zscore_cols:
            warnings.warn("No Z-score columns found. Use add_zscore_columns() first.")
            return self.clean_df, self.outlier_info
        
        # Clean each column
        for col in original_cols:
            self.remove_outliers_zscore(col, threshold=threshold)
        
        return self.clean_df, self.outlier_info
        
    def remove_outliers_iqr(self, column: str, lower_factor: Optional[float] = None, upper_factor: Optional[float] = None) -> 'StatClean':
        """
        Remove outliers from a DataFrame column using the IQR method.
        
        Parameters:
        -----------
        column : str
            The name of the column to clean
        lower_factor : float, optional
            The factor to multiply the IQR by for the lower bound. Uses default if None.
        upper_factor : float, optional
            The factor to multiply the IQR by for the upper bound. Uses default if None.
            
        Returns:
        --------
        StatClean
            Self for method chaining
            
        Raises:
        -------
        ValueError
            If no DataFrame is set, column doesn't exist, or factors are negative
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        if column not in self.clean_df.columns:
            available_cols = ", ".join(self.clean_df.columns.tolist())
            raise ValueError(f"Column '{column}' not found in DataFrame. Available columns: {available_cols}")
        
        lower_factor = lower_factor or self._default_thresholds['iqr_lower_factor']
        upper_factor = upper_factor or self._default_thresholds['iqr_upper_factor']
        
        if lower_factor < 0 or upper_factor < 0:
            raise ValueError("Factors must be non-negative values")
        
        if not pd.api.types.is_numeric_dtype(self.clean_df[column]):
            raise ValueError(f"Column '{column}' must be numeric for outlier detection")
            
        # Use utility method to calculate bounds
        lower_bound, upper_bound, stats = self._calculate_iqr_bounds(column, lower_factor, upper_factor)
        
        # Identify outliers
        outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
        outliers = self.clean_df[outlier_mask]
        
        # Create a clean DataFrame without outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Prepare outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
            
        outlier_info = {
            'method': 'IQR',
            'column': column,
            'Q1': stats['Q1'],
            'Q3': stats['Q3'],
            'IQR': stats['IQR'],
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'num_outliers': len(outliers),
            'num_outliers_below': len(self.original_df[self.original_df[column] < lower_bound]),
            'num_outliers_above': len(self.original_df[self.original_df[column] > upper_bound]),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store outlier information
        self.outlier_info[column] = outlier_info
        
        return self
    
    def remove_outliers_zscore(self, column: str, threshold: Optional[float] = None) -> 'StatClean':
        """
        Remove outliers from a DataFrame column using the Z-score method.
        If a Z-score column exists (column_zscore), it will use that instead of recalculating.
        
        Parameters:
        -----------
        column : str
            The name of the column to clean
        threshold : float, optional
            The Z-score threshold above which to consider a point an outlier. Uses default if None.
            
        Returns:
        --------
        StatClean
            Self for method chaining
            
        Raises:
        -------
        ValueError
            If no DataFrame is set, column doesn't exist, or threshold is negative
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        if column not in self.clean_df.columns:
            available_cols = ", ".join(self.clean_df.columns.tolist())
            raise ValueError(f"Column '{column}' not found in DataFrame. Available columns: {available_cols}")
        
        threshold = threshold or self._default_thresholds['zscore_threshold']
        
        if threshold <= 0:
            raise ValueError("Threshold must be a positive value")
        
        if not pd.api.types.is_numeric_dtype(self.clean_df[column]):
            raise ValueError(f"Column '{column}' must be numeric for outlier detection")
        
        # Use detection method
        outlier_mask = self.detect_outliers_zscore(column, threshold)
        
        # If no outliers detected, record info and warn only when std is degenerate
        if not outlier_mask.any():
            mean, std, _ = self._calculate_zscore_stats(column, threshold)
            if std == 0 or pd.isna(std):
                warnings.warn(f"Column '{column}' has zero or NaN standard deviation. No outliers detected.")
            self.outlier_info[column] = {
                'method': 'Z-score',
                'column': column,
                'mean': mean,
                'std': std,
                'threshold': threshold,
                'num_outliers': 0,
                'percent_removed': 0.0,
                'outlier_indices': []
            }
            return self
        
        # Get outliers
        outliers = self.clean_df[outlier_mask]
        
        # Create a clean DataFrame without outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Prepare outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
            
        mean, std, _ = self._calculate_zscore_stats(column, threshold)
        
        outlier_info = {
            'method': 'Z-score',
            'column': column,
            'mean': mean,
            'std': std,
            'threshold': threshold,
            'num_outliers': len(outliers),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store outlier information
        self.outlier_info[column] = outlier_info
        
        return self
    
    def get_outlier_stats(self, columns: Optional[List[str]] = None, methods: List[str] = ['iqr', 'zscore'], iqr_factor: float = 1.5, zscore_threshold: float = 3.0, include_indices: bool = False) -> pd.DataFrame:
        """
        Get comprehensive statistics about potential outliers without removing them.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to analyze. If None, all numeric columns will be analyzed.
        methods : list, default=['iqr', 'zscore']
            List of methods to use for outlier detection
        iqr_factor : float, default=1.5
            The factor to multiply the IQR by for the IQR method
        zscore_threshold : float, default=3.0
            The Z-score threshold for the Z-score method
        include_indices : bool, default=False
            Whether to include outlier indices in the output
            
        Returns:
        --------
        pandas.DataFrame
            A DataFrame containing outlier statistics for each column and method
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        if self.clean_df.empty:
            raise ValueError("DataFrame is empty. Cannot analyze outliers.")
            
        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
            
        stats_data = []
        
        for column in columns:
            if not np.issubdtype(self.clean_df[column].dtype, np.number):
                print(f"Warning: Column '{column}' is not numeric. Skipping.")
                continue
                
            for method in methods:
                if method == 'iqr':
                    # Calculate IQR statistics
                    Q1 = self.clean_df[column].quantile(0.25)
                    Q3 = self.clean_df[column].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - (iqr_factor * IQR)
                    upper_bound = Q3 + (iqr_factor * IQR)
                    
                    outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
                    outlier_indices = self.clean_df[outlier_mask].index.tolist() if include_indices else None
                    
                    stats_data.append({
                        'Column': column,
                        'Method': 'IQR',
                        'Potential Outliers': outlier_mask.sum(),
                        'Percent Outliers': (outlier_mask.sum() / len(self.clean_df)) * 100,
                        'Lower Bound': lower_bound,
                        'Upper Bound': upper_bound,
                        'Q1': Q1,
                        'Q3': Q3,
                        'IQR': IQR,
                        'Outlier Indices': outlier_indices if include_indices else None
                    })
                
                elif method == 'zscore':
                    # Calculate Z-score statistics
                    zscore_col = f"{column}_zscore"
                    if zscore_col in self.clean_df.columns:
                        z_scores = np.abs(self.clean_df[zscore_col])
                    else:
                        mean = self.clean_df[column].mean()
                        std = self.clean_df[column].std()
                        z_scores = np.abs((self.clean_df[column] - mean) / std)
                    
                    outlier_mask = z_scores > zscore_threshold
                    outlier_indices = self.clean_df[outlier_mask].index.tolist() if include_indices else None
                    
                    stats_data.append({
                        'Column': column,
                        'Method': 'Z-score',
                        'Potential Outliers': outlier_mask.sum(),
                        'Percent Outliers': (outlier_mask.sum() / len(self.clean_df)) * 100,
                        'Threshold': zscore_threshold,
                        'Mean': self.clean_df[column].mean(),
                        'Std': self.clean_df[column].std(),
                        'Outlier Indices': outlier_indices if include_indices else None
                    })
        
        # Convert to DataFrame
        stats_df = pd.DataFrame(stats_data)
        
        # Format percentage with 2 decimal places
        if 'Percent Outliers' in stats_df.columns:
            stats_df['Percent Outliers'] = stats_df['Percent Outliers'].round(2)
        
        # Drop the Outlier Indices column if not requested
        if not include_indices and 'Outlier Indices' in stats_df.columns:
            stats_df = stats_df.drop('Outlier Indices', axis=1)
        
        return stats_df
        
    def plot_outlier_analysis(self, columns: Optional[Union[str, List[str]]] = None, methods: Optional[List[str]] = None, figsize: Tuple[int, int] = (15, 5)) -> Dict[str, Any]:
        """
        Generate comprehensive outlier analysis plots for specified columns.
        
        Parameters
        ----------
        columns : str or list of str, optional
            Column(s) to analyze. If None, analyzes all numeric columns.
            Column names are case-insensitive.
        methods : list of str, optional
            Outlier detection methods to use. If None, uses all available methods.
        figsize : tuple, optional
            Base figure size for each subplot (width, height). Default is (15, 5).
            
        Returns
        -------
        dict
            Dictionary of matplotlib figures keyed by column names.
        """
        if not hasattr(self, 'clean_df') or self.clean_df is None:
            raise ValueError("No data available. Please set data using set_data() first.")
        if self.clean_df.empty:
            raise ValueError("DataFrame is empty. Cannot generate plots.")

        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        elif isinstance(columns, str):
            columns = [columns]
        
        # Create case-insensitive column mapping
        column_map = {col.lower(): col for col in self.clean_df.columns}
        
        # Validate columns exist in the DataFrame (case-insensitive)
        invalid_columns = []
        resolved_columns = []
        for col in columns:
            col_lower = col.lower()
            if col_lower in column_map:
                resolved_columns.append(column_map[col_lower])
            else:
                invalid_columns.append(col)
        
        if invalid_columns:
            available_cols = "\n".join(self.clean_df.columns)
            raise ValueError(
                f"Column(s) {invalid_columns} not found in the dataset.\n"
                f"Available columns are:\n{available_cols}"
            )

        figures = {}
        for column in resolved_columns:
            if not pd.api.types.is_numeric_dtype(self.clean_df[column]):
                print(f"Warning: Skipping non-numeric column '{column}'")
                continue
            
            fig, axes = plt.subplots(1, 3, figsize=figsize)
            fig.suptitle(f'Outlier Analysis for {column}', fontsize=14)
            
            # Box plot - explicit axis for seaborn compatibility
            sns.boxplot(y=self.clean_df[column], ax=axes[0])
            axes[0].set_title('Box Plot')
            axes[0].set_xlabel(column)
            
            # Distribution plot with outlier thresholds
            sns.histplot(x=self.clean_df[column], ax=axes[1], kde=True)
            axes[1].set_title('Distribution Plot')
            axes[1].set_xlabel(column)
            
            # Q-Q plot
            stats.probplot(self.clean_df[column].dropna(), dist="norm", plot=axes[2])
            axes[2].set_title('Q-Q Plot')
            
            plt.tight_layout()
            figures[column] = fig
        
        return figures
        
    def compare_methods(self, columns=None, methods=None, iqr_factor=1.5, zscore_threshold=3.0):
        """
        Compare different outlier detection methods and their agreement.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to analyze. If None, all numeric columns will be analyzed.
        methods : list, default=['iqr', 'zscore']
            List of methods to compare
        iqr_factor : float, default=1.5
            The factor to multiply the IQR by for the IQR method
        zscore_threshold : float, default=3.0
            The Z-score threshold for the Z-score method
            
        Returns:
        --------
        dict
            A dictionary containing comparison metrics:
            {
                'column_name': {
                    'agreement_percentage': float,  # % of points where methods agree
                    'common_outliers': list,  # indices flagged by all methods
                    'method_specific_outliers': {  # indices unique to each method
                        'iqr': list,
                        'zscore': list
                    },
                    'summary': str  # Text summary of the comparison
                }
            }
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # Default methods if not provided
        if methods is None:
            methods = ['iqr', 'zscore']

        # Get outlier statistics
        stats_df = self.get_outlier_stats(columns, methods, iqr_factor, zscore_threshold)
        comparison = {}
        
        # Get unique columns from the stats DataFrame
        unique_columns = stats_df['Column'].unique()
        
        for column in unique_columns:
            comparison[column] = {}
            outliers_by_method = {}
            
            # Get outlier indices for each method
            if 'iqr' in methods:
                iqr_row = stats_df[(stats_df['Column'] == column) & (stats_df['Method'] == 'IQR')]
                if not iqr_row.empty:
                    Q1 = iqr_row['Q1'].iloc[0]
                    Q3 = iqr_row['Q3'].iloc[0]
                    IQR = iqr_row['IQR'].iloc[0]
                    lower_bound = Q1 - (iqr_factor * IQR)
                    upper_bound = Q3 + (iqr_factor * IQR)
                    outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
                    outliers_by_method['iqr'] = set(self.clean_df[outlier_mask].index.tolist())
            
            if 'zscore' in methods:
                zscore_row = stats_df[(stats_df['Column'] == column) & (stats_df['Method'] == 'Z-score')]
                if not zscore_row.empty:
                    zscore_col = f"{column}_zscore"
                    if zscore_col in self.clean_df.columns:
                        z_scores = np.abs(self.clean_df[zscore_col])
                    else:
                        mean = zscore_row['Mean'].iloc[0]
                        std = zscore_row['Std'].iloc[0]
                        z_scores = np.abs((self.clean_df[column] - mean) / std)
                    outlier_mask = z_scores > zscore_threshold
                    outliers_by_method['zscore'] = set(self.clean_df[outlier_mask].index.tolist())
            
            # Find common outliers across all methods
            if len(methods) > 1:
                common_outliers = set.intersection(*outliers_by_method.values())
                
                # Calculate method-specific outliers
                method_specific = {}
                for method in methods:
                    if method in outliers_by_method:
                        method_specific[method] = outliers_by_method[method] - common_outliers
                
                # Calculate agreement percentage
                all_outliers = set.union(*outliers_by_method.values())
                agreement_percentage = (len(common_outliers) / len(all_outliers) * 100) if all_outliers else 100.0
                
                comparison[column] = {
                    'agreement_percentage': agreement_percentage,
                    'common_outliers': sorted(list(common_outliers)),
                    'method_specific_outliers': {m: sorted(list(s)) for m, s in method_specific.items()},
                    'summary': f"""
                    Analysis for column '{column}':
                    - Total potential outliers: {len(all_outliers)}
                    - Outliers identified by all methods: {len(common_outliers)}
                    - Method agreement: {agreement_percentage:.1f}%
                    - Method-specific counts: {', '.join(f"{m}: {len(v)}" for m, v in method_specific.items())}
                    """
                }
            else:
                # If only one method, set its outliers as common
                method = methods[0]
                comparison[column] = {
                    'agreement_percentage': 100.0,
                    'common_outliers': sorted(list(outliers_by_method[method])),
                    'method_specific_outliers': {method: []},
                    'summary': f"""
                    Analysis for column '{column}':
                    - Total outliers identified by {method}: {len(outliers_by_method[method])}
                    """
                }
        
        return comparison
        
    def analyze_distribution(self, column: str) -> Dict[str, Any]:
        """
        Analyze the distribution of a column and recommend the best outlier detection method.
        
        Parameters:
        -----------
        column : str
            The name of the column to analyze
            
        Returns:
        --------
        dict
            Distribution analysis results including:
            - skewness
            - kurtosis
            - normality test results
            - recommended method
            - recommended thresholds
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        data = self.clean_df[column].dropna()
        
        # Calculate basic statistics
        skewness = data.skew()
        kurtosis = data.kurtosis()
        
        # Perform Shapiro-Wilk test for normality (handle large datasets)
        sample = data.sample(min(len(data), 5000)) if len(data) > 0 else data
        _, p_value = stats.shapiro(sample)
        
        # Calculate robust statistics
        median = data.median()
        mad = stats.median_abs_deviation(data)
        
        # Make recommendations
        if abs(skewness) > 2 or abs(kurtosis) > 7:
            recommended_method = 'iqr'
            recommended_threshold: Dict[str, float] = {
                'lower_factor': 2.0 if skewness < -1 else 1.5,
                'upper_factor': 2.0 if skewness > 1 else 1.5
            }
        elif p_value < 0.05:
            recommended_method = 'modified_zscore'
            recommended_threshold: float = 3.5
        else:
            recommended_method = 'zscore'
            recommended_threshold: float = 3.0
            
        return {
            'skewness': skewness,
            'kurtosis': kurtosis,
            'normality_p_value': p_value,
            'is_normal': p_value >= 0.05,
            'median': median,
            'mad': mad,
            'recommended_method': recommended_method,
            'recommended_threshold': recommended_threshold
        }
        
    def remove_outliers_modified_zscore(self, column: str, threshold: Optional[float] = None) -> 'StatClean':
        """
        Remove outliers using Modified Z-score method, which is more robust for skewed data.
        Uses Median Absolute Deviation (MAD) instead of standard deviation.
        
        Parameters:
        -----------
        column : str
            The name of the column to clean
        threshold : float, optional
            The modified Z-score threshold above which to consider a point an outlier. Uses default if None.
            
        Returns:
        --------
        StatClean
            Self for method chaining
            
        Raises:
        -------
        ValueError
            If no DataFrame is set, column doesn't exist, or threshold is negative
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        if column not in self.clean_df.columns:
            available_cols = ", ".join(self.clean_df.columns.tolist())
            raise ValueError(f"Column '{column}' not found in DataFrame. Available columns: {available_cols}")
        
        threshold = threshold or self._default_thresholds['modified_zscore_threshold']
        
        if threshold <= 0:
            raise ValueError("Threshold must be a positive value")
        
        if not pd.api.types.is_numeric_dtype(self.clean_df[column]):
            raise ValueError(f"Column '{column}' must be numeric for outlier detection")
        
        # Use detection method
        outlier_mask = self.detect_outliers_modified_zscore(column, threshold)
        
        # If no outliers detected (due to zero MAD), return early
        if not outlier_mask.any():
            median, mad, _ = self._calculate_modified_zscore_stats(column, threshold)
            print(f"Warning: MAD is zero for column '{column}'. No outliers detected.")
            self.outlier_info[column] = {
                'method': 'Modified Z-score',
                'column': column,
                'median': median,
                'mad': mad,
                'threshold': threshold,
                'num_outliers': 0,
                'percent_removed': 0.0,
                'outlier_indices': []
            }
            return self
        
        # Get outliers
        outliers = self.clean_df[outlier_mask]
        
        # Create a clean DataFrame without outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Prepare outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
            
        median, mad, _ = self._calculate_modified_zscore_stats(column, threshold)
        
        outlier_info = {
            'method': 'Modified Z-score',
            'column': column,
            'median': median,
            'mad': mad,
            'threshold': threshold,
            'num_outliers': len(outliers),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store outlier information
        self.outlier_info[column] = outlier_info
        
        return self
    
    # Batch processing methods
    def apply_cleaning_strategy(self, strategy: Dict[str, Dict[str, Any]]) -> 'StatClean':
        """
        Apply a custom cleaning strategy to multiple columns.
        
        Parameters:
        -----------
        strategy : dict
            Dictionary mapping column names to cleaning configurations.
            Format: {'column_name': {'method': 'iqr', 'threshold': 2.0, ...}}
            
        Returns:
        --------
        StatClean
            Self for method chaining
        
        Example:
        --------
        strategy = {
            'price': {'method': 'iqr', 'lower_factor': 1.5, 'upper_factor': 1.5},
            'age': {'method': 'zscore', 'threshold': 2.5},
            'income': {'method': 'modified_zscore', 'threshold': 3.5}
        }
        cleaner.apply_cleaning_strategy(strategy)
        """
        for column, config in strategy.items():
            method = config.get('method', 'auto')
            
            if method == 'iqr':
                self.remove_outliers_iqr(column, 
                                       lower_factor=config.get('lower_factor'),
                                       upper_factor=config.get('upper_factor'))
            elif method == 'zscore':
                self.remove_outliers_zscore(column, threshold=config.get('threshold'))
            elif method == 'modified_zscore':
                self.remove_outliers_modified_zscore(column, threshold=config.get('threshold'))
            elif method == 'auto':
                analysis = self.analyze_distribution(column)
                recommended_method = analysis['recommended_method']
                recommended_threshold = analysis['recommended_threshold']
                
                if recommended_method == 'iqr':
                    self.remove_outliers_iqr(column, 
                                           lower_factor=recommended_threshold['lower_factor'],
                                           upper_factor=recommended_threshold['upper_factor'])
                elif recommended_method == 'modified_zscore':
                    self.remove_outliers_modified_zscore(column, threshold=recommended_threshold)
                else:
                    self.remove_outliers_zscore(column, threshold=recommended_threshold)
        
        return self
    
    def detect_all_outliers(self, columns: Optional[List[str]] = None, 
                           methods: Optional[List[str]] = None) -> Dict[str, Dict[str, pd.Series]]:
        """
        Detect outliers in multiple columns using multiple methods without removing them.
        
        Parameters:
        -----------
        columns : list, optional
            Columns to analyze. If None, all numeric columns.
        methods : list, optional
            Methods to use. If None, uses ['iqr', 'zscore', 'modified_zscore'].
            
        Returns:
        --------
        dict
            Nested dictionary: {column: {method: boolean_mask}}
        """
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
        
        if methods is None:
            methods = ['iqr', 'zscore', 'modified_zscore']
        
        results = {}
        for column in columns:
            results[column] = {}
            for method in methods:
                if method == 'iqr':
                    results[column][method] = self.detect_outliers_iqr(column)
                elif method == 'zscore':
                    results[column][method] = self.detect_outliers_zscore(column)
                elif method == 'modified_zscore':
                    results[column][method] = self.detect_outliers_modified_zscore(column)
        
        return results
    
    # Winsorizing methods (alternative to removal)
    def winsorize_outliers_iqr(self, column: str, lower_factor: Optional[float] = None, 
                              upper_factor: Optional[float] = None) -> 'StatClean':
        """
        Winsorize outliers using IQR method (cap values instead of removing).
        
        Parameters:
        -----------
        column : str
            The name of the column to winsorize
        lower_factor : float, optional
            The factor to multiply the IQR by for the lower bound
        upper_factor : float, optional  
            The factor to multiply the IQR by for the upper bound
            
        Returns:
        --------
        StatClean
            Self for method chaining
        """
        self._validate_column(column)
        lower_bound, upper_bound, stats = self._calculate_iqr_bounds(column, lower_factor, upper_factor)
        
        # Identify outliers
        original_values = self.clean_df[column].copy()
        outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
        
        # Winsorize (cap) the values
        self.clean_df[column] = self.clean_df[column].clip(lower_bound, upper_bound)
        
        # Track winsorization info
        num_winsorized = outlier_mask.sum()
        num_lower = (original_values < lower_bound).sum()
        num_upper = (original_values > upper_bound).sum()
        
        winsorize_info = {
            'method': 'IQR Winsorizing',
            'column': column,
            'Q1': stats['Q1'],
            'Q3': stats['Q3'], 
            'IQR': stats['IQR'],
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'num_winsorized': num_winsorized,
            'num_winsorized_lower': num_lower,
            'num_winsorized_upper': num_upper,
            'percent_winsorized': (num_winsorized / len(self.clean_df)) * 100,
            'winsorized_indices': self.clean_df[outlier_mask].index.tolist()
        }
        
        self.outlier_info[column] = winsorize_info
        return self
    
    def winsorize_outliers_zscore(self, column: str, threshold: Optional[float] = None) -> 'StatClean':
        """
        Winsorize outliers using Z-score method (cap values instead of removing).
        
        Parameters:
        -----------
        column : str
            The name of the column to winsorize
        threshold : float, optional
            The Z-score threshold above which to winsorize values
            
        Returns:
        --------
        StatClean
            Self for method chaining
        """
        self._validate_column(column)
        mean, std, threshold = self._calculate_zscore_stats(column, threshold)
        
        if std == 0 or pd.isna(std):
            print(f"Warning: Column '{column}' has zero or NaN standard deviation. No winsorization applied.")
            return self
        
        # Calculate bounds
        lower_bound = mean - threshold * std
        upper_bound = mean + threshold * std
        
        # Identify and winsorize outliers
        original_values = self.clean_df[column].copy()
        outlier_mask = (np.abs((self.clean_df[column] - mean) / std) > threshold)
        
        self.clean_df[column] = self.clean_df[column].clip(lower_bound, upper_bound)
        
        # Track winsorization info
        num_winsorized = outlier_mask.sum()
        
        winsorize_info = {
            'method': 'Z-score Winsorizing',
            'column': column,
            'mean': mean,
            'std': std,
            'threshold': threshold,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'num_winsorized': num_winsorized,
            'percent_winsorized': (num_winsorized / len(self.clean_df)) * 100,
            'winsorized_indices': self.clean_df[outlier_mask].index.tolist()
        }
        
        self.outlier_info[column] = winsorize_info
        return self
    
    def winsorize_outliers_percentile(self, column: str, lower_percentile: float = 5.0, 
                                    upper_percentile: float = 95.0) -> 'StatClean':
        """
        Winsorize outliers using percentile method.
        
        Parameters:
        -----------
        column : str
            The name of the column to winsorize
        lower_percentile : float, default=5.0
            Lower percentile for winsorization (0-100)
        upper_percentile : float, default=95.0
            Upper percentile for winsorization (0-100)
            
        Returns:
        --------
        StatClean
            Self for method chaining
        """
        self._validate_column(column)
        
        if not (0 <= lower_percentile < upper_percentile <= 100):
            raise ValueError("Percentiles must be between 0-100 and lower < upper")
        
        # Calculate percentile bounds
        lower_bound = self.clean_df[column].quantile(lower_percentile / 100.0)
        upper_bound = self.clean_df[column].quantile(upper_percentile / 100.0)
        
        # Identify and winsorize outliers
        original_values = self.clean_df[column].copy()
        outlier_mask = (self.clean_df[column] < lower_bound) | (self.clean_df[column] > upper_bound)
        
        self.clean_df[column] = self.clean_df[column].clip(lower_bound, upper_bound)
        
        # Track winsorization info
        num_winsorized = outlier_mask.sum()
        num_lower = (original_values < lower_bound).sum()
        num_upper = (original_values > upper_bound).sum()
        
        winsorize_info = {
            'method': 'Percentile Winsorizing',
            'column': column,
            'lower_percentile': lower_percentile,
            'upper_percentile': upper_percentile,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'num_winsorized': num_winsorized,
            'num_winsorized_lower': num_lower,
            'num_winsorized_upper': num_upper,
            'percent_winsorized': (num_winsorized / len(self.clean_df)) * 100,
            'winsorized_indices': self.clean_df[outlier_mask].index.tolist()
        }
        
        self.outlier_info[column] = winsorize_info
        return self
    
    # Multivariate outlier detection
    def detect_outliers_mahalanobis(self, columns: Optional[List[str]] = None, 
                                   chi2_threshold: Optional[float] = None,
                                   use_shrinkage: bool = False) -> pd.Series:
        """
        Detect multivariate outliers using Mahalanobis distance.
        
        Parameters:
        -----------
        columns : list, optional
            List of columns to include in multivariate analysis. 
            If None, uses all numeric columns.
        chi2_threshold : float, optional
            Chi-square threshold for outlier detection.
            If None, uses 97.5th percentile of chi-square distribution.
            
        Returns:
        --------
        pandas.Series
            Boolean mask where True indicates outliers
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
        
        # Select columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
        
        if len(columns) < 2:
            raise ValueError("Mahalanobis distance requires at least 2 numeric columns")
        
        # Validate all columns exist and are numeric
        for col in columns:
            if col not in self.clean_df.columns:
                available_cols = ", ".join(self.clean_df.columns.tolist())
                raise ValueError(f"Column '{col}' not found in DataFrame. Available columns: {available_cols}")
            if not pd.api.types.is_numeric_dtype(self.clean_df[col]):
                raise ValueError(f"Column '{col}' must be numeric for Mahalanobis distance")
        
        # Extract data and remove missing values
        data = self.clean_df[columns].dropna()
        if len(data) == 0:
            raise ValueError("No complete cases available after removing missing values")
        
        n_features = len(columns)
        n_samples = len(data)
        
        if n_samples <= n_features:
            raise ValueError(f"Need more observations ({n_samples}) than features ({n_features}) for Mahalanobis distance")
        
        # Calculate mean and covariance matrix (optionally using shrinkage estimator)
        try:
            mean = data.mean()
            if use_shrinkage:
                try:
                    # Lazy import to avoid hard dependency
                    from sklearn.covariance import LedoitWolf  # type: ignore
                    lw = LedoitWolf().fit(data.values)
                    inv_cov_matrix = lw.precision_
                    cov_values = lw.covariance_
                except Exception as e:
                    warnings.warn(f"Shrinkage covariance (Ledoit-Wolf) unavailable ({e}); falling back to sample covariance.")
                    cov_values = data.cov().values
                    try:
                        inv_cov_matrix = np.linalg.inv(cov_values)
                    except np.linalg.LinAlgError:
                        warnings.warn("Covariance inversion failed; using pseudoinverse (pinv).")
                        inv_cov_matrix = np.linalg.pinv(cov_values)
            else:
                cov_values = data.cov().values
                # Compute inverse or pseudoinverse with conditioning checks
                try:
                    det = np.linalg.det(cov_values)
                except Exception:
                    det = None
                if det is not None and det == 0:
                    warnings.warn("Covariance matrix is singular; using pseudoinverse (pinv) for Mahalanobis distance.")
                    inv_cov_matrix = np.linalg.pinv(cov_values)
                else:
                    try:
                        inv_cov_matrix = np.linalg.inv(cov_values)
                    except np.linalg.LinAlgError:
                        warnings.warn("Covariance inversion failed; using pseudoinverse (pinv).")
                        inv_cov_matrix = np.linalg.pinv(cov_values)
            # Warn on ill-conditioning
            try:
                cond = np.linalg.cond(cov_values)
                if cond > 1e12:
                    warnings.warn(f"Covariance matrix is ill-conditioned (cond={cond:.2e}); results may be unstable.")
            except Exception:
                pass
        except Exception as e:
            raise ValueError(f"Could not compute covariance inverse: {e}")
        
        # Calculate Mahalanobis distances
        def mahalanobis_distance(row):
            diff = row - mean
            return np.sqrt(diff.T @ inv_cov_matrix @ diff)
        
        mahal_distances = data.apply(mahalanobis_distance, axis=1)
        
        # Convert to chi-square statistics (square of Mahalanobis distance)
        chi2_stats = mahal_distances ** 2
        
        # Set threshold
        if chi2_threshold is None:
            chi2_threshold = chi2.ppf(0.975, df=n_features)  # 97.5th percentile
        elif 0 < chi2_threshold <= 1:
            # Interpret as percentile and convert to chi-square statistic
            chi2_threshold = chi2.ppf(chi2_threshold, df=n_features)
        
        # Create boolean mask for all rows in the original dataframe
        outlier_mask = pd.Series(False, index=self.clean_df.index)
        outlier_mask.loc[data.index] = chi2_stats > chi2_threshold
        
        return outlier_mask
    
    def remove_outliers_mahalanobis(self, columns: Optional[List[str]] = None, 
                                   chi2_threshold: Optional[float] = None,
                                   use_shrinkage: bool = False) -> 'StatClean':
        """
        Remove multivariate outliers using Mahalanobis distance.
        
        Parameters:
        -----------
        columns : list, optional
            List of columns to include in multivariate analysis
        chi2_threshold : float, optional
            Chi-square threshold for outlier detection
            
        Returns:
        --------
        StatClean
            Self for method chaining
        """
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
        
        # Get outlier mask
        outlier_mask = self.detect_outliers_mahalanobis(columns, chi2_threshold, use_shrinkage=use_shrinkage)
        outliers = self.clean_df[outlier_mask]
        
        # Remove outliers
        self.clean_df = self.clean_df[~outlier_mask].copy()
        
        # Reset index if not preserving
        if not self.preserve_index:
            self.clean_df.reset_index(drop=True, inplace=True)
        
        # Calculate threshold if not provided
        if chi2_threshold is None:
            chi2_threshold = chi2.ppf(0.975, df=len(columns))
        
        # Store outlier information
        if self.original_df is None:
            raise ValueError("Original DataFrame is None")
        
        outlier_info = {
            'method': 'Mahalanobis Distance',
            'columns': columns,
            'chi2_threshold': chi2_threshold,
            'degrees_of_freedom': len(columns),
            'num_outliers': len(outliers),
            'percent_removed': (len(outliers) / len(self.original_df)) * 100,
            'outlier_indices': outliers.index.tolist()
        }
        
        # Store info using first column name as key
        key = f"multivariate_{columns[0]}" if columns else "multivariate"
        self.outlier_info[key] = outlier_info
        
        return self
    
    # Data transformation methods
    def transform_boxcox(self, column: str, lambda_param: Optional[float] = None) -> Tuple['StatClean', Dict[str, Any]]:
        """
        Apply Box-Cox transformation to reduce skewness and make data more normal.
        
        Parameters:
        -----------
        column : str
            The name of the column to transform
        lambda_param : float, optional
            Lambda parameter for Box-Cox. If None, optimal lambda is estimated.
            
        Returns:
        --------
        tuple
            (self, transformation_info) containing the cleaner and transformation details
        """
        self._validate_column(column)
        
        original_data = self.clean_df[column].copy()
        
        # Box-Cox requires positive values
        if (original_data <= 0).any():
            min_val = original_data.min()
            shift = abs(min_val) + 1
            data_to_transform = original_data + shift
            warnings.warn(f"Column '{column}' contains non-positive values. Shifting by {shift}")
        else:
            data_to_transform = original_data
            shift = 0
        
        try:
            non_na_mask = data_to_transform.notna()
            if lambda_param is None:
                # Find optimal lambda using non-NA values
                _, optimal_lambda = boxcox(data_to_transform[non_na_mask])
                # Apply to non-NA values only
                transformed_full = data_to_transform.copy()
                transformed_full[non_na_mask] = boxcox(data_to_transform[non_na_mask], lmbda=optimal_lambda)
                self.clean_df[column] = transformed_full
            else:
                # Use specified lambda
                transformed_full = data_to_transform.copy()
                transformed_full[non_na_mask] = boxcox(data_to_transform[non_na_mask], lmbda=lambda_param)
                self.clean_df[column] = transformed_full
                optimal_lambda = lambda_param
                
        except Exception as e:
            raise ValueError(f"Box-Cox transformation failed: {str(e)}")
        
        # Calculate transformation statistics
        transformed_skewness = self.clean_df[column].skew()
        original_skewness = original_data.skew()
        
        transform_info = {
            'method': 'Box-Cox',
            'column': column,
            'lambda': optimal_lambda,
            'shift_applied': shift,
            'original_skewness': original_skewness,
            'transformed_skewness': transformed_skewness,
            'skewness_improvement': abs(original_skewness) - abs(transformed_skewness)
        }
        
        return self, transform_info
    
    def transform_log(self, column: str, base: str = 'natural') -> Tuple['StatClean', Dict[str, Any]]:
        """
        Apply logarithmic transformation to reduce right skewness.
        
        Parameters:
        -----------
        column : str
            The name of the column to transform
        base : str, default='natural'
            Base of logarithm ('natural', '10', '2')
            
        Returns:
        --------
        tuple
            (self, transformation_info)
        """
        self._validate_column(column)
        
        original_data = self.clean_df[column].copy()
        
        # Log requires positive values
        if (original_data <= 0).any():
            min_val = original_data.min()
            shift = abs(min_val) + 1
            data_to_transform = original_data + shift
            warnings.warn(f"Column '{column}' contains non-positive values. Shifting by {shift}")
        else:
            data_to_transform = original_data
            shift = 0
        
        # Apply transformation based on base
        if base == 'natural':
            self.clean_df[column] = np.log(data_to_transform)
            base_used = math.e
        elif base == '10':
            self.clean_df[column] = np.log10(data_to_transform)
            base_used = 10
        elif base == '2':
            self.clean_df[column] = np.log2(data_to_transform)
            base_used = 2
        else:
            raise ValueError("Base must be 'natural', '10', or '2'")
        
        # Calculate transformation statistics
        transformed_skewness = self.clean_df[column].skew()
        original_skewness = original_data.skew()
        
        transform_info = {
            'method': f'Log (base {base})',
            'column': column,
            'base': base_used,
            'shift_applied': shift,
            'original_skewness': original_skewness,
            'transformed_skewness': transformed_skewness,
            'skewness_improvement': abs(original_skewness) - abs(transformed_skewness)
        }
        
        return self, transform_info
    
    def transform_sqrt(self, column: str) -> Tuple['StatClean', Dict[str, Any]]:
        """
        Apply square root transformation to reduce right skewness.
        
        Parameters:
        -----------
        column : str
            The name of the column to transform
            
        Returns:
        --------
        tuple
            (self, transformation_info)
        """
        self._validate_column(column)
        
        original_data = self.clean_df[column].copy()
        
        # Square root requires non-negative values
        if (original_data < 0).any():
            min_val = original_data.min()
            shift = abs(min_val)
            data_to_transform = original_data + shift
            warnings.warn(f"Column '{column}' contains negative values. Shifting by {shift}")
        else:
            data_to_transform = original_data
            shift = 0
        
        # Apply transformation
        self.clean_df[column] = np.sqrt(data_to_transform)
        
        # Calculate transformation statistics
        transformed_skewness = self.clean_df[column].skew()
        original_skewness = original_data.skew()
        
        transform_info = {
            'method': 'Square Root',
            'column': column,
            'shift_applied': shift,
            'original_skewness': original_skewness,
            'transformed_skewness': transformed_skewness,
            'skewness_improvement': abs(original_skewness) - abs(transformed_skewness)
        }
        
        return self, transform_info
    
    def recommend_transformation(self, column: str) -> Dict[str, Any]:
        """
        Recommend the best transformation for a column based on its distribution.
        
        Parameters:
        -----------
        column : str
            The name of the column to analyze
            
        Returns:
        --------
        dict
            Recommendation including suggested method and expected improvement
        """
        self._validate_column(column)
        
        data = self.clean_df[column].dropna()
        original_skewness = data.skew()
        
        # Test different transformations (on a copy)
        temp_cleaner = StatClean(pd.DataFrame({column: data}))
        recommendations = []
        
        # Test transformations if data allows
        try:
            if (data > 0).all():
                # Test Box-Cox
                try:
                    _, boxcox_info = temp_cleaner.transform_boxcox(column)
                    recommendations.append(boxcox_info)
                except:
                    pass
                
                # Test Log
                temp_cleaner.clean_df[column] = data.copy()
                _, log_info = temp_cleaner.transform_log(column, 'natural')
                recommendations.append(log_info)
                
            if (data >= 0).all():
                # Test Square root
                temp_cleaner.clean_df[column] = data.copy()
                _, sqrt_info = temp_cleaner.transform_sqrt(column)
                recommendations.append(sqrt_info)
                
        except Exception as e:
            warnings.warn(f"Could not test all transformations: {str(e)}")
        
        # Find best transformation
        if recommendations:
            best_transform = max(recommendations, key=lambda x: x['skewness_improvement'])
            
            return {
                'column': column,
                'original_skewness': original_skewness,
                'recommended_method': best_transform['method'],
                'expected_improvement': best_transform['skewness_improvement'],
                'all_results': recommendations
            }
        else:
            return {
                'column': column,
                'original_skewness': original_skewness,
                'recommended_method': 'None (no suitable transformations)',
                'expected_improvement': 0,
                'all_results': []
            }
        
    def clean_columns(self, columns: Optional[List[str]] = None, method: str = 'auto', show_progress: bool = True, include_indices: bool = False, **kwargs: Any) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Clean multiple columns using the most appropriate method for each column.
        
        Parameters:
        -----------
        columns : list or None, default=None
            List of columns to clean. If None, all numeric columns will be used.
        method : str, default='auto'
            Method to use for cleaning:
            - 'auto': Automatically choose best method based on distribution
            - 'iqr': Use IQR method
            - 'zscore': Use Z-score method
            - 'modified_zscore': Use Modified Z-score method
        show_progress : bool, default=True
            Whether to show a progress bar during cleaning
        include_indices : bool, default=False
            Whether to include outlier indices in the output DataFrame
        **kwargs:
            Additional arguments to pass to the cleaning methods:
            - threshold: for Z-score methods
            - lower_factor, upper_factor: for IQR method
            
        Returns:
        --------
        tuple
            - pandas.DataFrame: The cleaned DataFrame
            - pandas.DataFrame: Summary of outlier statistics for each column
        """
        if self.clean_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        # If no columns specified, use all numeric columns
        if columns is None:
            columns = self.clean_df.select_dtypes(include=np.number).columns.tolist()
            
        # Create progress bar if requested
        columns_to_iterate = tqdm(columns, desc="Cleaning columns") if show_progress else columns
            
        cleaning_results = []
        
        for column in columns_to_iterate:
            if method == 'auto':
                # Analyze distribution and get recommended method
                analysis = self.analyze_distribution(column)
                recommended_method = analysis['recommended_method']
                recommended_threshold = analysis['recommended_threshold']
                
                if recommended_method == 'iqr':
                    self.remove_outliers_iqr(column, 
                                           lower_factor=recommended_threshold['lower_factor'],
                                           upper_factor=recommended_threshold['upper_factor'])
                elif recommended_method == 'modified_zscore':
                    self.remove_outliers_modified_zscore(column, threshold=recommended_threshold)
                else:
                    self.remove_outliers_zscore(column, threshold=recommended_threshold)
            else:
                if method == 'iqr':
                    self.remove_outliers_iqr(column, **kwargs)
                elif method == 'zscore':
                    self.remove_outliers_zscore(column, **kwargs)
                elif method == 'modified_zscore':
                    self.remove_outliers_modified_zscore(column, **kwargs)
                else:
                    available_methods = ['iqr', 'zscore', 'modified_zscore', 'auto']
                    raise ValueError(f"Unknown method '{method}'. Available methods: {', '.join(available_methods)}")
            
            # Get the outlier info for this column
            info = self.outlier_info[column]
            
            # Create a summary row
            summary = {
                'Column': column,
                'Method': info['method'],
                'Outliers Found': info['num_outliers'],
                'Percent Removed': round(info['percent_removed'], 2)
            }
            
            # Add method-specific statistics
            if info['method'] == 'IQR':
                summary.update({
                    'Lower Bound': info['lower_bound'],
                    'Upper Bound': info['upper_bound'],
                    'Q1': info['Q1'],
                    'Q3': info['Q3'],
                    'IQR': info['IQR'],
                    'Below Lower': info.get('num_outliers_below', '-'),
                    'Above Upper': info.get('num_outliers_above', '-')
                })
            elif info['method'] in ['Z-score', 'Modified Z-score']:
                if info['method'] == 'Z-score':
                    summary.update({
                        'Mean': info['mean'],
                        'Std': info['std'],
                        'Threshold': info['threshold']
                    })
                else:
                    summary.update({
                        'Median': info['median'],
                        'MAD': info['mad'],
                        'Threshold': info['threshold']
                    })
            
            # Add outlier indices if requested
            if include_indices:
                summary['Outlier Indices'] = info.get('outlier_indices', [])
                
            cleaning_results.append(summary)
        
        # Convert results to DataFrame
        results_df = pd.DataFrame(cleaning_results)
        
        # Reorder columns for better presentation
        column_order = ['Column', 'Method', 'Outliers Found', 'Percent Removed']
        if 'Lower Bound' in results_df.columns:
            column_order.extend(['Lower Bound', 'Upper Bound', 'Q1', 'Q3', 'IQR', 'Below Lower', 'Above Upper'])
        if 'Mean' in results_df.columns:
            column_order.extend(['Mean', 'Std', 'Threshold'])
        if 'Median' in results_df.columns:
            column_order.extend(['Median', 'MAD', 'Threshold'])
        if include_indices and 'Outlier Indices' in results_df.columns:
            column_order.append('Outlier Indices')
            
        results_df = results_df[column_order]
        
        return self.clean_df, results_df
    
    def visualize_outliers(self, column: str) -> None:
        """
        Visualize the distribution of data and highlight outliers.
        
        Parameters:
        -----------
        column : str
            The name of the column to visualize
        """
        if self.original_df is None:
            raise ValueError("No DataFrame has been set. Use set_data() first.")
            
        if column not in self.outlier_info:
            processed_cols = ", ".join(self.outlier_info.keys()) if self.outlier_info else "None"
            raise ValueError(f"No outlier information found for column '{column}'. Processed columns: {processed_cols}. Run outlier removal first.")
            
        outlier_info = self.outlier_info[column]
        
        plt.figure(figsize=(12, 6))
        
        # Create subplot for the boxplot
        plt.subplot(1, 2, 1)
        sns.boxplot(y=self.original_df[column])
        plt.title(f'Boxplot of {column}')
        
        # Create subplot for the histogram
        plt.subplot(1, 2, 2)
        sns.histplot(self.original_df[column], kde=True)
        
        if outlier_info['method'] == 'IQR':
            plt.axvline(outlier_info['lower_bound'], color='r', linestyle='--', 
                       label=f"Lower bound: {outlier_info['lower_bound']:.2f}")
            plt.axvline(outlier_info['upper_bound'], color='r', linestyle='--',
                       label=f"Upper bound: {outlier_info['upper_bound']:.2f}")
        else:
            # Calculate bounds for z-score or modified z-score visualization
            method = outlier_info['method']
            if method == 'Z-score':
                mean = outlier_info['mean']
                std = outlier_info['std']
                threshold = outlier_info['threshold']
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                label_suffix = 'Z'
            else:  # Modified Z-score visualization: approximate bounds using median and MAD
                median = outlier_info['median']
                mad = outlier_info['mad']
                threshold = outlier_info['threshold']
                # Approximate bounds based on modified z-score definition
                lower_bound = median - (threshold * mad / 0.6745)
                upper_bound = median + (threshold * mad / 0.6745)
                label_suffix = 'Modified Z'

            plt.axvline(lower_bound, color='r', linestyle='--',
                        label=f"Lower bound ({label_suffix}): {lower_bound:.2f}")
            plt.axvline(upper_bound, color='r', linestyle='--',
                        label=f"Upper bound ({label_suffix}): {upper_bound:.2f}")
        
        plt.title(f'Distribution of {column} with Outlier Bounds')
        plt.legend()
        
        plt.tight_layout()
        plt.show()
        
        self._print_outlier_summary(column)
    
    def _print_outlier_summary(self, column: str) -> None:
        """
        Print a summary of outliers for a specific column.
        
        Parameters:
        -----------
        column : str
            The name of the column to summarize
        """
        if column not in self.outlier_info:
            processed_cols = ", ".join(self.outlier_info.keys()) if self.outlier_info else "None"
            raise ValueError(f"No outlier information found for column '{column}'. Processed columns: {processed_cols}")
            
        outlier_info = self.outlier_info[column]
        
        print(f"Outlier Summary ({outlier_info['method']} method):")
        print(f"- Column: {column}")
        print(f"- Number of outliers: {outlier_info['num_outliers']} ({outlier_info['percent_removed']:.2f}%)")
        if outlier_info['method'] == 'IQR':
            print(f"- Outliers below lower bound: {outlier_info['num_outliers_below']}")
            print(f"- Outliers above upper bound: {outlier_info['num_outliers_above']}")
    
    def get_summary_report(self) -> Dict[str, Any]:
        """
        Generate a summary report of all outlier removal operations.
        
        Returns:
        --------
        dict
            Summary report of all operations
        """
        if not self.outlier_info:
            return {"status": "No outlier removal operations performed yet"}
            
        if self.original_df is None or self.clean_df is None:
            raise ValueError("DataFrames are None")
            
        total_rows_before = len(self.original_df)
        total_rows_after = len(self.clean_df)
        percent_removed = ((total_rows_before - total_rows_after) / total_rows_before) * 100
        
        summary = {
            "original_shape": self.original_df.shape,
            "clean_shape": self.clean_df.shape,
            "total_rows_removed": total_rows_before - total_rows_after,
            "percent_removed": percent_removed,
            "columns_processed": list(self.outlier_info.keys()),
            "column_details": self.outlier_info
        }
        
        return summary
    
    def reset(self) -> None:
        """
        Reset the cleaner to the original DataFrame and clear all cached data.
        """
        if self.original_df is not None:
            self.clean_df = self.original_df.copy()
            self.outlier_info = {}
            # Clear stats cache if it exists
            if hasattr(self, '_stats_cache'):
                self._stats_cache = {}

    def get_outlier_indices(self, column: Optional[str] = None) -> Dict[str, List[int]]:
        """
        Get the indices of outliers for specified column(s).
        
        Parameters:
        -----------
        column : str or None, default=None
            Column name to get outlier indices for.
            If None, returns indices for all columns that have been cleaned.
            
        Returns:
        --------
        dict
            Dictionary mapping column names to lists of outlier indices.
            For columns without outlier information, returns an empty list.
        """
        if column is not None:
            if column not in self.outlier_info:
                return {column: []}
            info = self.outlier_info[column]
            return {column: info.get('outlier_indices', [])}
        
        return {col: info.get('outlier_indices', []) 
               for col, info in self.outlier_info.items()}


# Example usage:
def example():
    """
    Example demonstrating how to use the StatClean class.
    
    This example showcases both traditional and advanced statistical methods
    for outlier detection and data cleaning.
    """
    # Create a sample DataFrame
    np.random.seed(42)
    data = {
        'normal_data': np.random.normal(0, 1, 1000),
        'skewed_data': np.random.exponential(2, 1000),
        'categorical': np.random.choice(['A', 'B', 'C'], 1000)
    }
    df = pd.DataFrame(data)
    
    # Add some outliers
    df.loc[0, 'normal_data'] = 15  # Add a high outlier
    df.loc[1, 'normal_data'] = -12  # Add a low outlier
    df.loc[2, 'skewed_data'] = 30  # Add a high outlier
    
    # Create a StatClean instance
    cleaner = StatClean(df)
    
    # Example 1: Formal Statistical Testing
    print("=== Formal Statistical Testing ===")
    grubbs_result = cleaner.grubbs_test('normal_data')
    print(f"Grubbs' test p-value: {grubbs_result['p_value']:.4f}")
    print(f"Outlier detected: {grubbs_result['is_outlier']}")
    
    # Example 2: Method Chaining with Configuration
    print("\n=== Method Chaining ===")
    cleaner.set_thresholds(zscore_threshold=2.5, iqr_lower_factor=2.0)\
           .add_zscore_columns(['normal_data'])\
           .winsorize_outliers_iqr('skewed_data')
    
    # Example 3: Multivariate Outlier Detection
    print("\n=== Multivariate Analysis ===")
    outliers = cleaner.detect_outliers_mahalanobis(['normal_data', 'skewed_data'])
    print(f"Multivariate outliers detected: {outliers.sum()}")
    
    # Reset for traditional methods
    cleaner.reset()
    
    # Method 1: Clean a specific column using IQR
    print("Cleaning 'normal_data' with IQR method:")
    cleaner.remove_outliers_iqr('normal_data')
    cleaner.visualize_outliers('normal_data')
    
    # Reset to original data
    cleaner.reset()
    
    # Method 2: Clean a specific column using Z-score
    print("\nCleaning 'normal_data' with Z-score method:")
    cleaner.remove_outliers_zscore('normal_data', threshold=2.5)
    cleaner.visualize_outliers('normal_data')
    
    # Reset to original data
    cleaner.reset()
    
    # Method 3: Clean multiple columns at once
    print("\nCleaning multiple columns with IQR method:")
    cleaner.clean_columns(method='iqr', columns=['normal_data', 'skewed_data'])
    
    # Get a summary report
    report = cleaner.get_summary_report()
    print("\nSummary Report:")
    for key, value in report.items():
        if key != "column_details":
            print(f"- {key}: {value}")
            
    # Visualize the results for all processed columns
    for column in report["columns_processed"]:
        cleaner.visualize_outliers(column)


if __name__ == "__main__":
    example()