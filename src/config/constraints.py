"""
Optimization constraints for the multi-objective portfolio optimization.

This module defines various constraints that can be applied during
the portfolio optimization process.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass

from ..config.assets import AssetClass, ALL_ASSETS

@dataclass
class ConstraintViolation:
    """Represents a constraint violation."""
    constraint_name: str
    violation_amount: float
    description: str

class Constraint(ABC):
    """Abstract base class for portfolio constraints."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        """Check if the constraint is satisfied."""
        pass
    
    @abstractmethod
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        """Get constraint violation details if any."""
        pass
    
    @abstractmethod
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        """Get bounds for each asset weight."""
        pass

class WeightSumConstraint(Constraint):
    """Constraint that weights must sum to 1."""
    
    def __init__(self, tolerance: float = 1e-6):
        super().__init__("Weight Sum")
        self.tolerance = tolerance
    
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        return abs(np.sum(weights) - 1.0) <= self.tolerance
    
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        violation = abs(np.sum(weights) - 1.0)
        if violation > self.tolerance:
            return ConstraintViolation(
                constraint_name=self.name,
                violation_amount=violation,
                description=f"Weights sum to {np.sum(weights):.6f}, should sum to 1.0"
            )
        return None
    
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        # This constraint doesn't directly provide bounds
        return [(0.0, 1.0) for _ in assets]

class NonNegativeConstraint(Constraint):
    """Constraint that all weights must be non-negative (no short selling)."""
    
    def __init__(self):
        super().__init__("Non-Negative")
    
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        return np.all(weights >= 0)
    
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        negative_weights = weights[weights < 0]
        if len(negative_weights) > 0:
            violation = abs(np.sum(negative_weights))
            return ConstraintViolation(
                constraint_name=self.name,
                violation_amount=violation,
                description=f"Found {len(negative_weights)} negative weights"
            )
        return None
    
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        return [(0.0, 1.0) for _ in assets]

class IndividualAssetConstraint(Constraint):
    """Constraint on individual asset weights."""
    
    def __init__(self, asset_limits: Dict[str, Tuple[float, float]]):
        super().__init__("Individual Asset Limits")
        self.asset_limits = asset_limits
    
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        for i, asset in enumerate(assets):
            if asset in self.asset_limits:
                min_weight, max_weight = self.asset_limits[asset]
                if not (min_weight <= weights[i] <= max_weight):
                    return False
        return True
    
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        violations = []
        for i, asset in enumerate(assets):
            if asset in self.asset_limits:
                min_weight, max_weight = self.asset_limits[asset]
                if weights[i] < min_weight:
                    violations.append(f"{asset}: {weights[i]:.4f} < {min_weight}")
                elif weights[i] > max_weight:
                    violations.append(f"{asset}: {weights[i]:.4f} > {max_weight}")
        
        if violations:
            total_violation = sum(abs(weights[i] - np.clip(weights[i], 
                                                          self.asset_limits.get(assets[i], (0, 1))[0],
                                                          self.asset_limits.get(assets[i], (0, 1))[1]))
                                for i in range(len(assets)) if assets[i] in self.asset_limits)
            return ConstraintViolation(
                constraint_name=self.name,
                violation_amount=total_violation,
                description="; ".join(violations)
            )
        return None
    
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        bounds = []
        for asset in assets:
            if asset in self.asset_limits:
                bounds.append(self.asset_limits[asset])
            else:
                bounds.append((0.0, 1.0))
        return bounds

class AssetClassConstraint(Constraint):
    """Constraint on asset class allocations."""
    
    def __init__(self, asset_class_limits: Dict[AssetClass, Tuple[float, float]]):
        super().__init__("Asset Class Limits")
        self.asset_class_limits = asset_class_limits
    
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        asset_class_weights = self._calculate_asset_class_weights(weights, assets)
        
        for asset_class, (min_weight, max_weight) in self.asset_class_limits.items():
            class_weight = asset_class_weights.get(asset_class, 0.0)
            if not (min_weight <= class_weight <= max_weight):
                return False
        return True
    
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        asset_class_weights = self._calculate_asset_class_weights(weights, assets)
        violations = []
        total_violation = 0.0
        
        for asset_class, (min_weight, max_weight) in self.asset_class_limits.items():
            class_weight = asset_class_weights.get(asset_class, 0.0)
            if class_weight < min_weight:
                violation = min_weight - class_weight
                violations.append(f"{asset_class.value}: {class_weight:.4f} < {min_weight}")
                total_violation += violation
            elif class_weight > max_weight:
                violation = class_weight - max_weight
                violations.append(f"{asset_class.value}: {class_weight:.4f} > {max_weight}")
                total_violation += violation
        
        if violations:
            return ConstraintViolation(
                constraint_name=self.name,
                violation_amount=total_violation,
                description="; ".join(violations)
            )
        return None
    
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        # Asset class constraints don't directly provide individual asset bounds
        return [(0.0, 1.0) for _ in assets]
    
    def _calculate_asset_class_weights(self, weights: np.ndarray, assets: List[str]) -> Dict[AssetClass, float]:
        """Calculate total weight for each asset class."""
        class_weights = {}
        
        for i, asset in enumerate(assets):
            if asset in ALL_ASSETS:
                asset_class = ALL_ASSETS[asset].asset_class
                class_weights[asset_class] = class_weights.get(asset_class, 0.0) + weights[i]
        
        return class_weights

class MaxAssetsConstraint(Constraint):
    """Constraint limiting the maximum number of assets with non-zero weights."""
    
    def __init__(self, max_assets: int, min_weight_threshold: float = 1e-4):
        super().__init__("Max Assets")
        self.max_assets = max_assets
        self.min_weight_threshold = min_weight_threshold
    
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        non_zero_assets = np.sum(weights > self.min_weight_threshold)
        return non_zero_assets <= self.max_assets
    
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        non_zero_assets = np.sum(weights > self.min_weight_threshold)
        if non_zero_assets > self.max_assets:
            violation = non_zero_assets - self.max_assets
            return ConstraintViolation(
                constraint_name=self.name,
                violation_amount=violation,
                description=f"Portfolio has {non_zero_assets} assets, max allowed is {self.max_assets}"
            )
        return None
    
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        return [(0.0, 1.0) for _ in assets]

class TurnoverConstraint(Constraint):
    """Constraint limiting portfolio turnover."""
    
    def __init__(self, max_turnover: float, previous_weights: Optional[np.ndarray] = None):
        super().__init__("Turnover")
        self.max_turnover = max_turnover
        self.previous_weights = previous_weights
    
    def check(self, weights: np.ndarray, assets: List[str]) -> bool:
        if self.previous_weights is None:
            return True  # No previous weights to compare against
        
        turnover = np.sum(np.abs(weights - self.previous_weights)) / 2
        return turnover <= self.max_turnover
    
    def get_violation(self, weights: np.ndarray, assets: List[str]) -> Optional[ConstraintViolation]:
        if self.previous_weights is None:
            return None
        
        turnover = np.sum(np.abs(weights - self.previous_weights)) / 2
        if turnover > self.max_turnover:
            violation = turnover - self.max_turnover
            return ConstraintViolation(
                constraint_name=self.name,
                violation_amount=violation,
                description=f"Turnover {turnover:.4f} exceeds maximum {self.max_turnover:.4f}"
            )
        return None
    
    def get_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        if self.previous_weights is None:
            return [(0.0, 1.0) for _ in assets]
        
        # Calculate bounds based on turnover constraint
        bounds = []
        for i in range(len(assets)):
            prev_weight = self.previous_weights[i]
            lower_bound = max(0.0, prev_weight - self.max_turnover)
            upper_bound = min(1.0, prev_weight + self.max_turnover)
            bounds.append((lower_bound, upper_bound))
        
        return bounds

class ConstraintManager:
    """Manages multiple constraints for portfolio optimization."""
    
    def __init__(self):
        self.constraints: List[Constraint] = []
    
    def add_constraint(self, constraint: Constraint):
        """Add a constraint to the manager."""
        self.constraints.append(constraint)
    
    def remove_constraint(self, constraint_name: str):
        """Remove a constraint by name."""
        self.constraints = [c for c in self.constraints if c.name != constraint_name]
    
    def check_all(self, weights: np.ndarray, assets: List[str]) -> bool:
        """Check if all constraints are satisfied."""
        return all(constraint.check(weights, assets) for constraint in self.constraints)
    
    def get_violations(self, weights: np.ndarray, assets: List[str]) -> List[ConstraintViolation]:
        """Get all constraint violations."""
        violations = []
        for constraint in self.constraints:
            violation = constraint.get_violation(weights, assets)
            if violation:
                violations.append(violation)
        return violations
    
    def get_combined_bounds(self, assets: List[str]) -> List[Tuple[float, float]]:
        """Get combined bounds from all constraints."""
        if not self.constraints:
            return [(0.0, 1.0) for _ in assets]
        
        # Start with the first constraint's bounds
        combined_bounds = self.constraints[0].get_bounds(assets)
        
        # Intersect with bounds from other constraints
        for constraint in self.constraints[1:]:
            constraint_bounds = constraint.get_bounds(assets)
            for i in range(len(assets)):
                lower = max(combined_bounds[i][0], constraint_bounds[i][0])
                upper = min(combined_bounds[i][1], constraint_bounds[i][1])
                combined_bounds[i] = (lower, upper)
        
        return combined_bounds
    
    def penalty_function(self, weights: np.ndarray, assets: List[str], penalty_factor: float = 1000.0) -> float:
        """Calculate penalty for constraint violations."""
        violations = self.get_violations(weights, assets)
        total_penalty = sum(violation.violation_amount for violation in violations)
        return penalty_factor * total_penalty

# Pre-defined constraint sets
def get_basic_constraints() -> ConstraintManager:
    """Get basic constraints (sum to 1, non-negative)."""
    manager = ConstraintManager()
    manager.add_constraint(WeightSumConstraint())
    manager.add_constraint(NonNegativeConstraint())
    return manager

def get_conservative_constraints() -> ConstraintManager:
    """Get conservative constraints for risk-averse investors."""
    manager = get_basic_constraints()
    
    # Limit individual asset exposure
    asset_limits = {
        "VTI": (0.0, 0.7),   # Max 70% US stocks
        "VXUS": (0.0, 0.4),  # Max 40% international stocks
        "BND": (0.1, 0.5),   # Min 10%, max 50% bonds
    }
    manager.add_constraint(IndividualAssetConstraint(asset_limits))
    
    # Asset class limits
    class_limits = {
        AssetClass.US_EQUITY: (0.3, 0.7),
        AssetClass.INTERNATIONAL_EQUITY: (0.0, 0.4),
        AssetClass.US_BONDS: (0.1, 0.5),
    }
    manager.add_constraint(AssetClassConstraint(class_limits))
    
    return manager

def get_aggressive_constraints() -> ConstraintManager:
    """Get constraints for aggressive growth investors."""
    manager = get_basic_constraints()
    
    # Allow higher equity exposure
    asset_limits = {
        "VTI": (0.0, 1.0),   # Up to 100% US stocks
        "VXUS": (0.0, 0.5),  # Up to 50% international stocks
        "BND": (0.0, 0.3),   # Max 30% bonds
    }
    manager.add_constraint(IndividualAssetConstraint(asset_limits))
    
    return manager

def get_simple_constraints(max_assets: int = 5) -> ConstraintManager:
    """Get constraints for simple portfolios."""
    manager = get_basic_constraints()
    manager.add_constraint(MaxAssetsConstraint(max_assets))
    return manager
