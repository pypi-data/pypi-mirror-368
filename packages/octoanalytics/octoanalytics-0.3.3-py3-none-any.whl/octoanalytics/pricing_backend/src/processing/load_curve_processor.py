"""Load curve data processing module."""

import pandas as pd
import logging
import os
from typing import Dict, List, Optional, Any, Union
from ..utils.date_utils import DateUtils
from ...config import load_config, get_config_value

logger = logging.getLogger(__name__)


class LoadCurveProcessor:
    """Processor for load curve data with peak/baseload analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize LoadCurveProcessor.
        
        Args:
            config: Configuration dictionary. If None, loads from config file.
        """
        self.config = config if config is not None else load_config()
        self.date_utils = DateUtils(
            country_code=get_config_value(self.config, 'regional.country', 'FR'),
            timezone=get_config_value(self.config, 'regional.timezone', 'Europe/Paris')
        )
        
        # Get configuration values
        self.peak_start = get_config_value(self.config, 'peak_load.hours.start', 8)
        self.peak_end = get_config_value(self.config, 'peak_load.hours.end', 20)
        self.exclude_holidays = get_config_value(self.config, 'peak_load.exclude_holidays', True)
        
        # Required columns
        self.required_columns = get_config_value(
            self.config, 
            'load_curve.required_columns', 
            ['datetime', 'load_value', 'sous_profile']
        )
    
    def process_load_curve(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process load curve data by adding peak load indicators and time features.
        
        Args:
            df: Input DataFrame with load curve data
            
        Returns:
            Processed DataFrame with additional columns
        """
        logger.info("Starting load curve processing")
        
        # Create a copy to avoid modifying original data
        processed_df = df.copy()
        
        # Map columns to expected format
        datetime_col = self._get_datetime_column(processed_df)
        load_value_col = self._get_load_value_column(processed_df)
        
        logger.info(f"Using datetime column: {datetime_col}")
        logger.info(f"Using load value column: {load_value_col}")
        
        # Add peak load column
        processed_df = self.date_utils.add_peak_load_column(
            processed_df,
            datetime_col=datetime_col,
            peak_start=self.peak_start,
            peak_end=self.peak_end,
            exclude_holidays=self.exclude_holidays
        )
        
        # Add Paris timezone features
        processed_df = self.date_utils.add_paris_timezone_features(
            processed_df,
            datetime_col=datetime_col
        )
        
        logger.info(f"Processing complete. Output shape: {processed_df.shape}")
        return processed_df
    
    def _get_datetime_column(self, df: pd.DataFrame) -> str:
        """Get the appropriate datetime column from the DataFrame."""
        alternative_columns = get_config_value(
            self.config, 
            'load_curve.alternative_columns.datetime', 
            ['interval_start', 'datetime']
        )
        
        for col in alternative_columns:
            if col in df.columns:
                return col
        
        raise ValueError(f"No datetime column found. Expected one of: {alternative_columns}")
    
    def _get_load_value_column(self, df: pd.DataFrame) -> str:
        """Get the appropriate load value column from the DataFrame."""
        alternative_columns = get_config_value(
            self.config, 
            'load_curve.alternative_columns.load_value', 
            ['interval_value_W', 'load_value']
        )
        
        for col in alternative_columns:
            if col in df.columns:
                return col
        
        raise ValueError(f"No load value column found. Expected one of: {alternative_columns}")
