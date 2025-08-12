"""Contract and hedging models for pricing calculations."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ContractType(Enum):
    """Enum for different contract types."""
    BASELOAD_VALUE_HEDGE = "baseload_value_hedge"  # A1 hedge
    BASELOAD_PEAKLOAD_VALUE_HEDGE = "baseload_peakload_value_hedge"  # A2/B2 hedge


class HedgeType(Enum):
    """Enum for hedge execution types."""
    FIXED = "fixed"
    DYNAMIC = "dynamic"


class PFCType(Enum):
    """Enum for price forward curve types."""
    TIMESTEP = 15  # 15-minute intervals


@dataclass
class HedgingConfig:
    """Configuration for hedging strategy calculations."""
    contract_type: ContractType
    hedge_type: HedgeType = HedgeType.FIXED
    analysis_start_date: Optional[str] = None  # Format: 'YYYY-MM-DD'
    analysis_end_date: Optional[str] = None    # Format: 'YYYY-MM-DD'
    
    def __post_init__(self):
        """Validate configuration."""
        if not isinstance(self.contract_type, ContractType):
            raise ValueError(f"contract_type must be a ContractType enum, got {type(self.contract_type)}")
        
        if not isinstance(self.hedge_type, HedgeType):
            raise ValueError(f"hedge_type must be a HedgeType enum, got {type(self.hedge_type)}")


@dataclass
class PricingResult:
    """Container for pricing calculation results."""
    total_cost: float
    baseload_cost: float
    peakload_cost: Optional[float] = None
    hedge_effectiveness: Optional[float] = None
    
    def __post_init__(self):
        """Validate pricing results."""
        if self.total_cost < 0:
            raise ValueError("Total cost cannot be negative")
        
        if self.baseload_cost < 0:
            raise ValueError("Baseload cost cannot be negative")
            
        if self.peakload_cost is not None and self.peakload_cost < 0:
            raise ValueError("Peakload cost cannot be negative") 