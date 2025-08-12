"""File utility functions for pricing data loading."""

import pandas as pd
import logging
import os
from typing import Union, Optional
from ...config import load_config, get_config_value

logger = logging.getLogger(__name__)


def read_load_curve(file_path: Union[str, os.PathLike], 
                   config: Optional[dict] = None) -> pd.DataFrame:
    """
    Load load curve data from CSV file with automatic datetime conversion.
    
    This is a standalone function that can be used independently of the LoadCurveProcessor.
    
    Args:
        file_path: Path to the CSV file containing load curve data
        config: Optional configuration dictionary. If None, loads from config file.
        
    Returns:
        DataFrame with load curve data and converted datetime columns
        
    Raises:
        FileNotFoundError: If the CSV file is not found
        ValueError: If required columns are missing or datetime conversion fails
        
    Example:
        >>> df = read_load_curve('path/to/load_curve.csv')
        >>> print(df.head())
    """
    # Load configuration if not provided
    if config is None:
        config = load_config()
    
    # Get CSV reading configuration
    delimiter = get_config_value(config, 'file_processing.csv_settings.delimiter', ',')
    encoding = get_config_value(config, 'file_processing.csv_settings.encoding', 'utf-8')
    
    logger.info(f"Loading load curve data from CSV: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    try:
        # Read CSV file
        df = pd.read_csv(
            file_path, 
            delimiter=delimiter,
            encoding=encoding
        )
        
        logger.info(f"Loaded {len(df)} rows from CSV")
        logger.info(f"Columns found: {list(df.columns)}")
        
        # Convert time columns to datetime if they exist
        time_columns = ['interval_start', 'interval_end', 'datetime']
        for col in time_columns:
            if col in df.columns:
                logger.info(f"Converting column '{col}' to datetime")
                df[col] = pd.to_datetime(df[col])
                logger.info(f"Column '{col}' dtype after conversion: {df[col].dtype}")
        
        # Validate that we have at least one time column
        time_cols_present = [col for col in time_columns if col in df.columns]
        if not time_cols_present:
            raise ValueError(f"No time columns found. Expected one of: {time_columns}")
        
        logger.info(f"Data types after conversion: {df.dtypes}")
        
        # Add Paris timezone features if interval_start column exists
        if 'interval_start' in df.columns:
            from .date_utils import DateUtils
            date_utils = DateUtils()
            df = date_utils.add_paris_timezone_features(df, 'interval_start')
            logger.info("Added Paris timezone features (day_tz_paris, hour_tz_paris)")
        
        return df
        
    except pd.errors.EmptyDataError:
        raise ValueError(f"CSV file is empty: {file_path}")
    except pd.errors.ParserError as e:
        raise ValueError(f"Error parsing CSV file {file_path}: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error reading CSV file {file_path}: {e}")


def validate_csv_structure(file_path: Union[str, os.PathLike], 
                          required_columns: Optional[list] = None,
                          config: Optional[dict] = None) -> dict:
    """
    Validate CSV file structure without loading the entire file.
    
    Args:
        file_path: Path to the CSV file to validate
        required_columns: List of required columns. If None, uses config defaults.
        config: Optional configuration dictionary. If None, loads from config file.
        
    Returns:
        Dictionary with validation results including column info and sample data
        
    Raises:
        FileNotFoundError: If the CSV file is not found
    """
    if config is None:
        config = load_config()
    
    if required_columns is None:
        required_columns = get_config_value(
            config, 
            'load_curve.required_columns', 
            ['datetime', 'load_value', 'sous_profile']
        )
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    
    # Read just the header and a few rows for validation
    delimiter = get_config_value(config, 'file_processing.csv_settings.delimiter', ',')
    encoding = get_config_value(config, 'file_processing.csv_settings.encoding', 'utf-8')
    
    try:
        # Read header and first few rows
        df_sample = pd.read_csv(
            file_path, 
            delimiter=delimiter,
            encoding=encoding,
            nrows=5  # Just read first 5 rows for validation
        )
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in df_sample.columns]
        found_columns = list(df_sample.columns)
        
        # Check for time columns
        time_columns = ['interval_start', 'interval_end', 'datetime']
        found_time_columns = [col for col in time_columns if col in df_sample.columns]
        
        validation_result = {
            'file_path': str(file_path),
            'total_rows_checked': len(df_sample),
            'found_columns': found_columns,
            'required_columns': required_columns,
            'missing_columns': missing_columns,
            'found_time_columns': found_time_columns,
            'is_valid': len(missing_columns) == 0 and len(found_time_columns) > 0,
            'sample_data': df_sample.head(2).to_dict('records')
        }
        
        return validation_result
        
    except Exception as e:
        return {
            'file_path': str(file_path),
            'error': str(e),
            'is_valid': False
        } 