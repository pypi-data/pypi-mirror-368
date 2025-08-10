"""
Advanced Line Search Algorithms for SGLBO
=========================================

This module implements sophisticated line search algorithms for optimal
step size determination in gradient-based optimization. It provides
Armijo-Goldstein conditions, Wolfe conditions, backtracking methods,
and trust region approaches with adaptive parameter tuning.

Key Features:
- Armijo rule with sufficient decrease condition
- Strong and weak Wolfe conditions  
- Backtracking line search with adaptive reduction
- Trust region methods with constraint handling
- Cubic and quadratic interpolation
- Parallel line search with multiple candidates
- Constraint-aware step size computation

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Advanced Line Search Implementation
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import warnings

import numpy as np
from scipy.optimize import minimize_scalar, OptimizeResult
from scipy.interpolate import interp1d

logger = logging.getLogger(__name__)


class LineSearchStatus(Enum):
    """Status codes for line search results."""
    SUCCESS = "success"
    MAX_ITERATIONS = "max_iterations" 
    INSUFFICIENT_DECREASE = "insufficient_decrease"
    STEP_TOO_SMALL = "step_too_small"
    FUNCTION_ERROR = "function_error"
    CONSTRAINT_VIOLATION = "constraint_violation"


@dataclass
class LineSearchResult:
    """Result container for line search optimization."""
    success: bool
    status: LineSearchStatus
    step_size: float
    n_function_evals: int
    n_gradient_evals: int
    final_function_value: float
    initial_function_value: float
    function_decrease: float
    gradient_norm: float
    armijo_satisfied: bool = False
    wolfe_satisfied: bool = False
    computation_time: float = 0.0
    message: str = ""


@dataclass  
class LineSearchConfig:
    """Configuration for line search algorithms."""
    # Armijo parameters
    armijo_c1: float = 1e-4  # Sufficient decrease parameter
    
    # Wolfe parameters  
    wolfe_c2: float = 0.9    # Curvature condition parameter
    strong_wolfe: bool = False  # Use strong Wolfe conditions
    
    # Backtracking parameters
    initial_step: float = 1.0
    step_reduction_factor: float = 0.5
    step_increase_factor: float = 1.2
    min_step_size: float = 1e-10
    max_step_size: float = 2.0
    
    # Iteration limits
    max_iterations: int = 50
    max_function_evals: int = 100
    
    # Trust region parameters
    trust_radius: float = 1.0
    trust_reduction_factor: float = 0.25
    trust_increase_factor: float = 2.0
    
    # Interpolation parameters
    use_interpolation: bool = True
    interpolation_safeguard: float = 0.1
    
    # Constraint handling
    respect_bounds: bool = True
    constraint_penalty: float = 1e6


class LineSearchBase(ABC):
    """Abstract base class for line search algorithms."""
    
    def __init__(self, config: LineSearchConfig):
        self.config = config
        
    @abstractmethod
    def search(self, x: np.ndarray, direction: np.ndarray, 
              objective_function: Callable, gradient_function: Optional[Callable] = None,
              bounds: Optional[np.ndarray] = None) -> LineSearchResult:
        """Perform line search optimization."""
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Get method name."""
        pass


class ArmijoLineSearch(LineSearchBase):
    """
    Armijo line search with backtracking.
    
    Implements the Armijo rule (sufficient decrease condition) with
    backtracking to find acceptable step sizes. This is the most
    robust and commonly used line search method.
    """
    
    def search(self, x: np.ndarray, direction: np.ndarray,
              objective_function: Callable, gradient_function: Optional[Callable] = None,
              bounds: Optional[np.ndarray] = None) -> LineSearchResult:
        """
        Perform Armijo line search with backtracking.
        
        Args:
            x: Current point
            direction: Search direction (should be descent direction)
            objective_function: Function to minimize
            gradient_function: Gradient function (optional)
            bounds: Parameter bounds [n_params, 2] (optional)
            
        Returns:
            LineSearchResult with optimization details
        """
        start_time = time.time()
        
        # Initialize counters
        n_function_evals = 0
        n_gradient_evals = 0
        
        try:
            # Ensure direction is descent direction
            if gradient_function is not None:
                gradient = gradient_function(x)
                n_gradient_evals += 1
                directional_derivative = np.dot(gradient, direction)
                
                if directional_derivative >= 0:
                    logger.warning("Search direction is not descent direction")
                    direction = -gradient  # Use negative gradient
                    directional_derivative = np.dot(gradient, direction)
            else:
                # Assume direction is already descent direction
                directional_derivative = -np.linalg.norm(direction) ** 2
            
            # Initial function evaluation
            f_0 = objective_function(x)
            n_function_evals += 1
            
            # Initialize step size
            alpha = self.config.initial_step
            
            # Armijo line search loop
            for iteration in range(self.config.max_iterations):
                # Compute trial point
                x_trial = self._compute_trial_point(x, direction, alpha, bounds)
                
                # Evaluate objective at trial point
                try:
                    f_trial = objective_function(x_trial)
                    n_function_evals += 1
                except Exception as e:
                    logger.warning(f"Function evaluation failed at trial point: {e}")
                    alpha *= self.config.step_reduction_factor
                    continue
                
                # Check Armijo condition
                expected_decrease = self.config.armijo_c1 * alpha * directional_derivative
                actual_decrease = f_0 - f_trial
                
                if actual_decrease >= -expected_decrease:  # Sufficient decrease
                    # Success
                    result = LineSearchResult(
                        success=True,
                        status=LineSearchStatus.SUCCESS,
                        step_size=alpha,
                        n_function_evals=n_function_evals,
                        n_gradient_evals=n_gradient_evals,
                        final_function_value=f_trial,
                        initial_function_value=f_0,
                        function_decrease=actual_decrease,
                        gradient_norm=np.linalg.norm(direction),
                        armijo_satisfied=True,
                        computation_time=time.time() - start_time,
                        message=f"Armijo condition satisfied at iteration {iteration}"
                    )
                    return result
                
                # Reduce step size using interpolation or simple backtracking
                if self.config.use_interpolation and iteration > 0:
                    alpha = self._interpolate_step_size(alpha, f_0, f_trial, directional_derivative)
                else:
                    alpha *= self.config.step_reduction_factor
                
                # Check minimum step size
                if alpha < self.config.min_step_size:
                    result = LineSearchResult(
                        success=False,
                        status=LineSearchStatus.STEP_TOO_SMALL,
                        step_size=alpha,
                        n_function_evals=n_function_evals,
                        n_gradient_evals=n_gradient_evals,
                        final_function_value=f_trial,
                        initial_function_value=f_0,
                        function_decrease=actual_decrease,
                        gradient_norm=np.linalg.norm(direction),
                        computation_time=time.time() - start_time,
                        message="Step size too small"
                    )
                    return result
            
            # Maximum iterations reached
            result = LineSearchResult(
                success=False,
                status=LineSearchStatus.MAX_ITERATIONS,
                step_size=alpha,
                n_function_evals=n_function_evals,
                n_gradient_evals=n_gradient_evals,
                final_function_value=f_trial if 'f_trial' in locals() else f_0,
                initial_function_value=f_0,
                function_decrease=f_0 - f_trial if 'f_trial' in locals() else 0.0,
                gradient_norm=np.linalg.norm(direction),
                computation_time=time.time() - start_time,
                message="Maximum iterations reached"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in Armijo line search: {e}")
            result = LineSearchResult(
                success=False,
                status=LineSearchStatus.FUNCTION_ERROR,
                step_size=0.0,
                n_function_evals=n_function_evals,
                n_gradient_evals=n_gradient_evals,
                final_function_value=f_0 if 'f_0' in locals() else 0.0,
                initial_function_value=f_0 if 'f_0' in locals() else 0.0,
                function_decrease=0.0,
                gradient_norm=np.linalg.norm(direction),
                computation_time=time.time() - start_time,
                message=f"Function error: {e}"
            )
            return result
    
    def _compute_trial_point(self, x: np.ndarray, direction: np.ndarray,
                           step_size: float, bounds: Optional[np.ndarray] = None) -> np.ndarray:
        """Compute trial point with optional bound constraints."""
        x_trial = x + step_size * direction
        
        if bounds is not None and self.config.respect_bounds:
            # Project onto bounds
            x_trial = np.clip(x_trial, bounds[:, 0], bounds[:, 1])
        
        return x_trial
    
    def _interpolate_step_size(self, alpha: float, f_0: float, f_alpha: float,
                             grad_0: float) -> float:
        """Compute new step size using quadratic interpolation."""
        try:
            # Quadratic interpolation
            # f(alpha) ≈ f_0 + alpha * grad_0 + 0.5 * alpha^2 * a
            # Solve for minimum: grad_0 + alpha * a = 0
            a = 2 * (f_alpha - f_0 - alpha * grad_0) / (alpha ** 2)
            
            if a > 0:  # Convex case
                alpha_new = -grad_0 / (2 * a)
                # Safeguard the new step
                alpha_new = max(self.config.interpolation_safeguard * alpha,
                               min(0.9 * alpha, alpha_new))
            else:
                # Non-convex case, use simple reduction
                alpha_new = alpha * self.config.step_reduction_factor
            
            return max(alpha_new, self.config.min_step_size)
            
        except (ZeroDivisionError, ValueError):
            # Fallback to simple reduction
            return alpha * self.config.step_reduction_factor
    
    def get_method_name(self) -> str:
        return "Armijo"


class WolfeLineSearch(LineSearchBase):
    """
    Wolfe line search with curvature conditions.
    
    Implements both weak and strong Wolfe conditions for more
    sophisticated step size selection. Combines Armijo condition
    with curvature condition for better convergence properties.
    """
    
    def search(self, x: np.ndarray, direction: np.ndarray,
              objective_function: Callable, gradient_function: Optional[Callable] = None,
              bounds: Optional[np.ndarray] = None) -> LineSearchResult:
        """
        Perform Wolfe line search.
        
        Args:
            x: Current point
            direction: Search direction
            objective_function: Function to minimize
            gradient_function: Gradient function (required for Wolfe)
            bounds: Parameter bounds (optional)
            
        Returns:
            LineSearchResult with optimization details
        """
        start_time = time.time()
        
        if gradient_function is None:
            logger.error("Gradient function required for Wolfe line search")
            # Fallback to Armijo
            armijo = ArmijoLineSearch(self.config)
            return armijo.search(x, direction, objective_function, None, bounds)
        
        # Initialize counters
        n_function_evals = 0
        n_gradient_evals = 0
        
        try:
            # Initial evaluations
            f_0 = objective_function(x)
            grad_0 = gradient_function(x)
            n_function_evals += 1
            n_gradient_evals += 1
            
            # Directional derivative
            grad_0_dir = np.dot(grad_0, direction)
            
            if grad_0_dir >= 0:
                logger.warning("Search direction is not descent direction")
                direction = -grad_0
                grad_0_dir = np.dot(grad_0, direction)
            
            # Initialize step size bounds
            alpha_low = 0.0
            alpha_high = None
            alpha = self.config.initial_step
            
            f_prev = f_0
            grad_prev_dir = grad_0_dir
            
            for iteration in range(self.config.max_iterations):
                # Compute trial point
                x_trial = self._compute_trial_point(x, direction, alpha, bounds)
                
                try:
                    f_trial = objective_function(x_trial)
                    n_function_evals += 1
                except Exception as e:
                    logger.warning(f"Function evaluation failed: {e}")
                    alpha = (alpha_low + alpha) / 2 if alpha_high is None else (alpha_low + alpha_high) / 2
                    continue
                
                # Check Armijo condition
                armijo_condition = (f_trial <= f_0 + self.config.armijo_c1 * alpha * grad_0_dir)
                
                if not armijo_condition or (iteration > 0 and f_trial >= f_prev):
                    # Zoom phase
                    result = self._zoom_phase(x, direction, objective_function, gradient_function,
                                            alpha_low, alpha, f_0, grad_0_dir, bounds)
                    result.computation_time = time.time() - start_time
                    result.n_function_evals += n_function_evals
                    result.n_gradient_evals += n_gradient_evals
                    return result
                
                # Evaluate gradient at trial point
                try:
                    grad_trial = gradient_function(x_trial)
                    n_gradient_evals += 1
                    grad_trial_dir = np.dot(grad_trial, direction)
                except Exception as e:
                    logger.warning(f"Gradient evaluation failed: {e}")
                    alpha = (alpha_low + alpha) / 2 if alpha_high is None else (alpha_low + alpha_high) / 2
                    continue
                
                # Check curvature condition
                if self.config.strong_wolfe:
                    curvature_condition = abs(grad_trial_dir) <= -self.config.wolfe_c2 * grad_0_dir
                else:
                    curvature_condition = grad_trial_dir >= self.config.wolfe_c2 * grad_0_dir
                
                if curvature_condition:
                    # Both conditions satisfied
                    result = LineSearchResult(
                        success=True,
                        status=LineSearchStatus.SUCCESS,
                        step_size=alpha,
                        n_function_evals=n_function_evals,
                        n_gradient_evals=n_gradient_evals,
                        final_function_value=f_trial,
                        initial_function_value=f_0,
                        function_decrease=f_0 - f_trial,
                        gradient_norm=np.linalg.norm(direction),
                        armijo_satisfied=True,
                        wolfe_satisfied=True,
                        computation_time=time.time() - start_time,
                        message=f"Wolfe conditions satisfied at iteration {iteration}"
                    )
                    return result
                
                if grad_trial_dir >= 0:
                    # Zoom phase
                    result = self._zoom_phase(x, direction, objective_function, gradient_function,
                                            alpha_low, alpha, f_0, grad_0_dir, bounds)
                    result.computation_time = time.time() - start_time
                    result.n_function_evals += n_function_evals
                    result.n_gradient_evals += n_gradient_evals
                    return result
                
                # Update bounds and continue
                alpha_low = alpha
                f_prev = f_trial
                grad_prev_dir = grad_trial_dir
                
                # Choose new alpha
                if alpha_high is None:
                    alpha *= self.config.step_increase_factor
                else:
                    alpha = (alpha_low + alpha_high) / 2
                
                # Check bounds
                alpha = min(alpha, self.config.max_step_size)
            
            # Maximum iterations reached
            result = LineSearchResult(
                success=False,
                status=LineSearchStatus.MAX_ITERATIONS,
                step_size=alpha,
                n_function_evals=n_function_evals,
                n_gradient_evals=n_gradient_evals,
                final_function_value=f_trial if 'f_trial' in locals() else f_0,
                initial_function_value=f_0,
                function_decrease=f_0 - f_trial if 'f_trial' in locals() else 0.0,
                gradient_norm=np.linalg.norm(direction),
                computation_time=time.time() - start_time,
                message="Maximum iterations reached"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in Wolfe line search: {e}")
            result = LineSearchResult(
                success=False,
                status=LineSearchStatus.FUNCTION_ERROR,
                step_size=0.0,
                n_function_evals=n_function_evals,
                n_gradient_evals=n_gradient_evals,
                final_function_value=f_0 if 'f_0' in locals() else 0.0,
                initial_function_value=f_0 if 'f_0' in locals() else 0.0,
                function_decrease=0.0,
                gradient_norm=np.linalg.norm(direction),
                computation_time=time.time() - start_time,
                message=f"Function error: {e}"
            )
            return result
    
    def _zoom_phase(self, x: np.ndarray, direction: np.ndarray,
                   objective_function: Callable, gradient_function: Callable,
                   alpha_low: float, alpha_high: float,
                   f_0: float, grad_0_dir: float,
                   bounds: Optional[np.ndarray] = None) -> LineSearchResult:
        """Zoom phase of Wolfe line search."""
        n_function_evals = 0
        n_gradient_evals = 0
        
        for iteration in range(20):  # Zoom iteration limit
            # Interpolate new alpha
            alpha = (alpha_low + alpha_high) / 2
            
            # Compute trial point
            x_trial = self._compute_trial_point(x, direction, alpha, bounds)
            
            # Evaluate function
            try:
                f_trial = objective_function(x_trial)
                n_function_evals += 1
            except Exception:
                alpha_high = alpha
                continue
            
            # Check Armijo condition
            if f_trial > f_0 + self.config.armijo_c1 * alpha * grad_0_dir:
                alpha_high = alpha
                continue
            
            # Evaluate gradient
            try:
                grad_trial = gradient_function(x_trial)
                n_gradient_evals += 1
                grad_trial_dir = np.dot(grad_trial, direction)
            except Exception:
                alpha_high = alpha
                continue
            
            # Check curvature condition
            if self.config.strong_wolfe:
                curvature_satisfied = abs(grad_trial_dir) <= -self.config.wolfe_c2 * grad_0_dir
            else:
                curvature_satisfied = grad_trial_dir >= self.config.wolfe_c2 * grad_0_dir
            
            if curvature_satisfied:
                return LineSearchResult(
                    success=True,
                    status=LineSearchStatus.SUCCESS,
                    step_size=alpha,
                    n_function_evals=n_function_evals,
                    n_gradient_evals=n_gradient_evals,
                    final_function_value=f_trial,
                    initial_function_value=f_0,
                    function_decrease=f_0 - f_trial,
                    gradient_norm=np.linalg.norm(direction),
                    armijo_satisfied=True,
                    wolfe_satisfied=True,
                    message=f"Wolfe conditions satisfied in zoom phase at iteration {iteration}"
                )
            
            if grad_trial_dir * (alpha_high - alpha_low) >= 0:
                alpha_high = alpha_low
            
            alpha_low = alpha
        
        # Zoom failed
        return LineSearchResult(
            success=False,
            status=LineSearchStatus.MAX_ITERATIONS,
            step_size=alpha,
            n_function_evals=n_function_evals,
            n_gradient_evals=n_gradient_evals,
            final_function_value=f_trial if 'f_trial' in locals() else f_0,
            initial_function_value=f_0,
            function_decrease=f_0 - f_trial if 'f_trial' in locals() else 0.0,
            gradient_norm=np.linalg.norm(direction),
            message="Zoom phase failed to converge"
        )
    
    def _compute_trial_point(self, x: np.ndarray, direction: np.ndarray,
                           step_size: float, bounds: Optional[np.ndarray] = None) -> np.ndarray:
        """Compute trial point with optional bound constraints."""
        x_trial = x + step_size * direction
        
        if bounds is not None and self.config.respect_bounds:
            x_trial = np.clip(x_trial, bounds[:, 0], bounds[:, 1])
        
        return x_trial
    
    def get_method_name(self) -> str:
        return f"Wolfe ({'Strong' if self.config.strong_wolfe else 'Weak'})"


class TrustRegionLineSearch(LineSearchBase):
    """
    Trust region approach for step size selection.
    
    Maintains a trust region radius and adjusts step sizes based
    on the agreement between model and actual function decrease.
    """
    
    def __init__(self, config: LineSearchConfig):
        super().__init__(config)
        self.trust_radius = config.trust_radius
        self.trust_history = []
    
    def search(self, x: np.ndarray, direction: np.ndarray,
              objective_function: Callable, gradient_function: Optional[Callable] = None,
              bounds: Optional[np.ndarray] = None) -> LineSearchResult:
        """
        Perform trust region line search.
        
        Args:
            x: Current point
            direction: Search direction
            objective_function: Function to minimize
            gradient_function: Gradient function (optional)
            bounds: Parameter bounds (optional)
            
        Returns:
            LineSearchResult with optimization details
        """
        start_time = time.time()
        n_function_evals = 0
        n_gradient_evals = 0
        
        try:
            # Initial function evaluation
            f_0 = objective_function(x)
            n_function_evals += 1
            
            # Normalize direction
            direction_norm = np.linalg.norm(direction)
            if direction_norm < 1e-12:
                logger.warning("Direction vector is nearly zero")
                result = LineSearchResult(
                    success=False,
                    status=LineSearchStatus.STEP_TOO_SMALL,
                    step_size=0.0,
                    n_function_evals=n_function_evals,
                    n_gradient_evals=n_gradient_evals,
                    final_function_value=f_0,
                    initial_function_value=f_0,
                    function_decrease=0.0,
                    gradient_norm=direction_norm,
                    computation_time=time.time() - start_time,
                    message="Direction vector is nearly zero"
                )
                return result
            
            unit_direction = direction / direction_norm
            
            # Determine step size based on trust radius
            if direction_norm <= self.trust_radius:
                alpha = 1.0  # Full step within trust region
            else:
                alpha = self.trust_radius / direction_norm  # Scale to trust boundary
            
            # Compute trial point
            x_trial = self._compute_trial_point(x, direction, alpha, bounds)
            
            # Evaluate function at trial point
            try:
                f_trial = objective_function(x_trial)
                n_function_evals += 1
            except Exception as e:
                logger.warning(f"Function evaluation failed: {e}")
                self._shrink_trust_region()
                result = LineSearchResult(
                    success=False,
                    status=LineSearchStatus.FUNCTION_ERROR,
                    step_size=0.0,
                    n_function_evals=n_function_evals,
                    n_gradient_evals=n_gradient_evals,
                    final_function_value=f_0,
                    initial_function_value=f_0,
                    function_decrease=0.0,
                    gradient_norm=direction_norm,
                    computation_time=time.time() - start_time,
                    message=f"Function evaluation failed: {e}"
                )
                return result
            
            # Compute actual decrease
            actual_decrease = f_0 - f_trial
            
            # Compute predicted decrease (linear model)
            if gradient_function is not None:
                grad_0 = gradient_function(x)
                n_gradient_evals += 1
                predicted_decrease = -alpha * np.dot(grad_0, direction)
            else:
                # Estimate using function values
                predicted_decrease = max(1e-8, abs(f_0) * 0.01)  # Simple heuristic
            
            # Compute reduction ratio
            if abs(predicted_decrease) > 1e-12:
                rho = actual_decrease / predicted_decrease
            else:
                rho = 1.0 if actual_decrease > 0 else 0.0
            
            # Update trust radius based on reduction ratio
            success = rho > 0.1  # Accept step if reasonable agreement
            
            if rho < 0.25:
                # Poor agreement, shrink trust region
                self._shrink_trust_region()
            elif rho > 0.75 and abs(direction_norm - self.trust_radius) < 1e-8:
                # Good agreement and at trust boundary, expand trust region
                self._expand_trust_region()
            
            # Store trust region history
            self.trust_history.append({
                'radius': self.trust_radius,
                'rho': rho,
                'actual_decrease': actual_decrease,
                'predicted_decrease': predicted_decrease
            })
            
            # Keep limited history
            if len(self.trust_history) > 100:
                self.trust_history = self.trust_history[-50:]
            
            result = LineSearchResult(
                success=success,
                status=LineSearchStatus.SUCCESS if success else LineSearchStatus.INSUFFICIENT_DECREASE,
                step_size=alpha,
                n_function_evals=n_function_evals,
                n_gradient_evals=n_gradient_evals,
                final_function_value=f_trial,
                initial_function_value=f_0,
                function_decrease=actual_decrease,
                gradient_norm=direction_norm,
                computation_time=time.time() - start_time,
                message=f"Trust region step ({'accepted' if success else 'rejected'}), rho={rho:.3f}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error in trust region line search: {e}")
            result = LineSearchResult(
                success=False,
                status=LineSearchStatus.FUNCTION_ERROR,
                step_size=0.0,
                n_function_evals=n_function_evals,
                n_gradient_evals=n_gradient_evals,
                final_function_value=f_0 if 'f_0' in locals() else 0.0,
                initial_function_value=f_0 if 'f_0' in locals() else 0.0,
                function_decrease=0.0,
                gradient_norm=np.linalg.norm(direction),
                computation_time=time.time() - start_time,
                message=f"Function error: {e}"
            )
            return result
    
    def _shrink_trust_region(self) -> None:
        """Shrink trust region radius."""
        self.trust_radius *= self.config.trust_reduction_factor
        self.trust_radius = max(self.trust_radius, self.config.min_step_size)
    
    def _expand_trust_region(self) -> None:
        """Expand trust region radius."""
        self.trust_radius = min(self.trust_radius * self.config.trust_increase_factor,
                               self.config.max_step_size)
    
    def _compute_trial_point(self, x: np.ndarray, direction: np.ndarray,
                           step_size: float, bounds: Optional[np.ndarray] = None) -> np.ndarray:
        """Compute trial point with optional bound constraints."""
        x_trial = x + step_size * direction
        
        if bounds is not None and self.config.respect_bounds:
            x_trial = np.clip(x_trial, bounds[:, 0], bounds[:, 1])
        
        return x_trial
    
    def get_method_name(self) -> str:
        return "Trust Region"
    
    def get_trust_radius(self) -> float:
        """Get current trust radius."""
        return self.trust_radius
    
    def reset_trust_radius(self, radius: Optional[float] = None) -> None:
        """Reset trust radius to initial or specified value."""
        self.trust_radius = radius or self.config.trust_radius


class LineSearchManager:
    """
    Manager for multiple line search algorithms with automatic selection.
    
    Coordinates different line search methods and selects the most
    appropriate one based on problem characteristics and performance history.
    """
    
    def __init__(self, config: Optional[LineSearchConfig] = None):
        """
        Initialize line search manager.
        
        Args:
            config: Line search configuration
        """
        self.config = config or LineSearchConfig()
        
        # Initialize line search algorithms
        self.algorithms = {
            "armijo": ArmijoLineSearch(self.config),
            "wolfe": WolfeLineSearch(self.config),
            "trust_region": TrustRegionLineSearch(self.config)
        }
        
        # Performance tracking
        self.performance_history = {name: [] for name in self.algorithms.keys()}
        self.method_preferences = {name: 1.0 for name in self.algorithms.keys()}
    
    def search(self, x: np.ndarray, direction: np.ndarray,
              objective_function: Callable, gradient_function: Optional[Callable] = None,
              bounds: Optional[np.ndarray] = None,
              method: Optional[str] = None) -> LineSearchResult:
        """
        Perform line search using specified or automatically selected method.
        
        Args:
            x: Current point
            direction: Search direction
            objective_function: Function to minimize
            gradient_function: Gradient function (optional)
            bounds: Parameter bounds (optional) 
            method: Specific method to use (if None, auto-select)
            
        Returns:
            LineSearchResult with optimization details
        """
        if method is None:
            method = self._select_method(x, direction, gradient_function)
        
        if method not in self.algorithms:
            logger.warning(f"Method '{method}' not available, using Armijo")
            method = "armijo"
        
        # Perform line search
        result = self.algorithms[method].search(
            x, direction, objective_function, gradient_function, bounds
        )
        
        # Update performance tracking
        self._update_performance(method, result)
        
        return result
    
    def _select_method(self, x: np.ndarray, direction: np.ndarray,
                      gradient_function: Optional[Callable]) -> str:
        """Automatically select line search method."""
        # Prefer Wolfe if gradient function available
        if gradient_function is not None:
            return "wolfe"
        
        # Use Armijo as robust fallback
        return "armijo"
    
    def _update_performance(self, method: str, result: LineSearchResult) -> None:
        """Update performance history for line search methods."""
        performance_score = 0.0
        
        if result.success:
            # Base score for success
            performance_score = 1.0
            
            # Bonus for efficiency (fewer evaluations)
            if result.n_function_evals < 10:
                performance_score += 0.2
            
            # Bonus for good function decrease
            if result.function_decrease > 0:
                performance_score += 0.1
            
            # Bonus for fast computation
            if result.computation_time < 0.1:
                performance_score += 0.1
        
        # Store performance
        self.performance_history[method].append(performance_score)
        
        # Keep limited history
        if len(self.performance_history[method]) > 50:
            self.performance_history[method] = self.performance_history[method][-25:]
        
        # Update method preferences
        recent_performance = np.mean(self.performance_history[method][-10:])
        self.method_preferences[method] = 0.9 * self.method_preferences[method] + 0.1 * recent_performance
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all line search methods."""
        summary = {}
        
        for method, history in self.performance_history.items():
            if history:
                summary[method] = {
                    "average_performance": np.mean(history),
                    "recent_performance": np.mean(history[-5:]) if len(history) >= 5 else np.mean(history),
                    "success_rate": np.mean([1.0 if score > 0.5 else 0.0 for score in history]),
                    "preference_score": self.method_preferences[method],
                    "total_calls": len(history)
                }
            else:
                summary[method] = {
                    "average_performance": 0.0,
                    "recent_performance": 0.0,
                    "success_rate": 0.0,
                    "preference_score": self.method_preferences[method],
                    "total_calls": 0
                }
        
        return summary
    
    def reset_performance_history(self) -> None:
        """Reset performance tracking."""
        self.performance_history = {name: [] for name in self.algorithms.keys()}
        self.method_preferences = {name: 1.0 for name in self.algorithms.keys()}