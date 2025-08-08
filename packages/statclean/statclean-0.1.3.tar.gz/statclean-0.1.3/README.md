# StatClean

A comprehensive statistical data preprocessing and outlier detection library with formal statistical testing and publication-quality reporting.

StatClean provides advanced statistical methods for data cleaning including formal statistical tests (Grubbs' test, Dixon's Q-test), multivariate outlier detection, data transformations, and publication-quality reporting with p-values and effect sizes. Designed for academic research, data science, and statistical analysis where rigorous statistical methods and reproducible results are essential.

## Features

### 🔬 Statistical Testing & Analysis
- **Formal Statistical Tests**: Grubbs' test and Dixon's Q-test with p-values and critical values
- **Distribution Analysis**: Automatic normality testing, skewness/kurtosis calculation
- **Method Comparison**: Statistical agreement analysis between different detection methods
- **Publication-Quality Reporting**: P-values, confidence intervals, and effect sizes

### 📊 Detection Methods
- **Univariate Methods**: IQR, Z-score, Modified Z-score (MAD-based)
- **Multivariate Methods**: Mahalanobis distance with chi-square thresholds
- **Batch Processing**: Detect outliers across multiple columns with progress tracking
- **Automatic Method Selection**: Based on statistical distribution analysis

### 🛠️ Treatment Options
- **Outlier Removal**: Remove detected outliers with statistical validation
- **Winsorizing**: Cap outliers at specified bounds instead of removal
- **Data Transformations**: Box-Cox, logarithmic, and square-root transformations
- **Transformation Recommendations**: Automatic selection based on distribution characteristics

### 📈 Advanced Visualization
- **Comprehensive Analysis Plots**: 3-in-1 analysis (boxplot, distribution, Q-Q plot)
- **Standalone Plotting Functions**: Individual scatter, distribution, box, and Q-Q plots
- **Interactive Dashboards**: 2x2 comprehensive analysis grid
- **Publication-Ready Figures**: Professional styling with customizable parameters

### 🚀 Developer Experience
- **Method Chaining**: Fluent API for streamlined workflows
- **Type Safety**: Comprehensive type hints for enhanced IDE support
- **Progress Tracking**: Built-in progress bars for batch operations
- **Flexible Configuration**: Customizable thresholds and statistical parameters
- **Memory Efficient**: Statistics caching and lazy evaluation

## Installation

```bash
pip install statclean
```

## Quick Start

```python
import pandas as pd
from statclean import StatClean

# Load your data
df = pd.DataFrame({
    'income': [25000, 30000, 35000, 40000, 500000, 45000, 50000],  # Contains outlier
    'age': [25, 30, 35, 40, 35, 45, 50]
})

"""
Note: As of v0.1.3, remover methods return the cleaner instance for method chaining.
Access cleaned data via `cleaner.clean_df` and details via `cleaner.outlier_info`.
"""

# Initialize StatClean
cleaner = StatClean(df)

# Automatic analysis and cleaning
cleaned_df, info = cleaner.clean_columns(['income'], method='auto', show_progress=True)

print(f"Original shape: {df.shape}")
print(f"Cleaned shape: {cleaned_df.shape}")
print(f"Outliers removed: {info['income']['outliers_removed']}")
```

## Advanced Usage

### Formal Statistical Testing

```python
# Grubbs' test for outliers with statistical significance
result = cleaner.grubbs_test('income', alpha=0.05)
print(f"Test statistic: {result['statistic']:.3f}")
print(f"P-value: {result['p_value']:.6f}")
print(f"Outlier detected: {result['is_outlier']}")

# Dixon's Q-test for small samples
result = cleaner.dixon_q_test('age', alpha=0.05)
print(f"Q statistic: {result['statistic']:.3f}")
print(f"Critical value: {result['critical_value']:.3f}")
```

### Multivariate Outlier Detection

```python
# Mahalanobis distance for multivariate outliers
# chi2_threshold can be a percentile (0<val<=1) or absolute chi-square statistic
# use_shrinkage=True uses Ledoit–Wolf shrinkage covariance if scikit-learn is installed
outliers = cleaner.detect_outliers_mahalanobis(['income', 'age'], chi2_threshold=0.95, use_shrinkage=True)
print(f"Multivariate outliers detected: {outliers.sum()}")

# Remove multivariate outliers
cleaned_df = cleaner.remove_outliers_mahalanobis(['income', 'age'])
```

### Data Transformations

```python
# Automatic transformation recommendation
recommendation = cleaner.recommend_transformation('income')
print(f"Recommended transformation: {recommendation['recommended_method']}")
print(f"Improvement in skewness: {recommendation['expected_improvement']:.3f}")

# Apply Box-Cox transformation
_, info = cleaner.transform_boxcox('income')
print(f"Optimal lambda: {info['lambda']:.3f}")

# Method chaining for complex workflows
result = (cleaner
          .set_thresholds(zscore_threshold=2.5)
          .add_zscore_columns(['income'])
          .winsorize_outliers_iqr('income', lower_factor=1.5, upper_factor=1.5)
          .clean_df)
```

### Comprehensive Analysis

```python
# Distribution analysis with recommendations
analysis = cleaner.analyze_distribution('income')
print(f"Skewness: {analysis['skewness']:.3f}")
print(f"Kurtosis: {analysis['kurtosis']:.3f}")
print(f"Normality test p-value: {analysis['normality_test']['p_value']:.6f}")
print(f"Recommended method: {analysis['recommended_method']}")

# Compare different detection methods
comparison = cleaner.compare_methods(['income'], 
                                   methods=['iqr', 'zscore', 'modified_zscore'])
print("Method Agreement Analysis:")
for method, stats in comparison['income']['method_stats'].items():
    print(f"  {method}: {stats['outliers_detected']} outliers")
```

### Advanced Visualization

```python
# Comprehensive analysis plots
figures = cleaner.plot_outlier_analysis(['income', 'age'])

# Individual visualization components
from statclean.utils import plot_outliers, plot_distribution, plot_qq

# Custom outlier highlighting
outliers = cleaner.detect_outliers_zscore('income')
plot_outliers(df['income'], outliers, title='Income Distribution')
plot_distribution(df['income'], outliers, title='Income KDE')
plot_qq(df['income'], outliers, title='Income Normality')
```

### Batch Processing with Progress Tracking

```python
# Process multiple columns with detailed reporting
columns_to_clean = ['income', 'age', 'score', 'rating']
cleaned_df, detailed_info = cleaner.clean_columns(
    columns=columns_to_clean,
    method='auto',
    show_progress=True,
    include_indices=True
)

# Access detailed statistics
for column, info in detailed_info.items():
    print(f"\n{column}:")
    print(f"  Method used: {info['method_used']}")
    print(f"  Outliers removed: {info['outliers_removed']}")
    print(f"  Percentage removed: {info['percentage_removed']:.2f}%")
    if 'p_value' in info:
        print(f"  Statistical significance: p = {info['p_value']:.6f}")
```

## Statistical Methods Reference

### Detection Methods
- **`detect_outliers_iqr()`**: Interquartile Range method with configurable factors
- **`detect_outliers_zscore()`**: Standard Z-score method
- **`detect_outliers_modified_zscore()`**: Modified Z-score using MAD (robust to skewness)
- **`detect_outliers_mahalanobis()`**: Multivariate detection using Mahalanobis distance

### Formal Statistical Tests
- **`grubbs_test()`**: Grubbs' test for single outliers with p-values
- **`dixon_q_test()`**: Dixon's Q-test for small samples (n < 30)

### Treatment Methods
- **`remove_outliers_*()`**: Remove detected outliers
- **`winsorize_outliers_*()`**: Cap outliers at specified bounds
- **`transform_boxcox()`**: Box-Cox transformation with optimal lambda
- **`transform_log()`**: Logarithmic transformation (natural, base 10, base 2)
- **`transform_sqrt()`**: Square root transformation

### Analysis and Reporting
- **`analyze_distribution()`**: Comprehensive distribution analysis
- **`compare_methods()`**: Statistical agreement between methods
- **`get_outlier_stats()`**: Detailed outlier statistics without removal
- **`get_summary_report()`**: Publication-quality summary report

## Real-World Example

```python
import pandas as pd
from sklearn.datasets import fetch_california_housing
from statclean import StatClean

# Load California Housing dataset
housing = fetch_california_housing()
df = pd.DataFrame(housing.data, columns=housing.feature_names)
df['PRICE'] = housing.target

print(f"Dataset shape: {df.shape}")
print("Features:", list(df.columns))

# Initialize with index preservation
cleaner = StatClean(df, preserve_index=True)

# Analyze key features
features = ['MedInc', 'AveRooms', 'PRICE']
for feature in features:
    analysis = cleaner.analyze_distribution(feature)
    print(f"\n{feature} Analysis:")
    print(f"  Skewness: {analysis['skewness']:.3f}")
    print(f"  Recommended method: {analysis['recommended_method']}")
    
    # Statistical significance test
    if analysis['skewness'] > 1:  # Highly skewed
        grubbs_result = cleaner.grubbs_test(feature, alpha=0.05)
        print(f"  Grubbs test p-value: {grubbs_result['p_value']:.6f}")

# Comprehensive cleaning with statistical validation
cleaned_df, cleaning_info = cleaner.clean_columns(
    columns=features,
    method='auto',
    show_progress=True,
    include_indices=True
)

print(f"\nCleaning Results:")
print(f"Original shape: {df.shape}")
print(f"Cleaned shape: {cleaned_df.shape}")

for feature, info in cleaning_info.items():
    print(f"\n{feature}:")
    print(f"  Method: {info['method_used']}")
    print(f"  Outliers removed: {info['outliers_removed']}")
    print(f"  Percentage: {info['percentage_removed']:.2f}%")

# Generate comprehensive visualizations
figures = cleaner.plot_outlier_analysis(features)

# Method comparison analysis
comparison = cleaner.compare_methods(features)
for feature in features:
    print(f"\n{feature} Method Comparison:")
    print(comparison[feature]['summary'])
```

## Requirements

- **Python**: ≥3.7
- **numpy**: ≥1.19.0
- **pandas**: ≥1.2.0  
- **matplotlib**: ≥3.3.0
- **seaborn**: ≥0.11.0
- **scipy**: ≥1.6.0 (for statistical tests)
- **tqdm**: ≥4.60.0 (for progress bars)
- **scikit-learn**: ≥0.24.0 (optional, for shrinkage covariance in Mahalanobis)

## Changelog

### Version 0.1.3 (2025-08-08)

- Align docs/examples with actual API: remover methods return `self`; use `cleaner.clean_df` and `cleaner.outlier_info`.
- Grubbs/Dixon result keys clarified: `statistic`, `is_outlier`.
- Mahalanobis `chi2_threshold` accepts percentile (0<val<=1) or absolute chi-square statistic; added `use_shrinkage` option.
- Transformations preserve NaNs; Box-Cox computed on non-NA values only.
- Seaborn plotting calls updated for compatibility; analysis functions made NaN-safe.
- Added GitHub Actions workflow to publish to PyPI on releases.

### Version 0.1.0 (2025-08-06)

**🎉 Initial Release of StatClean**

Complete rebranding from OutlierCleaner to StatClean with expanded statistical capabilities:

#### **New Features**
- **Formal Statistical Testing**: Grubbs' test and Dixon's Q-test with p-values
- **Multivariate Analysis**: Mahalanobis distance outlier detection
- **Data Transformations**: Box-Cox, logarithmic, square-root with automatic recommendations
- **Method Chaining**: Fluent API for streamlined statistical workflows
- **Publication-Quality Reporting**: Statistical significance testing and effect sizes

#### **Enhanced Functionality**
- **Advanced Distribution Analysis**: Automatic normality testing and method recommendations
- **Batch Processing**: Multi-column processing with progress tracking and detailed reporting
- **Statistical Validation**: P-values, confidence intervals, and critical value calculations
- **Comprehensive Visualization**: 3-in-1 analysis plots and standalone plotting functions

#### **Technical Improvements**
- **Type Safety**: Complete type annotations for enhanced IDE support
- **Memory Efficiency**: Statistics caching and lazy evaluation
- **Robust Error Handling**: Edge case handling for statistical computations
- **Flexible Configuration**: Customizable thresholds and statistical parameters

#### **API Changes**
- Package renamed from `outlier-cleaner` to `statclean`
- Main class renamed from `OutlierCleaner` to `StatClean`
- Backward compatibility alias maintained: `OutlierCleaner = StatClean`
- Enhanced method signatures with comprehensive parameter documentation

This release transforms the package from a basic outlier detection tool into a comprehensive statistical preprocessing library suitable for academic research and professional data science applications.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Areas of particular interest:

- Additional statistical tests and methods
- Performance optimizations for large datasets
- Enhanced visualization capabilities
- Documentation improvements and examples

## License

MIT License

## Author

**Subashanan Nair**

---

*StatClean: Where statistical rigor meets practical data science.*

## Development: Run Tests in Headless Mode and Capture Logs

```bash
# Ensure a headless matplotlib backend and run tests quietly
export MPLBACKEND=Agg
pytest -q

# Save a timestamped test log (example)
LOG=cursor_logs/test_log.md
mkdir -p cursor_logs
echo "==== $(date) ====\n" >> "$LOG"
MPLBACKEND=Agg pytest -q 2>&1 | tee -a "$LOG"

## Continuous Delivery: Publish to PyPI (Trusted Publisher)

This repository includes a GitHub Actions workflow using PyPI Trusted Publisher (OIDC).

Setup (one-time on PyPI):
- Add this GitHub repo as a Trusted Publisher in the PyPI project settings.

Release steps:
1. Bump version in `statclean/__init__.py` and `setup.py` (already `0.1.3`).
2. Push a tag matching the version, e.g., `git tag v0.1.3 && git push origin v0.1.3`.
3. Workflow will run tests, build, and publish to PyPI without storing credentials.
```