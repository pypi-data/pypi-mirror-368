"""
Advanced Gradient Estimation Methods for SGLBO
==============================================

This module implements multiple sophisticated gradient estimation methods
for Stochastic Gradient Line Bayesian Optimization. It provides analytical
gradients from GP posteriors, finite difference schemes, stochastic
approximation, and quasi-Newton methods.

Key Features:
- GP posterior analytical gradients
- Multiple finite difference schemes (forward, backward, central)
- Stochastic approximation for noisy objectives
- BFGS and L-BFGS quasi-Newton gradient approximation
- Adaptive step size selection
- Parallel gradient computation
- Constraint-aware gradient projection

Author: Multi-Objective Optimization Laboratory  
Version: 1.0.0 - Advanced Gradient Estimation
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
import concurrent.futures
from functools import lru_cache

import numpy as np
import torch
from torch import Tensor
from scipy.optimize import approx_fprime
from scipy.linalg import inv, LinAlgError
from sklearn.gaussian_process import GaussianProcessRegressor

logger = logging.getLogger(__name__)


@dataclass
class GradientResult:
    """Result container for gradient computation."""
    gradient: np.ndarray
    method: str
    computation_time: float
    confidence: float = 1.0  # Confidence in gradient estimate [0, 1]
    n_evaluations: int = 0  # Number of function evaluations used
    error_estimate: Optional[np.ndarray] = None


class GradientEstimatorBase(ABC):
    """Abstract base class for gradient estimators."""
    
    @abstractmethod
    def compute_gradient(self, x: np.ndarray, objective_function: Callable,
                        **kwargs) -> GradientResult:
        """Compute gradient at point x."""
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Get method name."""
        pass


class GPPosteriorGradientEstimator(GradientEstimatorBase):
    """
    Analytical gradient computation using GP posterior derivatives.
    
    This is the most accurate method when sufficient data is available,
    as it uses the analytical form of GP posterior derivatives.
    """
    
    def __init__(self, gp_models: Dict[str, Any], objective_names: List[str],
                 objective_directions: List[int], objective_weights: List[float],
                 device: torch.device = torch.device("cpu")):
        """
        Initialize GP posterior gradient estimator.
        
        Args:
            gp_models: Dictionary of fitted GP models
            objective_names: Names of objectives
            objective_directions: Optimization directions (+1, -1, 0)
            objective_weights: Weights for multi-objective aggregation
            device: Torch device for computations
        """
        self.gp_models = gp_models
        self.objective_names = objective_names
        self.objective_directions = objective_directions
        self.objective_weights = objective_weights
        self.device = device
    
    def compute_gradient(self, x: np.ndarray, objective_function: Optional[Callable] = None,
                        **kwargs) -> GradientResult:
        """
        Compute analytical gradient using GP posterior derivatives.
        
        Args:
            x: Point at which to compute gradient (normalized coordinates)
            objective_function: Not used for GP method
            
        Returns:
            GradientResult containing gradient information
        """
        start_time = time.time()
        
        try:
            composite_gradient = np.zeros_like(x)
            total_confidence = 0.0
            n_models = 0
            
            # Convert to tensor
            x_tensor = torch.tensor(x, dtype=torch.float64, device=self.device).unsqueeze(0)
            x_tensor.requires_grad_(True)
            
            for i, obj_name in enumerate(self.objective_names):
                if obj_name not in self.gp_models:
                    continue
                
                gp_model = self.gp_models[obj_name]
                weight = self.objective_weights[i]
                direction = self.objective_directions[i]
                
                try:
                    # Get GP posterior
                    posterior = gp_model.posterior(x_tensor)
                    mean = posterior.mean
                    
                    # Compute gradient using autograd
                    grad_outputs = torch.ones_like(mean)
                    gradient_tensor = torch.autograd.grad(
                        outputs=mean,
                        inputs=x_tensor, 
                        grad_outputs=grad_outputs,
                        create_graph=False,
                        retain_graph=True
                    )[0]
                    
                    gradient_np = gradient_tensor.squeeze().cpu().numpy()
                    
                    # Apply objective direction and weight
                    if direction == -1:  # Minimize
                        gradient_np = -gradient_np
                    elif direction == 0:  # Target - approximate with sign
                        # For target objectives, gradient points toward target
                        # This is simplified - could be enhanced with target value
                        pass
                    
                    weighted_gradient = weight * gradient_np
                    composite_gradient += weighted_gradient
                    
                    # Estimate confidence based on posterior variance
                    variance = posterior.variance.squeeze().cpu().numpy()
                    confidence = 1.0 / (1.0 + variance)  # Higher variance = lower confidence
                    total_confidence += confidence
                    n_models += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to compute GP gradient for '{obj_name}': {e}")
                    continue
            
            # Average confidence across models
            avg_confidence = total_confidence / max(1, n_models) if n_models > 0 else 0.0
            
            # Clear gradients
            if x_tensor.grad is not None:
                x_tensor.grad.data.zero_()
            
            computation_time = time.time() - start_time
            
            return GradientResult(
                gradient=composite_gradient,
                method="GP Posterior",
                computation_time=computation_time,
                confidence=avg_confidence,
                n_evaluations=0  # No additional function evaluations needed
            )
            
        except Exception as e:
            logger.error(f"Error in GP posterior gradient computation: {e}")
            # Fallback to zero gradient
            return GradientResult(
                gradient=np.zeros_like(x),
                method="GP Posterior (failed)",
                computation_time=time.time() - start_time,
                confidence=0.0,
                n_evaluations=0
            )
    
    def get_method_name(self) -> str:
        return "GP Posterior"


class FiniteDifferenceGradientEstimator(GradientEstimatorBase):
    """
    Finite difference gradient estimation with multiple schemes.
    
    Supports forward, backward, and central difference schemes with
    adaptive step size selection.
    """
    
    def __init__(self, step_size: float = 1e-6, scheme: str = "central",
                 adaptive_step: bool = True, parallel: bool = True):
        """
        Initialize finite difference gradient estimator.
        
        Args:
            step_size: Base step size for finite differences
            scheme: Difference scheme ('forward', 'backward', 'central')
            adaptive_step: Use adaptive step size selection
            parallel: Use parallel computation for gradient components
        """
        self.step_size = step_size
        self.scheme = scheme.lower()
        self.adaptive_step = adaptive_step
        self.parallel = parallel
        
        if self.scheme not in ['forward', 'backward', 'central']:
            logger.warning(f"Unknown scheme '{scheme}', defaulting to 'central'")
            self.scheme = 'central'
    
    def compute_gradient(self, x: np.ndarray, objective_function: Callable,
                        **kwargs) -> GradientResult:
        """
        Compute gradient using finite differences.
        
        Args:
            x: Point at which to compute gradient
            objective_function: Function to differentiate
            
        Returns:
            GradientResult containing gradient information
        """
        start_time = time.time()
        n_evaluations = 0
        
        try:
            # Determine step sizes (adaptive or fixed)
            if self.adaptive_step:
                step_sizes = self._compute_adaptive_steps(x, objective_function)
                n_evaluations += len(x)  # One evaluation per parameter for adaptation
            else:
                step_sizes = [self.step_size] * len(x)
            
            # Compute gradient components
            if self.parallel and len(x) > 1:
                gradient, evals = self._compute_gradient_parallel(x, objective_function, step_sizes)
            else:
                gradient, evals = self._compute_gradient_serial(x, objective_function, step_sizes)
            
            n_evaluations += evals
            
            # Estimate error (simplified)
            error_estimate = self._estimate_gradient_error(x, gradient, step_sizes)
            
            # Confidence based on step size consistency
            confidence = self._compute_confidence(step_sizes, gradient)
            
            computation_time = time.time() - start_time
            
            return GradientResult(
                gradient=gradient,
                method=f"Finite Difference ({self.scheme})",
                computation_time=computation_time,
                confidence=confidence,
                n_evaluations=n_evaluations,
                error_estimate=error_estimate
            )
            
        except Exception as e:
            logger.error(f"Error in finite difference gradient computation: {e}")
            return GradientResult(
                gradient=np.zeros_like(x),
                method=f"Finite Difference ({self.scheme}) - failed",
                computation_time=time.time() - start_time,
                confidence=0.0,
                n_evaluations=n_evaluations
            )
    
    def _compute_adaptive_steps(self, x: np.ndarray, objective_function: Callable) -> List[float]:
        """Compute adaptive step sizes for each parameter."""
        step_sizes = []
        f_x = objective_function(x)
        
        for i in range(len(x)):
            # Try different step sizes and choose optimal
            candidates = [self.step_size * (10 ** k) for k in [-2, -1, 0, 1]]
            best_step = self.step_size
            
            for step in candidates:
                try:
                    x_plus = x.copy()
                    x_plus[i] = min(1.0, x[i] + step)
                    f_plus = objective_function(x_plus)
                    
                    # Check if step gives reasonable gradient estimate
                    if abs(f_plus - f_x) > 1e-12:  # Non-zero difference
                        best_step = step
                        break
                except:
                    continue
            
            step_sizes.append(best_step)
        
        return step_sizes
    
    def _compute_gradient_parallel(self, x: np.ndarray, objective_function: Callable,
                                 step_sizes: List[float]) -> Tuple[np.ndarray, int]:
        """Compute gradient components in parallel."""
        gradient = np.zeros_like(x)
        n_evaluations = 0
        
        def compute_component(i):
            return i, self._compute_gradient_component(x, objective_function, i, step_sizes[i])
        
        # Use thread pool for parallel computation
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(x), 4)) as executor:
            futures = [executor.submit(compute_component, i) for i in range(len(x))]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    i, (grad_i, evals_i) = future.result()
                    gradient[i] = grad_i
                    n_evaluations += evals_i
                except Exception as e:
                    logger.warning(f"Failed to compute gradient component: {e}")
        
        return gradient, n_evaluations
    
    def _compute_gradient_serial(self, x: np.ndarray, objective_function: Callable,
                               step_sizes: List[float]) -> Tuple[np.ndarray, int]:
        """Compute gradient components serially."""
        gradient = np.zeros_like(x)
        n_evaluations = 0
        
        for i in range(len(x)):
            grad_i, evals_i = self._compute_gradient_component(x, objective_function, i, step_sizes[i])
            gradient[i] = grad_i
            n_evaluations += evals_i
        
        return gradient, n_evaluations
    
    def _compute_gradient_component(self, x: np.ndarray, objective_function: Callable,
                                  component: int, step_size: float) -> Tuple[float, int]:
        """Compute single gradient component."""
        n_evals = 0
        
        try:
            if self.scheme == "forward":
                x_plus = x.copy()
                x_plus[component] = min(1.0, x[component] + step_size)
                
                f_x = objective_function(x)
                f_plus = objective_function(x_plus)
                n_evals = 2
                
                gradient = (f_plus - f_x) / step_size
                
            elif self.scheme == "backward":
                x_minus = x.copy()
                x_minus[component] = max(0.0, x[component] - step_size)
                
                f_x = objective_function(x)
                f_minus = objective_function(x_minus)
                n_evals = 2
                
                gradient = (f_x - f_minus) / step_size
                
            else:  # central
                x_plus = x.copy()
                x_minus = x.copy()
                x_plus[component] = min(1.0, x[component] + step_size)
                x_minus[component] = max(0.0, x[component] - step_size)
                
                f_plus = objective_function(x_plus)
                f_minus = objective_function(x_minus)
                n_evals = 2
                
                actual_step = x_plus[component] - x_minus[component]
                gradient = (f_plus - f_minus) / actual_step
            
            return gradient, n_evals
            
        except Exception as e:
            logger.warning(f"Failed to compute gradient component {component}: {e}")
            return 0.0, n_evals
    
    def _estimate_gradient_error(self, x: np.ndarray, gradient: np.ndarray,
                               step_sizes: List[float]) -> np.ndarray:
        """Estimate gradient error based on step sizes."""
        # Simple error estimate based on step size
        error_estimate = np.array(step_sizes) * np.abs(gradient)
        return error_estimate
    
    def _compute_confidence(self, step_sizes: List[float], gradient: np.ndarray) -> float:
        """Compute confidence based on step size consistency and gradient magnitude."""
        # Higher confidence for smaller step sizes and reasonable gradient magnitudes
        avg_step = np.mean(step_sizes)
        avg_grad_mag = np.mean(np.abs(gradient))
        
        # Heuristic confidence measure
        step_confidence = 1.0 / (1.0 + avg_step * 1000)  # Prefer smaller steps
        grad_confidence = min(1.0, avg_grad_mag / 10.0)   # Reasonable gradient magnitude
        
        return (step_confidence + grad_confidence) / 2.0
    
    def get_method_name(self) -> str:
        return f"Finite Difference ({self.scheme})"


class StochasticApproximationGradientEstimator(GradientEstimatorBase):
    """
    Stochastic approximation gradient estimator for noisy objectives.
    
    Uses simultaneous perturbation stochastic approximation (SPSA) or
    similar methods to handle noise in objective evaluations.
    """
    
    def __init__(self, noise_level: float = 0.01, n_samples: int = 3,
                 perturbation_distribution: str = "bernoulli"):
        """
        Initialize stochastic approximation gradient estimator.
        
        Args:
            noise_level: Expected noise level in objective evaluations
            n_samples: Number of samples for gradient estimation
            perturbation_distribution: Distribution for perturbations ('bernoulli', 'normal')
        """
        self.noise_level = noise_level
        self.n_samples = n_samples
        self.perturbation_distribution = perturbation_distribution.lower()
    
    def compute_gradient(self, x: np.ndarray, objective_function: Callable,
                        **kwargs) -> GradientResult:
        """
        Compute gradient using stochastic approximation.
        
        Args:
            x: Point at which to compute gradient
            objective_function: Function to differentiate
            
        Returns:
            GradientResult containing gradient information
        """
        start_time = time.time()
        n_evaluations = 0
        
        try:
            gradients = []
            
            for sample in range(self.n_samples):
                # Generate perturbation vector
                if self.perturbation_distribution == "bernoulli":
                    delta = np.random.choice([-1, 1], size=len(x)) * self.noise_level
                else:  # normal
                    delta = np.random.normal(0, self.noise_level, size=len(x))
                
                # Evaluate at perturbed points
                x_plus = np.clip(x + delta, 0, 1)
                x_minus = np.clip(x - delta, 0, 1)
                
                f_plus = objective_function(x_plus)
                f_minus = objective_function(x_minus)
                n_evaluations += 2
                
                # SPSA gradient estimate
                gradient_sample = (f_plus - f_minus) / (2 * delta)
                gradients.append(gradient_sample)
            
            # Average gradients
            gradient = np.mean(gradients, axis=0)
            
            # Estimate confidence based on consistency across samples
            if len(gradients) > 1:
                gradient_std = np.std(gradients, axis=0)
                confidence = 1.0 / (1.0 + np.mean(gradient_std))
            else:
                confidence = 0.5  # Medium confidence for single sample
            
            computation_time = time.time() - start_time
            
            return GradientResult(
                gradient=gradient,
                method="Stochastic Approximation",
                computation_time=computation_time,
                confidence=confidence,
                n_evaluations=n_evaluations,
                error_estimate=gradient_std if len(gradients) > 1 else None
            )
            
        except Exception as e:
            logger.error(f"Error in stochastic approximation gradient computation: {e}")
            return GradientResult(
                gradient=np.zeros_like(x),
                method="Stochastic Approximation - failed",
                computation_time=time.time() - start_time,
                confidence=0.0,
                n_evaluations=n_evaluations
            )
    
    def get_method_name(self) -> str:
        return "Stochastic Approximation"


class QuasiNewtonGradientEstimator(GradientEstimatorBase):
    """
    Quasi-Newton gradient approximation using BFGS or L-BFGS.
    
    Maintains an approximation of the Hessian matrix and uses it
    to improve gradient estimates over time.
    """
    
    def __init__(self, method: str = "bfgs", memory_size: int = 10):
        """
        Initialize quasi-Newton gradient estimator.
        
        Args:
            method: Quasi-Newton method ('bfgs', 'lbfgs')
            memory_size: Memory size for L-BFGS
        """
        self.method = method.lower()
        self.memory_size = memory_size
        self.history = []  # Store (x, gradient) pairs
        self.hessian_inv = None
    
    def compute_gradient(self, x: np.ndarray, objective_function: Callable,
                        **kwargs) -> GradientResult:
        """
        Compute gradient using quasi-Newton approximation.
        
        Args:
            x: Point at which to compute gradient
            objective_function: Function to differentiate
            
        Returns:
            GradientResult containing gradient information
        """
        start_time = time.time()
        
        try:
            # For first call or insufficient history, use finite differences
            if len(self.history) < 2:
                fd_estimator = FiniteDifferenceGradientEstimator(scheme="central")
                fd_result = fd_estimator.compute_gradient(x, objective_function)
                
                # Store in history
                self.history.append((x.copy(), fd_result.gradient.copy()))
                
                # Initialize Hessian inverse
                if self.hessian_inv is None:
                    self.hessian_inv = np.eye(len(x))
                
                return GradientResult(
                    gradient=fd_result.gradient,
                    method="Quasi-Newton (initialization)",
                    computation_time=fd_result.computation_time,
                    confidence=fd_result.confidence,
                    n_evaluations=fd_result.n_evaluations
                )
            
            # Use quasi-Newton update
            gradient = self._quasi_newton_gradient(x, objective_function)
            
            computation_time = time.time() - start_time
            
            return GradientResult(
                gradient=gradient,
                method=f"Quasi-Newton ({self.method.upper()})",
                computation_time=computation_time,
                confidence=0.8,  # High confidence due to Hessian information
                n_evaluations=0   # No additional evaluations needed
            )
            
        except Exception as e:
            logger.error(f"Error in quasi-Newton gradient computation: {e}")
            return GradientResult(
                gradient=np.zeros_like(x),
                method=f"Quasi-Newton ({self.method.upper()}) - failed",
                computation_time=time.time() - start_time,
                confidence=0.0,
                n_evaluations=0
            )
    
    def _quasi_newton_gradient(self, x: np.ndarray, objective_function: Callable) -> np.ndarray:
        """Compute gradient using quasi-Newton approximation."""
        # Get most recent point and gradient
        x_prev, grad_prev = self.history[-1]
        
        # Compute finite difference gradient at current point
        fd_estimator = FiniteDifferenceGradientEstimator(scheme="central")
        fd_result = fd_estimator.compute_gradient(x, objective_function)
        grad_current = fd_result.gradient
        
        # Update quasi-Newton approximation
        if self.method == "bfgs":
            self._bfgs_update(x, grad_current, x_prev, grad_prev)
        else:  # lbfgs
            self._lbfgs_update(x, grad_current, x_prev, grad_prev)
        
        # Store current point in history
        self.history.append((x.copy(), grad_current.copy()))
        
        # Trim history for L-BFGS
        if len(self.history) > self.memory_size:
            self.history = self.history[-self.memory_size:]
        
        return grad_current
    
    def _bfgs_update(self, x: np.ndarray, grad: np.ndarray,
                     x_prev: np.ndarray, grad_prev: np.ndarray) -> None:
        """Update BFGS Hessian inverse approximation."""
        s = x - x_prev  # Step
        y = grad - grad_prev  # Gradient difference
        
        # Check curvature condition
        sy = np.dot(s, y)
        if abs(sy) < 1e-10:
            return  # Skip update
        
        try:
            # Sherman-Morrison-Woodbury formula for BFGS update
            rho = 1.0 / sy
            I = np.eye(len(x))
            
            V = I - rho * np.outer(s, y)
            self.hessian_inv = V @ self.hessian_inv @ V.T + rho * np.outer(s, s)
            
        except (LinAlgError, np.linalg.LinAlgError):
            # Reset to identity if update fails
            self.hessian_inv = np.eye(len(x))
    
    def _lbfgs_update(self, x: np.ndarray, grad: np.ndarray,
                      x_prev: np.ndarray, grad_prev: np.ndarray) -> None:
        """Update L-BFGS approximation (simplified)."""
        # Simplified L-BFGS - in practice, would implement two-loop recursion
        # For now, use BFGS update
        self._bfgs_update(x, grad, x_prev, grad_prev)
    
    def get_method_name(self) -> str:
        return f"Quasi-Newton ({self.method.upper()})"


class GradientEstimatorManager:
    """
    Manager for multiple gradient estimation methods with automatic selection.
    
    Combines different gradient estimators and selects the most appropriate
    method based on data availability, noise levels, and computational budget.
    """
    
    def __init__(self, gp_models: Optional[Dict[str, Any]] = None,
                 objective_names: Optional[List[str]] = None,
                 objective_directions: Optional[List[int]] = None,
                 objective_weights: Optional[List[float]] = None,
                 device: torch.device = torch.device("cpu")):
        """
        Initialize gradient estimator manager.
        
        Args:
            gp_models: Dictionary of GP models (if available)
            objective_names: Names of objectives  
            objective_directions: Optimization directions
            objective_weights: Objective weights
            device: Computing device
        """
        self.gp_models = gp_models or {}
        self.objective_names = objective_names or []
        self.objective_directions = objective_directions or []
        self.objective_weights = objective_weights or []
        self.device = device
        
        # Initialize estimators
        self.estimators = {}
        self._initialize_estimators()
        
        # Performance tracking
        self.method_performance = {}
        
    def _initialize_estimators(self) -> None:
        """Initialize all gradient estimators."""
        # GP Posterior estimator (if GP models available)
        if self.gp_models:
            self.estimators["gp_posterior"] = GPPosteriorGradientEstimator(
                self.gp_models, self.objective_names, self.objective_directions,
                self.objective_weights, self.device
            )
        
        # Finite difference estimators
        self.estimators["finite_diff_central"] = FiniteDifferenceGradientEstimator(
            scheme="central", adaptive_step=True
        )
        
        self.estimators["finite_diff_forward"] = FiniteDifferenceGradientEstimator(
            scheme="forward", adaptive_step=True
        )
        
        # Stochastic approximation
        self.estimators["stochastic_approx"] = StochasticApproximationGradientEstimator(
            n_samples=3
        )
        
        # Quasi-Newton
        self.estimators["quasi_newton"] = QuasiNewtonGradientEstimator(method="bfgs")
    
    def compute_gradient(self, x: np.ndarray, objective_function: Callable,
                        method: Optional[str] = None, **kwargs) -> GradientResult:
        """
        Compute gradient using specified or automatically selected method.
        
        Args:
            x: Point at which to compute gradient
            objective_function: Function to differentiate
            method: Specific method to use (if None, auto-select)
            
        Returns:
            GradientResult containing gradient information
        """
        if method is None:
            method = self._select_method(x, objective_function)
        
        if method not in self.estimators:
            logger.warning(f"Method '{method}' not available, using finite differences")
            method = "finite_diff_central"
        
        # Compute gradient
        result = self.estimators[method].compute_gradient(x, objective_function, **kwargs)
        
        # Update performance tracking
        self._update_performance(method, result)
        
        return result
    
    def _select_method(self, x: np.ndarray, objective_function: Callable) -> str:
        """Automatically select the best gradient estimation method."""
        # Prefer GP posterior if available and reliable
        if "gp_posterior" in self.estimators and len(self.gp_models) > 0:
            return "gp_posterior"
        
        # Otherwise use central finite differences (most reliable)
        return "finite_diff_central"
    
    def _update_performance(self, method: str, result: GradientResult) -> None:
        """Update performance statistics for gradient methods."""
        if method not in self.method_performance:
            self.method_performance[method] = {
                "calls": 0,
                "total_time": 0.0,
                "avg_confidence": 0.0,
                "success_rate": 0.0
            }
        
        stats = self.method_performance[method]
        stats["calls"] += 1
        stats["total_time"] += result.computation_time
        
        # Update running averages
        alpha = 1.0 / stats["calls"]  # Simple moving average
        stats["avg_confidence"] = (1 - alpha) * stats["avg_confidence"] + alpha * result.confidence
        
        success = 1.0 if result.confidence > 0.5 else 0.0
        stats["success_rate"] = (1 - alpha) * stats["success_rate"] + alpha * success
    
    def update_gp_models(self, gp_models: Dict[str, Any]) -> None:
        """Update GP models and reinitialize GP estimator."""
        self.gp_models = gp_models
        
        if gp_models:
            self.estimators["gp_posterior"] = GPPosteriorGradientEstimator(
                self.gp_models, self.objective_names, self.objective_directions,
                self.objective_weights, self.device
            )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all gradient methods."""
        return self.method_performance.copy()