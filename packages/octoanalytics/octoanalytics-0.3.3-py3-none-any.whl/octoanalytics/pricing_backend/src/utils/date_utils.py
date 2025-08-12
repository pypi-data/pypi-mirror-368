"""Date and time utility functions for pricing calculations."""

import pandas as pd
import holidays
from typing import List, Optional
from datetime import datetime, time


class DateUtils:
    """Utility class for date and time operations."""
    
    def __init__(self, country_code: str = "FR", timezone: str = "Europe/Paris"):
        """
        Initialize DateUtils with country and timezone settings.
        
        Args:
            country_code: Country code for holiday calculations (default: "FR")
            timezone: Timezone for date operations (default: "Europe/Paris")
        """
        self.country_code = country_code
        self.timezone = timezone
        self.holidays = holidays.country_holidays(country_code)
    
    @staticmethod
    def is_peak_hour(dt: datetime, 
                     peak_start: int = 8, 
                     peak_end: int = 20,
                     peak_weekdays: Optional[List[int]] = None) -> bool:
        """
        Determine if a given datetime falls within peak hours.
        
        Args:
            dt: Datetime to check
            peak_start: Start hour for peak period (default: 8)
            peak_end: End hour for peak period (default: 20)
            peak_weekdays: List of weekdays (0=Monday, 6=Sunday) that have peak hours
                          Default: [0,1,2,3,4] (Monday-Friday)
        
        Returns:
            True if datetime is during peak hours, False otherwise
        """
        if peak_weekdays is None:
            peak_weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
        
        # Check if it's a peak weekday
        if dt.weekday() not in peak_weekdays:
            return False
        
        # Check if it's within peak hours
        return peak_start <= dt.hour < peak_end
    
    def is_holiday(self, dt: datetime) -> bool:
        """
        Check if a given date is a holiday.
        
        Args:
            dt: Datetime to check
            
        Returns:
            True if the date is a holiday, False otherwise
        """
        return dt.date() in self.holidays
    
    def add_peak_load_column(self, 
                           df: pd.DataFrame, 
                           datetime_col: str = 'datetime',
                           peak_start: int = 8,
                           peak_end: int = 20,
                           exclude_holidays: bool = True) -> pd.DataFrame:
        """
        Add is_peak_load boolean column to DataFrame.
        
        Args:
            df: DataFrame with datetime column
            datetime_col: Name of the datetime column
            peak_start: Start hour for peak period (default: 8)
            peak_end: End hour for peak period (default: 20)
            exclude_holidays: Whether to exclude holidays from peak periods
            
        Returns:
            DataFrame with added is_peak_load column
        """
        df = df.copy()
        
        # Ensure datetime column is datetime type
        df[datetime_col] = pd.to_datetime(df[datetime_col])
        
        # Initialize peak load column
        df['is_peak_load'] = False
        
        # Apply peak hour logic
        for idx, row in df.iterrows():
            dt = row[datetime_col]
            
            # Check if it's a holiday and we're excluding holidays
            if exclude_holidays and self.is_holiday(dt):
                continue
            
            # Check if it's peak hours
            df.loc[idx, 'is_peak_load'] = self.is_peak_hour(dt, peak_start, peak_end)
        
        return df
    
    def add_paris_timezone_features(self, df: pd.DataFrame, 
                         datetime_col: str = 'interval_start') -> pd.DataFrame:
        """
        Add Paris timezone features to DataFrame from UTC datetime column.
        
        Args:
            df: DataFrame with UTC datetime column
            datetime_col: Name of the UTC datetime column (default: 'interval_start')
            
        Returns:
            DataFrame with added day_tz_paris and hour_tz_paris columns
        """
        df = df.copy()
        
        # Ensure datetime column is datetime type
        df[datetime_col] = pd.to_datetime(df[datetime_col])
        
        # Ensure timezone-aware (assume UTC if not specified)
        if df[datetime_col].dt.tz is None:
            df[datetime_col] = df[datetime_col].dt.tz_localize('UTC')
        
        # Convert to Paris timezone
        paris_time = df[datetime_col].dt.tz_convert('Europe/Paris')
        
        # Add Paris timezone features
        df['day_tz_paris'] = paris_time.dt.day
        df['hour_tz_paris'] = paris_time.dt.hour
        
        return df