import os
import sys
import unittest
import numpy as np

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    import pandas as pd
except ImportError:
    raise ImportError("pandas is required for testing. Install with: pip install pandas")

from statclean import StatClean

class TestStatClean(unittest.TestCase):
    def setUp(self):
        """Set up test data"""
        np.random.seed(42)
        n_samples = 100
        
        # Create test data with known outliers
        self.test_data = np.concatenate([
            np.random.normal(170, 10, n_samples-2),  # Normal data
            np.array([300, 40])  # Two outliers
        ])
        self.height = np.concatenate([
            np.random.normal(170, 10, n_samples-2),  # Normal data
            np.array([250, 50])  # Two outliers
        ])
        self.weight = np.concatenate([
            np.random.normal(70, 5, n_samples-2),  # Normal data
            np.array([150, 20])  # Two outliers
        ])
        
        # Create DataFrame
        self.df = pd.DataFrame({
            'test_col': self.test_data,
            'height': self.height,
            'weight': self.weight
        })
        
        # Import StatClean
        self.cleaner = StatClean()
        self.cleaner.set_data(self.df)

    def test_set_data(self):
        """Test setting data"""
        self.assertTrue(isinstance(self.cleaner.original_df, pd.DataFrame))
        self.assertTrue(isinstance(self.cleaner.clean_df, pd.DataFrame))
        self.assertEqual(len(self.cleaner.original_df), len(self.df))

    def test_add_zscore_columns(self):
        """Test adding Z-score columns"""
        self.cleaner.add_zscore_columns(['height', 'weight'])
        self.assertIn('height_zscore', self.cleaner.clean_df.columns)
        self.assertIn('weight_zscore', self.cleaner.clean_df.columns)

    def test_remove_outliers_zscore(self):
        """Test removing outliers using Z-score method"""
        # Add Z-score column first
        self.cleaner.add_zscore_columns(['test_col'])
        
        # Remove outliers
        self.cleaner.remove_outliers_zscore('test_col', threshold=3.0)
        
        # Check that outliers were removed
        cleaned_df = self.cleaner.clean_df
        self.assertNotIn(300, cleaned_df['test_col'].values)
        self.assertNotIn(40, cleaned_df['test_col'].values)
        self.assertLess(len(cleaned_df), len(self.df))

    def test_clean_zscore_columns(self):
        """Test cleaning all Z-score columns"""
        # Add Z-score columns
        self.cleaner.add_zscore_columns(['height', 'weight'])
        
        # Clean using Z-scores
        self.cleaner.clean_zscore_columns(threshold=3.0)
        
        # Check that outliers were removed
        cleaned_df = self.cleaner.clean_df
        self.assertNotIn(250, cleaned_df['height'].values)
        self.assertNotIn(50, cleaned_df['height'].values)
        self.assertNotIn(150, cleaned_df['weight'].values)
        self.assertNotIn(20, cleaned_df['weight'].values)
        self.assertLess(len(cleaned_df), len(self.df))

    def test_get_outlier_stats(self):
        """Test getting outlier statistics"""
        # Add Z-score columns
        self.cleaner.add_zscore_columns(['height', 'weight'])
        
        # Get stats
        stats = self.cleaner.get_outlier_stats(
            columns=['height', 'weight'],
            methods=['iqr', 'zscore']
        )
        
        # Check that stats is a DataFrame
        self.assertIsInstance(stats, pd.DataFrame)
        
        # Check that required columns exist
        expected_columns = ['Column', 'Method', 'Potential Outliers', 'Percent Outliers']
        for col in expected_columns:
            self.assertIn(col, stats.columns)
        
        # Check that both columns and methods are represented
        columns_in_stats = stats['Column'].unique()
        methods_in_stats = stats['Method'].unique()
        
        self.assertIn('height', columns_in_stats)
        self.assertIn('weight', columns_in_stats)
        self.assertIn('IQR', methods_in_stats)
        self.assertIn('Z-score', methods_in_stats)
        
        # Check that outliers were detected
        height_iqr_row = stats[(stats['Column'] == 'height') & (stats['Method'] == 'IQR')]
        height_zscore_row = stats[(stats['Column'] == 'height') & (stats['Method'] == 'Z-score')]
        
        self.assertGreater(height_iqr_row['Potential Outliers'].iloc[0], 0)
        self.assertGreater(height_zscore_row['Potential Outliers'].iloc[0], 0)

    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test empty DataFrame
        empty_df = pd.DataFrame()
        with self.assertRaises(ValueError):
            self.cleaner.set_data(empty_df)
        
        # Test non-numeric data
        str_df = pd.DataFrame({'text': ['a', 'b', 'c']})
        self.cleaner.set_data(str_df)
        stats = self.cleaner.get_outlier_stats()
        self.assertEqual(len(stats), 0)  # No numeric columns to analyze

class TestStatCleanFunctional(unittest.TestCase):
    """Functional tests simulating real-world usage scenarios"""
    
    def test_real_world_scenario(self):
        """Test complete workflow with realistic data"""
        # Create realistic dataset with multiple types of outliers
        np.random.seed(42)
        n_samples = 100  # Smaller dataset for faster testing
        
        # Generate realistic height data (in cm) with different types of outliers
        height = np.random.normal(170, 10, n_samples)
        height[0] = 250  # Obvious outlier
        height[1] = 120  # Borderline outlier
        height[2:5] += 40  # Cluster of mild outliers
        
        # Generate correlated weight data (in kg) with outliers
        weight = height * 0.4 + np.random.normal(0, 5, n_samples)
        weight[0] = 200  # Corresponding outlier
        weight[10] = 30  # Independent outlier
        
        # Create DataFrame
        df = pd.DataFrame({
            'height': height,
            'weight': weight
        })
        
        # Initialize cleaner
        cleaner = StatClean(df)
        
        # Get outlier statistics
        stats = cleaner.get_outlier_stats()
        
        # Clean data using both methods to populate outlier indices
        cleaner.remove_outliers_iqr('height')
        cleaner.reset()
        cleaner.remove_outliers_zscore('height')
        
        # Get outlier indices
        outliers = cleaner.get_outlier_indices('height')
        
        # Verify that obvious outliers were detected
        self.assertIn(0, outliers['height'])  # Index 0 has the obvious outlier (250)

if __name__ == '__main__':
    unittest.main()