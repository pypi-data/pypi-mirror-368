#!/usr/bin/env python3
"""
Example demonstrating the read_load_curve functionality.

This shows how to use the integrated load_csv function (renamed to read_load_curve)
from the original pricing_local_test_v0.py script with real data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Import the new functionality
from octoanalytics.pricing_backend import read_load_curve, LoadCurveProcessor

# Path to the real CSV file
REAL_CSV_FILE = "/Users/thomas.maaza/Documents/github_repo/oefr-procurement/Pricing/forecasted_data_cdc.csv"


def demonstrate_read_load_curve():
    """Demonstrate the read_load_curve functionality with real data."""
    
    print("=" * 60)
    print("Demonstrating read_load_curve functionality with REAL DATA")
    print("=" * 60)
    print(f"Using file: {REAL_CSV_FILE}")
    
    # Check if file exists
    if not os.path.exists(REAL_CSV_FILE):
        print(f"ERROR: File not found: {REAL_CSV_FILE}")
        return
    
    try:
        # 1. Read the load curve data
        print("\n1. Reading load curve data...")
        df = read_load_curve(REAL_CSV_FILE)
        
        # 2. Show data statistics
        print("\n2. Data statistics:")
        print(f"   Date range: {df['interval_start'].min()} to {df['interval_start'].max()}")
        print(f"   Unique segments: {df['segment'].nunique()}")
        print(f"   Unique sous_profiles: {df['sous_profile'].nunique()}")
        print(f"   Load value range: {df['interval_value_W'].min():.2f} to {df['interval_value_W'].max():.2f} W")
        
        # 3. Use with LoadCurveProcessor
        print("\n3. Processing with LoadCurveProcessor...")
        processor = LoadCurveProcessor()
        processed_df = processor.process_load_curve(df)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_standalone_usage():
    """Demonstrate standalone usage of read_load_curve with real data."""
    
    print("\n" + "=" * 60)
    print("Demonstrating standalone read_load_curve usage with REAL DATA")
    print("=" * 60)
    
    if not os.path.exists(REAL_CSV_FILE):
        print(f"ERROR: File not found: {REAL_CSV_FILE}")
        return
    
    try:
        # Show how to use read_load_curve directly
        print("\nUsing read_load_curve as standalone function:")
        df = read_load_curve(REAL_CSV_FILE)

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demonstrate_read_load_curve()
    demonstrate_standalone_usage()
