"""
Utility functions for outlier visualization and plotting.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Union, Optional
from scipy import stats

def plot_outliers(data: Union[pd.Series, np.ndarray], 
                 outliers: Union[pd.Series, np.ndarray],
                 title: Optional[str] = None,
                 figsize: tuple = (10, 6)) -> None:
    """
    Plot data points highlighting the outliers.
    
    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        The original data points
    outliers : Union[pd.Series, np.ndarray]
        Boolean mask or indices indicating outlier points
    title : Optional[str]
        Title for the plot
    figsize : tuple
        Figure size as (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Convert data to numpy array if it's a pandas Series
    if isinstance(data, pd.Series):
        data = data.values
    if isinstance(outliers, pd.Series):
        outliers = outliers.values
    
    # Create index array for x-axis
    x = np.arange(len(data))
    
    # Plot all points
    plt.scatter(x[~outliers], data[~outliers], c='blue', label='Normal Points')
    plt.scatter(x[outliers], data[outliers], c='red', label='Outliers')
    
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title(title or 'Outlier Detection Results')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

def plot_distribution(data: Union[pd.Series, np.ndarray],
                     outliers: Optional[Union[pd.Series, np.ndarray]] = None,
                     title: Optional[str] = None,
                     figsize: tuple = (10, 6)) -> None:
    """
    Plot the distribution of data points with optional outlier highlighting.
    
    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        The data points to plot
    outliers : Optional[Union[pd.Series, np.ndarray]]
        Boolean mask or indices indicating outlier points
    title : Optional[str]
        Title for the plot
    figsize : tuple
        Figure size as (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Convert to numpy arrays if needed
    if isinstance(data, pd.Series):
        data = data.values
    if isinstance(outliers, pd.Series):
        outliers = outliers.values if outliers is not None else None
    
    if outliers is not None:
        # Plot separate distributions for normal points and outliers
        sns.kdeplot(data[~outliers], label='Normal Points', color='blue')
        sns.kdeplot(data[outliers], label='Outliers', color='red')
        plt.legend()
    else:
        # Plot single distribution if no outliers specified
        sns.kdeplot(data, color='blue')
    
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.title(title or 'Data Distribution')
    plt.grid(True, alpha=0.3)
    plt.show()

def plot_boxplot(data: Union[pd.Series, np.ndarray],
                outliers: Optional[Union[pd.Series, np.ndarray]] = None,
                title: Optional[str] = None,
                figsize: tuple = (10, 6)) -> None:
    """
    Create a box plot of the data with optional outlier highlighting.
    
    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        The data points to plot
    outliers : Optional[Union[pd.Series, np.ndarray]]
        Boolean mask or indices indicating outlier points
    title : Optional[str]
        Title for the plot
    figsize : tuple
        Figure size as (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Convert to numpy arrays if needed
    if isinstance(data, pd.Series):
        data = data.values
    if isinstance(outliers, pd.Series):
        outliers = outliers.values if outliers is not None else None
    
    # Create box plot (explicit axis for seaborn compatibility)
    sns.boxplot(y=data, color='lightblue')
    
    if outliers is not None:
        # Overlay outlier points in red
        plt.plot(np.zeros_like(data[outliers]), data[outliers], 
                'ro', label='Identified Outliers')
        plt.legend()
    
    plt.title(title or 'Box Plot with Outliers')
    plt.grid(True, alpha=0.3)
    plt.show()

def plot_qq(data: Union[pd.Series, np.ndarray],
            outliers: Optional[Union[pd.Series, np.ndarray]] = None,
            title: Optional[str] = None,
            figsize: tuple = (10, 6)) -> None:
    """
    Create a Q-Q plot to assess normality of the data distribution.
    
    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        The data points to plot
    outliers : Optional[Union[pd.Series, np.ndarray]]
        Boolean mask or indices indicating outlier points
    title : Optional[str]
        Title for the plot
    figsize : tuple
        Figure size as (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Convert to numpy arrays if needed
    if isinstance(data, pd.Series):
        data = data.values
    if isinstance(outliers, pd.Series):
        outliers = outliers.values if outliers is not None else None
    
    # Create Q-Q plot
    stats.probplot(data, dist="norm", plot=plt)
    
    if outliers is not None:
        # Get the theoretical quantiles and ordered data
        theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
        sorted_data = np.sort(data)
        
        # Highlight outlier points
        mask = np.isin(sorted_data, data[outliers])
        plt.plot(theoretical_quantiles[mask], sorted_data[mask], 'ro', 
                label='Outliers', markersize=8)
        plt.legend()
    
    plt.title(title or 'Q-Q Plot for Normality Assessment')
    plt.grid(True, alpha=0.3)
    plt.show()

def plot_outlier_analysis(data: Union[pd.Series, np.ndarray],
                         outliers: Union[pd.Series, np.ndarray],
                         title: Optional[str] = None,
                         figsize: tuple = (15, 10)) -> None:
    """
    Create a comprehensive visualization combining multiple plots for outlier analysis.
    
    Parameters
    ----------
    data : Union[pd.Series, np.ndarray]
        The data points to plot
    outliers : Union[pd.Series, np.ndarray]
        Boolean mask or indices indicating outlier points
    title : Optional[str]
        Title for the plot
    figsize : tuple
        Figure size as (width, height)
    """
    # Create a figure with a 2x2 subplot layout
    fig = plt.figure(figsize=figsize)
    fig.suptitle(title or 'Comprehensive Outlier Analysis', fontsize=14)
    
    # Convert to numpy arrays if needed
    if isinstance(data, pd.Series):
        data = data.values
    if isinstance(outliers, pd.Series):
        outliers = outliers.values
    
    # 1. Scatter plot with outliers
    plt.subplot(2, 2, 1)
    x = np.arange(len(data))
    plt.scatter(x[~outliers], data[~outliers], c='blue', label='Normal Points')
    plt.scatter(x[outliers], data[outliers], c='red', label='Outliers')
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Outlier Detection')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Distribution plot
    plt.subplot(2, 2, 2)
    sns.kdeplot(data[~outliers], label='Normal Points', color='blue')
    sns.kdeplot(data[outliers], label='Outliers', color='red')
    plt.xlabel('Value')
    plt.ylabel('Density')
    plt.title('Data Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 3. Box plot
    plt.subplot(2, 2, 3)
    sns.boxplot(y=data, color='lightblue')
    plt.plot(np.zeros_like(data[outliers]), data[outliers], 
            'ro', label='Identified Outliers')
    plt.title('Box Plot')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 4. Q-Q plot
    plt.subplot(2, 2, 4)
    stats.probplot(data, dist="norm", plot=plt)
    theoretical_quantiles = stats.norm.ppf(np.linspace(0.01, 0.99, len(data)))
    sorted_data = np.sort(data)
    mask = np.isin(sorted_data, data[outliers])
    plt.plot(theoretical_quantiles[mask], sorted_data[mask], 'ro', 
            label='Outliers', markersize=8)
    plt.title('Q-Q Plot')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Adjust layout to prevent overlap
    plt.tight_layout()
    plt.show() 