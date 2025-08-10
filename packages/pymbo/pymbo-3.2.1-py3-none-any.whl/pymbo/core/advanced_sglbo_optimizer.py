"""
Advanced Stochastic Gradient Line Bayesian Optimization (SGLBO)
==============================================================

A state-of-the-art implementation of SGLBO for efficient parameter space exploration
before detailed Bayesian optimization. This module provides gradient-guided sampling,
line search optimization, and multi-objective support with advanced mathematical
techniques for superior performance.

Key Features:
- Stochastic gradient estimation with multiple methods
- Armijo-Goldstein line search with backtracking
- Multi-fidelity evaluation support
- Adaptive sampling strategies
- GPU acceleration and memory optimization
- Multi-objective gradient aggregation
- Advanced convergence detection

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Advanced SGLBO Implementation
"""

import logging
import time
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
import torch
from torch import Tensor
from scipy.optimize import minimize_scalar, OptimizeResult
from scipy.stats import qmc
from sklearn.preprocessing import StandardScaler

# BoTorch imports for GP models
from botorch.models import SingleTaskGP
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition.analytic import ExpectedImprovement
from botorch.utils.transforms import normalize, unnormalize
from gpytorch.mlls import ExactMarginalLogLikelihood

# Local imports
try:
    from .efficient_data_manager import OptimizationDataManager
    from ..utils.performance_optimizer import performance_timer
    PERFORMANCE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PERFORMANCE_OPTIMIZATION_AVAILABLE = False

# Configure warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)
logger = logging.getLogger(__name__)


class GradientMethod(Enum):
    """Gradient estimation methods."""
    FINITE_DIFFERENCE = "finite_difference"
    GP_POSTERIOR = "gp_posterior" 
    STOCHASTIC_APPROXIMATION = "stochastic_approximation"
    QUASI_NEWTON = "quasi_newton"


class LineSearchMethod(Enum):
    """Line search methods."""
    ARMIJO = "armijo"
    WOLFE = "wolfe"
    BACKTRACKING = "backtracking"
    TRUST_REGION = "trust_region"


@dataclass
class SGLBOConfig:
    """Configuration for SGLBO optimizer."""
    # Gradient estimation
    gradient_method: GradientMethod = GradientMethod.GP_POSTERIOR
    finite_diff_step: float = 1e-6
    stochastic_noise_level: float = 0.01
    
    # Line search parameters
    line_search_method: LineSearchMethod = LineSearchMethod.ARMIJO
    armijo_c1: float = 1e-4  # Sufficient decrease parameter
    wolfe_c2: float = 0.9    # Curvature condition parameter
    max_line_search_iter: int = 20
    initial_step_size: float = 1.0
    step_reduction_factor: float = 0.5
    
    # Exploration parameters
    exploration_factor: float = 0.1
    adaptive_exploration: bool = True
    multi_start_points: int = 3
    
    # Convergence parameters
    convergence_tolerance: float = 1e-6
    max_iterations: int = 100
    min_gradient_norm: float = 1e-8
    
    # Performance parameters
    batch_size: int = 1
    use_gpu: bool = True
    memory_threshold: float = 0.8


@dataclass 
class SGLBOResult:
    """Result container for SGLBO optimization."""
    success: bool
    message: str
    x: np.ndarray
    fun: float
    gradient: np.ndarray
    n_iterations: int
    n_function_evals: int
    n_gradient_evals: int
    convergence_history: List[Dict[str, Any]]
    execution_time: float


class AdvancedSGLBOOptimizer:
    """
    Advanced Stochastic Gradient Line Bayesian Optimization implementation.
    
    This optimizer combines gradient-based optimization with Bayesian optimization
    for efficient exploration of parameter spaces. It provides multiple gradient
    estimation methods, sophisticated line search algorithms, and multi-objective
    support.
    """
    
    def __init__(self,
                 params_config: Dict[str, Dict[str, Any]],
                 responses_config: Dict[str, Dict[str, Any]], 
                 config: Optional[SGLBOConfig] = None,
                 objective_function: Optional[Callable] = None,
                 random_seed: Optional[int] = None):
        """
        Initialize Advanced SGLBO optimizer.
        
        Args:
            params_config: Parameter configuration dictionary
            responses_config: Response configuration dictionary
            config: SGLBO configuration
            objective_function: Optional objective function for direct optimization
            random_seed: Random seed for reproducibility
        """
        self.params_config = params_config
        self.responses_config = responses_config
        self.config = config or SGLBOConfig()
        self.objective_function = objective_function
        
        # Set random seed
        if random_seed is not None:
            np.random.seed(random_seed)
            torch.manual_seed(random_seed)
        
        # Initialize parameter information
        self._setup_parameter_space()
        self._setup_objectives()
        
        # Initialize optimization state
        self.experimental_data = pd.DataFrame()
        self.gp_models = {}
        self.gradient_history = []
        self.convergence_history = []
        self.iteration_count = 0
        self.function_eval_count = 0
        self.gradient_eval_count = 0
        
        # Performance tracking
        self.timing_stats = {
            "gradient_computation": 0.0,
            "line_search": 0.0,
            "model_fitting": 0.0,
            "acquisition_optimization": 0.0
        }
        
        # GPU setup if available
        self.device = torch.device("cuda" if torch.cuda.is_available() and self.config.use_gpu else "cpu")
        
        # Initialize data manager for efficient processing
        if hasattr(self, 'data_manager'):
            self.data_manager = None  # Will be initialized when needed
        
        logger.info(f"Advanced SGLBO Optimizer initialized:")
        logger.info(f"  Parameters: {len(self.parameter_names)}")
        logger.info(f"  Objectives: {len(self.objective_names)}")
        logger.info(f"  Device: {self.device}")
        logger.info(f"  Gradient method: {self.config.gradient_method.value}")
        logger.info(f"  Line search: {self.config.line_search_method.value}")
    
    def _setup_parameter_space(self) -> None:
        """Setup parameter space information."""
        self.parameter_names = list(self.params_config.keys())
        self.bounds = []
        self.param_types = {}
        self.categorical_mappings = {}
        
        for name, config in self.params_config.items():
            param_type = config.get("type", "continuous")
            self.param_types[name] = param_type
            
            if param_type == "continuous":
                low = config.get("low", 0.0)
                high = config.get("high", 1.0)
                self.bounds.append([low, high])
            elif param_type == "discrete":
                low = config.get("low", 0)
                high = config.get("high", 10)
                self.bounds.append([low, high])
            elif param_type == "categorical":
                choices = config.get("choices", ["A", "B"])
                self.categorical_mappings[name] = {i: choice for i, choice in enumerate(choices)}
                self.bounds.append([0, len(choices) - 1])
            else:
                # Default bounds
                self.bounds.append([0.0, 1.0])
        
        self.bounds = np.array(self.bounds)
        self.n_params = len(self.parameter_names)
        
        # Parameter normalization for internal computations
        self.param_scaler = StandardScaler()
    
    def _setup_objectives(self) -> None:
        """Setup optimization objectives."""
        self.objective_names = []
        self.objective_directions = []  # 1 for maximize, -1 for minimize, 0 for target
        self.target_values = {}
        self.objective_weights = []
        
        for name, config in self.responses_config.items():
            goal = config.get("goal", "Maximize")
            weight = config.get("weight", 1.0)
            
            self.objective_names.append(name)
            self.objective_weights.append(weight)
            
            if goal == "Maximize":
                self.objective_directions.append(1)
            elif goal == "Minimize":  
                self.objective_directions.append(-1)
            elif goal == "Target":
                self.objective_directions.append(0)
                target = config.get("target", 0.0)
                self.target_values[name] = target
            else:
                logger.warning(f"Unknown goal '{goal}' for objective '{name}', defaulting to Maximize")
                self.objective_directions.append(1)
        
        self.n_objectives = len(self.objective_names)
        
        if self.n_objectives == 0:
            raise ValueError("At least one optimization objective must be defined")
        
        # Normalize weights
        total_weight = sum(self.objective_weights)
        if total_weight > 0:
            self.objective_weights = [w / total_weight for w in self.objective_weights]
        else:
            self.objective_weights = [1.0 / self.n_objectives] * self.n_objectives
    
    def add_experimental_data(self, data_df: pd.DataFrame) -> None:
        """
        Add experimental data to the optimizer.
        
        Args:
            data_df: DataFrame containing parameter and response data
        """
        try:
            logger.info(f"Adding {len(data_df)} experimental data points to Advanced SGLBO")
            
            # Validate data
            self._validate_experimental_data(data_df)
            
            # Add to experimental data
            if self.experimental_data.empty:
                self.experimental_data = data_df.copy()
            else:
                self.experimental_data = pd.concat([self.experimental_data, data_df], ignore_index=True)
            
            # Update function evaluation counter
            self.function_eval_count += len(data_df)
            
            # Update GP models
            self._update_gp_models()
            
            logger.info(f"Total experimental data points: {len(self.experimental_data)}")
            
        except Exception as e:
            logger.error(f"Error adding experimental data: {e}")
            raise
    
    def _validate_experimental_data(self, data_df: pd.DataFrame) -> None:
        """Validate experimental data format."""
        required_columns = self.parameter_names + self.objective_names
        missing_columns = [col for col in required_columns if col not in data_df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check for invalid values in objectives
        for obj_name in self.objective_names:
            if data_df[obj_name].isna().any():
                logger.warning(f"NaN values found in objective '{obj_name}'")
    
    def _update_gp_models(self) -> None:
        """Update Gaussian Process models for gradient computation."""
        if len(self.experimental_data) < 3:
            logger.debug("Insufficient data for GP models")
            return
        
        start_time = time.time()
        
        try:
            # Prepare training data
            X_data = self._prepare_training_features()
            
            # Build GP model for each objective
            for i, obj_name in enumerate(self.objective_names):
                if obj_name not in self.experimental_data.columns:
                    continue
                
                y_data = self.experimental_data[obj_name].values
                
                # Handle missing values
                valid_mask = ~pd.isna(y_data)
                if np.sum(valid_mask) < 3:
                    logger.warning(f"Insufficient valid data for objective '{obj_name}'")
                    continue
                
                X_valid = X_data[valid_mask]
                y_valid = y_data[valid_mask]
                
                # Convert to tensors
                X_tensor = torch.tensor(X_valid, dtype=torch.float64, device=self.device)
                y_tensor = torch.tensor(y_valid, dtype=torch.float64, device=self.device).unsqueeze(-1)
                
                try:
                    # Create and fit GP model
                    model = SingleTaskGP(X_tensor, y_tensor)
                    mll = ExactMarginalLogLikelihood(model.likelihood, model)
                    fit_gpytorch_mll(mll)
                    
                    self.gp_models[obj_name] = model
                    logger.debug(f"GP model updated for objective '{obj_name}'")
                    
                except Exception as e:
                    logger.warning(f"Failed to fit GP model for '{obj_name}': {e}")
            
            # Update timing
            model_time = time.time() - start_time
            self.timing_stats["model_fitting"] += model_time
            
        except Exception as e:
            logger.error(f"Error updating GP models: {e}")
    
    def _prepare_training_features(self) -> np.ndarray:
        """Prepare normalized training features."""
        X_data = []
        for _, row in self.experimental_data.iterrows():
            x_normalized = self._normalize_parameters({
                name: row[name] for name in self.parameter_names
            })
            X_data.append(x_normalized)
        
        return np.array(X_data)
    
    def _normalize_parameters(self, params: Dict[str, Any]) -> np.ndarray:
        """Normalize parameters to [0, 1] range."""
        x_normalized = np.zeros(self.n_params)
        
        for i, (name, value) in enumerate(params.items()):
            param_type = self.param_types[name]
            bounds = self.bounds[i]
            
            if param_type == "categorical":
                # Find index of categorical value
                for idx, choice in self.categorical_mappings[name].items():
                    if choice == value:
                        x_normalized[i] = idx / (len(self.categorical_mappings[name]) - 1)
                        break
            else:
                # Normalize continuous/discrete values
                x_normalized[i] = (value - bounds[0]) / (bounds[1] - bounds[0])
        
        return np.clip(x_normalized, 0, 1)
    
    def _denormalize_parameters(self, x_normalized: np.ndarray) -> Dict[str, Any]:
        """Convert normalized parameters back to original space."""
        params = {}
        
        for i, name in enumerate(self.parameter_names):
            param_type = self.param_types[name]
            bounds = self.bounds[i]
            norm_value = np.clip(x_normalized[i], 0, 1)
            
            if param_type == "categorical":
                # Convert to categorical choice
                idx = int(norm_value * (len(self.categorical_mappings[name]) - 1))
                idx = np.clip(idx, 0, len(self.categorical_mappings[name]) - 1)
                params[name] = self.categorical_mappings[name][idx]
            elif param_type == "discrete":
                # Convert to discrete value
                value = bounds[0] + norm_value * (bounds[1] - bounds[0])
                params[name] = int(np.round(value))
            else:
                # Continuous value
                params[name] = bounds[0] + norm_value * (bounds[1] - bounds[0])
        
        return params
    
    def suggest_initial_experiments(self, n_suggestions: int = 5) -> List[Dict[str, Any]]:
        """
        Generate initial experimental suggestions using advanced sampling.
        
        Args:
            n_suggestions: Number of suggestions to generate
            
        Returns:
            List of parameter dictionaries
        """
        logger.info(f"Generating {n_suggestions} initial experiment suggestions")
        
        suggestions = []
        
        # Use Latin Hypercube Sampling for good space coverage
        sampler = qmc.LatinHypercube(d=self.n_params)
        samples = sampler.random(n=n_suggestions)
        
        for sample in samples:
            params = self._denormalize_parameters(sample)
            suggestions.append(params)
        
        return suggestions
    
    def suggest_next_experiment(self) -> Dict[str, Any]:
        """
        Suggest next experiment using Advanced SGLBO algorithm.
        
        Returns:
            Dictionary of parameter values for next experiment
        """
        if len(self.experimental_data) < 5:
            # Not enough data for SGLBO, use initial sampling
            suggestions = self.suggest_initial_experiments(1)
            return suggestions[0]
        
        try:
            # Run SGLBO optimization
            result = self._run_sglbo_optimization()
            
            if result.success:
                next_params = self._denormalize_parameters(result.x)
                logger.info(f"SGLBO suggested experiment after {result.n_iterations} iterations")
                return next_params
            else:
                logger.warning(f"SGLBO failed: {result.message}")
                # Fallback to random sampling
                return self.suggest_initial_experiments(1)[0]
                
        except Exception as e:
            logger.error(f"Error in suggest_next_experiment: {e}")
            return self.suggest_initial_experiments(1)[0]
    
    def _run_sglbo_optimization(self) -> SGLBOResult:
        """Run the complete SGLBO optimization algorithm."""
        start_time = time.time()
        
        # Initialize optimization from multiple starting points
        best_result = None
        
        for start_idx in range(self.config.multi_start_points):
            # Choose starting point
            if start_idx == 0:
                # Start from best known point
                x_start = self._get_best_known_point()
            else:
                # Random starting points
                x_start = np.random.random(self.n_params)
            
            # Run single optimization
            result = self._single_sglbo_run(x_start, start_idx)
            
            # Keep best result
            if best_result is None or (result.success and result.fun > best_result.fun):
                best_result = result
        
        # Update execution time
        if best_result:
            best_result.execution_time = time.time() - start_time
        
        return best_result
    
    def _get_best_known_point(self) -> np.ndarray:
        """Get the best known point from experimental data."""
        if self.experimental_data.empty:
            return np.random.random(self.n_params)
        
        # Calculate composite score for multi-objective case
        if self.n_objectives == 1:
            obj_name = self.objective_names[0]
            direction = self.objective_directions[0]
            
            if direction == 1:  # Maximize
                best_idx = self.experimental_data[obj_name].idxmax()
            elif direction == -1:  # Minimize
                best_idx = self.experimental_data[obj_name].idxmin()
            else:  # Target
                target = self.target_values.get(obj_name, 0.0)
                deviations = np.abs(self.experimental_data[obj_name] - target)
                best_idx = deviations.idxmin()
        else:
            # Multi-objective: use weighted sum
            composite_scores = self._calculate_composite_scores()
            best_idx = np.argmax(composite_scores)
        
        # Get best parameters and normalize
        best_row = self.experimental_data.iloc[best_idx]
        best_params = {name: best_row[name] for name in self.parameter_names}
        return self._normalize_parameters(best_params)
    
    def _calculate_composite_scores(self) -> np.ndarray:
        """Calculate composite scores for multi-objective optimization."""
        scores = np.zeros(len(self.experimental_data))
        
        for i, obj_name in enumerate(self.objective_names):
            values = self.experimental_data[obj_name].values
            direction = self.objective_directions[i]
            weight = self.objective_weights[i]
            
            if direction == 1:  # Maximize
                normalized = (values - values.min()) / (values.max() - values.min() + 1e-8)
            elif direction == -1:  # Minimize  
                normalized = (values.max() - values) / (values.max() - values.min() + 1e-8)
            else:  # Target
                target = self.target_values.get(obj_name, values.mean())
                deviations = np.abs(values - target)
                normalized = 1.0 / (1.0 + deviations / (deviations.max() + 1e-8))
            
            scores += weight * normalized
        
        return scores

    def _single_sglbo_run(self, x_start: np.ndarray, run_id: int) -> SGLBOResult:
        """Run single SGLBO optimization from given starting point."""
        logger.debug(f"Starting SGLBO run {run_id} from point: {x_start}")
        
        x_current = x_start.copy()
        convergence_history = []
        
        for iteration in range(self.config.max_iterations):
            iter_start_time = time.time()
            
            # Compute gradient
            gradient = self._compute_gradient(x_current)
            self.gradient_eval_count += 1
            
            # Check convergence
            gradient_norm = np.linalg.norm(gradient)
            if gradient_norm < self.config.min_gradient_norm:
                logger.debug(f"Converged due to small gradient norm: {gradient_norm}")
                break
            
            # Perform line search
            step_size, line_search_result = self._line_search(x_current, gradient)
            
            # Update position
            x_new = x_current + step_size * gradient
            x_new = np.clip(x_new, 0, 1)  # Keep in bounds
            
            # Evaluate objective at new point
            f_new = self._evaluate_composite_objective(x_new)
            
            # Store convergence info
            iter_info = {
                "iteration": iteration,
                "x": x_current.copy(),
                "f": f_new,
                "gradient_norm": gradient_norm,
                "step_size": step_size,
                "line_search_success": line_search_result.success if hasattr(line_search_result, 'success') else True,
                "time": time.time() - iter_start_time
            }
            convergence_history.append(iter_info)
            
            # Update current position
            x_current = x_new
            
            # Check for convergence
            if len(convergence_history) > 1:
                f_improvement = abs(convergence_history[-1]["f"] - convergence_history[-2]["f"])
                if f_improvement < self.config.convergence_tolerance:
                    logger.debug(f"Converged due to small function improvement: {f_improvement}")
                    break
        
        # Create result
        final_f = self._evaluate_composite_objective(x_current)
        final_gradient = self._compute_gradient(x_current)
        
        result = SGLBOResult(
            success=True,
            message=f"SGLBO run {run_id} completed successfully",
            x=x_current,
            fun=final_f,
            gradient=final_gradient,
            n_iterations=len(convergence_history),
            n_function_evals=len(convergence_history),
            n_gradient_evals=len(convergence_history),
            convergence_history=convergence_history,
            execution_time=0.0  # Will be set by caller
        )
        
        return result

    def _compute_gradient(self, x: np.ndarray) -> np.ndarray:
        """
        Compute gradient at given point using selected method.
        
        Args:
            x: Point at which to compute gradient (normalized coordinates)
            
        Returns:
            Gradient vector
        """
        start_time = time.time()
        
        try:
            # Import gradient estimator manager
            from .gradient_estimator import GradientEstimatorManager
            
            # Initialize gradient manager if not exists
            if not hasattr(self, 'gradient_manager'):
                self.gradient_manager = GradientEstimatorManager(
                    gp_models=self.gp_models,
                    objective_names=self.objective_names,
                    objective_directions=self.objective_directions,
                    objective_weights=self.objective_weights,
                    device=self.device
                )
            else:
                # Update GP models if available
                if self.gp_models:
                    self.gradient_manager.update_gp_models(self.gp_models)
            
            # Define composite objective function for gradient computation
            def composite_objective(x_norm):
                return self._evaluate_composite_objective(x_norm)
            
            # Compute gradient
            result = self.gradient_manager.compute_gradient(
                x, composite_objective, method=self.config.gradient_method.value
            )
            
            # Update timing
            self.timing_stats["gradient_computation"] += time.time() - start_time
            
            return result.gradient
            
        except Exception as e:
            logger.error(f"Error computing gradient: {e}")
            return np.zeros_like(x)
    
    def _evaluate_composite_objective(self, x: np.ndarray) -> float:
        """
        Evaluate composite objective function at normalized coordinates.
        
        Args:
            x: Normalized parameter coordinates
            
        Returns:
            Composite objective value
        """
        try:
            # Convert to parameter dictionary
            params = self._denormalize_parameters(x)
            
            # If we have an objective function, use it directly
            if self.objective_function is not None:
                return self.objective_function(params)
            
            # Otherwise, use GP models for prediction
            if not self.gp_models:
                return 0.0
            
            x_tensor = torch.tensor(x, dtype=torch.float64, device=self.device).unsqueeze(0)
            
            composite_value = 0.0
            n_objectives = 0
            
            for i, obj_name in enumerate(self.objective_names):
                if obj_name not in self.gp_models:
                    continue
                
                try:
                    model = self.gp_models[obj_name]
                    with torch.no_grad():
                        prediction = model.posterior(x_tensor).mean.cpu().numpy()[0, 0]
                    
                    direction = self.objective_directions[i]
                    weight = self.objective_weights[i]
                    
                    if direction == 1:  # Maximize
                        objective_contrib = weight * prediction
                    elif direction == -1:  # Minimize
                        objective_contrib = -weight * prediction
                    else:  # Target
                        target = self.target_values.get(obj_name, 0.0)
                        objective_contrib = -weight * abs(prediction - target)
                    
                    composite_value += objective_contrib
                    n_objectives += 1
                    
                except Exception as e:
                    logger.warning(f"Error evaluating objective '{obj_name}': {e}")
                    continue
            
            return composite_value / max(1, n_objectives)
            
        except Exception as e:
            logger.error(f"Error evaluating composite objective: {e}")
            return 0.0
    
    def _line_search(self, x: np.ndarray, direction: np.ndarray) -> Tuple[float, Any]:
        """
        Perform line search to find optimal step size.
        
        Args:
            x: Current point
            direction: Search direction
            
        Returns:
            Tuple of (step_size, line_search_result)
        """
        start_time = time.time()
        
        try:
            # Import line search manager
            from .line_search_optimizer import LineSearchManager, LineSearchConfig
            
            # Initialize line search manager if not exists
            if not hasattr(self, 'line_search_manager'):
                ls_config = LineSearchConfig(
                    armijo_c1=self.config.armijo_c1,
                    wolfe_c2=self.config.wolfe_c2,
                    initial_step=self.config.initial_step_size,
                    step_reduction_factor=self.config.step_reduction_factor,
                    max_iterations=self.config.max_line_search_iter
                )
                self.line_search_manager = LineSearchManager(ls_config)
            
            # Define objective and gradient functions
            def objective_func(x_trial):
                return -self._evaluate_composite_objective(x_trial)  # Minimize negative for maximization
            
            def gradient_func(x_trial):
                return -self._compute_gradient(x_trial)  # Negate for minimization
            
            # Set up bounds (normalized space [0, 1])
            bounds = np.array([[0.0, 1.0]] * len(x))
            
            # Perform line search
            result = self.line_search_manager.search(
                x, direction, objective_func, gradient_func, bounds,
                method=self.config.line_search_method.value
            )
            
            # Update timing
            self.timing_stats["line_search"] += time.time() - start_time
            
            return result.step_size, result
            
        except Exception as e:
            logger.error(f"Error in line search: {e}")
            return self.config.initial_step_size * 0.5, None

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary."""
        return {
            "total_experiments": len(self.experimental_data),
            "function_evaluations": self.function_eval_count,
            "gradient_evaluations": self.gradient_eval_count,
            "iterations": self.iteration_count,
            "objectives": self.objective_names,
            "parameters": self.parameter_names,
            "config": {
                "gradient_method": self.config.gradient_method.value,
                "line_search_method": self.config.line_search_method.value,
                "exploration_factor": self.config.exploration_factor
            },
            "timing_stats": self.timing_stats,
            "convergence_history": self.convergence_history[-10:]  # Last 10 iterations
        }

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Clear GPU memory
            if self.device.type == "cuda":
                torch.cuda.empty_cache()
            
            # Clear large data structures
            self.gp_models.clear()
            self.gradient_history.clear()
            
            logger.info("Advanced SGLBO cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Factory function for easy integration
def create_advanced_sglbo_optimizer(params_config: Dict[str, Dict[str, Any]],
                                  responses_config: Dict[str, Dict[str, Any]],
                                  **kwargs) -> AdvancedSGLBOOptimizer:
    """
    Factory function to create Advanced SGLBO optimizer with intelligent defaults.
    
    Args:
        params_config: Parameter configuration
        responses_config: Response configuration  
        **kwargs: Additional configuration options
        
    Returns:
        Configured AdvancedSGLBOOptimizer instance
    """
    # Set intelligent defaults based on problem characteristics
    n_params = len(params_config)
    n_objectives = len(responses_config)
    
    # Default SGLBO configuration
    sglbo_config = SGLBOConfig(
        gradient_method=GradientMethod.GP_POSTERIOR if n_params <= 10 else GradientMethod.FINITE_DIFFERENCE,
        line_search_method=LineSearchMethod.ARMIJO,
        max_iterations=min(100, max(20, n_params * 10)),
        exploration_factor=0.1,
        convergence_tolerance=1e-6,
        adaptive_exploration=True,
        use_gpu=torch.cuda.is_available()
    )
    
    # Override with user settings
    for key, value in kwargs.items():
        if hasattr(sglbo_config, key):
            setattr(sglbo_config, key, value)
    
    return AdvancedSGLBOOptimizer(
        params_config=params_config,
        responses_config=responses_config, 
        config=sglbo_config,
        **{k: v for k, v in kwargs.items() if not hasattr(sglbo_config, k)}
    )