"""
OctoAnalytics Pricing Module

A comprehensive pricing analysis module for energy market calculations,
including load curve processing, peak/baseload analysis, and hedging strategies.
"""

from .config import load_config, get_config_value
from .src.models.contracts import ContractType, HedgeType, PFCType, HedgingConfig, PricingResult
from .src.utils.date_utils import DateUtils
from .src.utils.file_utils import read_load_curve, validate_csv_structure
from .src.processing.load_curve_processor import LoadCurveProcessor

__version__ = "1.0.0"
__author__ = "OctoAnalytics Team"

__all__ = [
    'load_config',
    'get_config_value',
    'ContractType', 
    'HedgeType', 
    'PFCType', 
    'HedgingConfig', 
    'PricingResult',
    'DateUtils',
    'read_load_curve',
    'validate_csv_structure',
    'LoadCurveProcessor'
]