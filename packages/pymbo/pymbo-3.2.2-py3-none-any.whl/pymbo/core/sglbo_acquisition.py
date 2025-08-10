"""
Advanced Acquisition Functions for SGLBO
========================================

This module implements sophisticated acquisition functions that incorporate
gradient information for improved exploration-exploitation balance in
Stochastic Gradient Line Bayesian Optimization. These functions extend
traditional acquisition functions with gradient-based heuristics.

Key Features:
- Gradient-Enhanced Expected Improvement (GEI)
- Multi-Point Gradient Acquisition (MGA) 
- Gradient-Weighted Upper Confidence Bound (GW-UCB)
- Exploration-Exploitation Gradient Balance (EEGB)
- Multi-objective gradient aggregation
- Parallel batch selection with gradient diversity
- Adaptive exploration based on gradient magnitude

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Advanced SGLBO Acquisition Functions
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import warnings

import numpy as np
import torch
from torch import Tensor
from scipy.stats import norm
from scipy.optimize import minimize
from sklearn.cluster import KMeans

# BoTorch imports
from botorch.acquisition import AcquisitionFunction
from botorch.models import SingleTaskGP, ModelListGP  
from botorch.utils import t_batch_mode_transform
from botorch.acquisition.analytic import ExpectedImprovement, UpperConfidenceBound
from botorch.acquisition.multi_objective import ExpectedHypervolumeImprovement

logger = logging.getLogger(__name__)


@dataclass
class AcquisitionConfig:
    """Configuration for SGLBO acquisition functions."""
    # Gradient weighting parameters
    gradient_weight: float = 0.3  # Weight for gradient contribution
    exploration_weight: float = 0.2  # Weight for exploration term
    exploitation_weight: float = 0.5  # Weight for exploitation term
    
    # UCB parameters
    beta: float = 2.0  # UCB confidence parameter
    
    # Gradient diversity parameters
    diversity_threshold: float = 0.1  # Minimum diversity for batch selection
    max_batch_diversity_iters: int = 50  # Max iterations for diversity optimization
    
    # Multi-objective parameters
    reference_point_offset: float = 0.1  # Offset for reference point calculation
    
    # Adaptive parameters
    adaptive_weights: bool = True  # Adapt weights based on gradient magnitude
    min_gradient_magnitude: float = 1e-6  # Minimum gradient for weighting
    
    # Performance parameters
    use_gpu: bool = True
    numerical_stability: float = 1e-8


class SGLBOAcquisitionFunction(AcquisitionFunction):
    """
    Base class for SGLBO acquisition functions that incorporate gradient information.
    
    Extends BoTorch's AcquisitionFunction with gradient-aware computations
    for improved exploration and exploitation balance.
    """
    
    def __init__(self, 
                 model: Union[SingleTaskGP, ModelListGP],
                 config: AcquisitionConfig = None,
                 gradient_function: Optional[Callable] = None,
                 bounds: Optional[torch.Tensor] = None):
        """
        Initialize SGLBO acquisition function.
        
        Args:
            model: GP model or ModelListGP for multi-objective
            config: Acquisition function configuration
            gradient_function: Function to compute gradients
            bounds: Parameter bounds [2 x d] tensor
        """
        super().__init__(model)
        self.config = config or AcquisitionConfig()
        self.gradient_function = gradient_function
        self.bounds = bounds
        
        # Cache for gradient evaluations
        self.gradient_cache = {}
        self.gradient_cache_hits = 0
        
        # Performance tracking
        self.eval_count = 0
        self.computation_time = 0.0
    
    def _compute_gradient_features(self, X: Tensor) -> Tensor:
        """
        Compute gradient-based features for acquisition function enhancement.
        
        Args:
            X: Input tensor [batch_size x d]
            
        Returns:
            Gradient features tensor [batch_size x feature_dim]
        """
        if self.gradient_function is None:
            return torch.zeros(X.shape[0], 1, dtype=X.dtype, device=X.device)
        
        try:
            features = []
            
            for i, x in enumerate(X):
                x_key = tuple(x.cpu().numpy().round(6))  # Cache key
                
                if x_key in self.gradient_cache:
                    gradient = self.gradient_cache[x_key]
                    self.gradient_cache_hits += 1
                else:
                    # Compute gradient
                    x_np = x.cpu().numpy()
                    gradient = self.gradient_function(x_np)
                    self.gradient_cache[x_key] = gradient
                
                # Extract features from gradient
                grad_magnitude = np.linalg.norm(gradient)
                grad_direction_entropy = self._compute_direction_entropy(gradient)
                
                feature_vector = [
                    grad_magnitude,  # Gradient magnitude
                    grad_direction_entropy,  # Direction entropy
                    np.max(np.abs(gradient)),  # Max component
                    np.std(gradient)  # Component variability
                ]
                
                features.append(feature_vector)
            
            features_tensor = torch.tensor(features, dtype=X.dtype, device=X.device)
            return features_tensor
            
        except Exception as e:
            logger.warning(f"Error computing gradient features: {e}")
            return torch.zeros(X.shape[0], 4, dtype=X.dtype, device=X.device)
    
    def _compute_direction_entropy(self, gradient: np.ndarray) -> float:
        """Compute entropy of gradient direction components."""
        try:
            abs_grad = np.abs(gradient) + self.config.numerical_stability
            normalized = abs_grad / np.sum(abs_grad)
            entropy = -np.sum(normalized * np.log(normalized + self.config.numerical_stability))
            return entropy
        except Exception:
            return 0.0
    
    def _adaptive_weight_adjustment(self, gradient_features: Tensor) -> Tensor:
        """Adaptively adjust weights based on gradient characteristics."""
        if not self.config.adaptive_weights:
            return torch.ones(gradient_features.shape[0], dtype=gradient_features.dtype, device=gradient_features.device)
        
        # Extract gradient magnitudes
        grad_magnitudes = gradient_features[:, 0]  # First feature is magnitude
        
        # Compute adaptive weights
        # High gradient magnitude -> more exploitation
        # Low gradient magnitude -> more exploration
        exploitation_weights = torch.sigmoid(grad_magnitudes - grad_magnitudes.mean())
        exploration_weights = 1.0 - exploitation_weights
        
        return torch.stack([exploration_weights, exploitation_weights], dim=1)
    
    def clear_gradient_cache(self) -> None:
        """Clear gradient cache and reset performance counters."""
        self.gradient_cache.clear()
        self.gradient_cache_hits = 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for acquisition function."""
        return {
            "evaluations": self.eval_count,
            "computation_time": self.computation_time,
            "gradient_cache_size": len(self.gradient_cache),
            "gradient_cache_hits": self.gradient_cache_hits,
            "avg_time_per_eval": self.computation_time / max(1, self.eval_count)
        }


class GradientEnhancedEI(SGLBOAcquisitionFunction):
    """
    Gradient-Enhanced Expected Improvement (GEI).
    
    Combines traditional Expected Improvement with gradient magnitude
    and direction information for improved acquisition function performance.
    """
    
    def __init__(self, model: SingleTaskGP, best_f: Optional[float] = None,
                 config: AcquisitionConfig = None, gradient_function: Optional[Callable] = None,
                 bounds: Optional[torch.Tensor] = None):
        """
        Initialize Gradient-Enhanced Expected Improvement.
        
        Args:
            model: Single-task GP model
            best_f: Current best function value
            config: Acquisition configuration
            gradient_function: Gradient computation function
            bounds: Parameter bounds
        """
        super().__init__(model, config, gradient_function, bounds)
        self.best_f = best_f
        
        # Initialize base EI
        self.base_ei = ExpectedImprovement(model, best_f)
    
    @t_batch_mode_transform(expected_q=1)
    def forward(self, X: Tensor) -> Tensor:
        """
        Evaluate Gradient-Enhanced Expected Improvement.
        
        Args:
            X: Input tensor [batch_size x d]
            
        Returns:
            Acquisition function values [batch_size]
        """
        start_time = time.time()
        
        try:
            # Compute base Expected Improvement
            ei_values = self.base_ei(X)
            
            # Compute gradient features
            gradient_features = self._compute_gradient_features(X)
            
            # Extract gradient magnitudes and normalize
            grad_magnitudes = gradient_features[:, 0]
            grad_magnitudes_norm = grad_magnitudes / (grad_magnitudes.max() + self.config.numerical_stability)
            
            # Compute gradient enhancement factor
            gradient_enhancement = self.config.gradient_weight * grad_magnitudes_norm
            
            # Compute adaptive weights
            adaptive_weights = self._adaptive_weight_adjustment(gradient_features)
            exploration_weights = adaptive_weights[:, 0]
            exploitation_weights = adaptive_weights[:, 1]
            
            # Enhanced acquisition function
            enhanced_ei = (
                exploitation_weights * ei_values +
                exploration_weights * gradient_enhancement +
                self.config.exploration_weight * torch.rand_like(ei_values)  # Random exploration
            )
            
            # Update performance tracking
            self.eval_count += X.shape[0]
            self.computation_time += time.time() - start_time
            
            return enhanced_ei
            
        except Exception as e:
            logger.error(f"Error in Gradient-Enhanced EI: {e}")
            # Fallback to base EI
            return self.base_ei(X)


class GradientWeightedUCB(SGLBOAcquisitionFunction):
    """
    Gradient-Weighted Upper Confidence Bound (GW-UCB).
    
    Modifies the traditional UCB acquisition function by weighting
    the confidence bound based on gradient information.
    """
    
    def __init__(self, model: SingleTaskGP, beta: Optional[float] = None,
                 config: AcquisitionConfig = None, gradient_function: Optional[Callable] = None,
                 bounds: Optional[torch.Tensor] = None):
        """
        Initialize Gradient-Weighted Upper Confidence Bound.
        
        Args:
            model: Single-task GP model
            beta: UCB confidence parameter
            config: Acquisition configuration  
            gradient_function: Gradient computation function
            bounds: Parameter bounds
        """
        super().__init__(model, config, gradient_function, bounds)
        self.beta = beta or config.beta if config else 2.0
        
        # Initialize base UCB
        self.base_ucb = UpperConfidenceBound(model, beta=self.beta)
    
    @t_batch_mode_transform(expected_q=1)
    def forward(self, X: Tensor) -> Tensor:
        """
        Evaluate Gradient-Weighted Upper Confidence Bound.
        
        Args:
            X: Input tensor [batch_size x d]
            
        Returns:
            Acquisition function values [batch_size]
        """
        start_time = time.time()
        
        try:
            # Get posterior predictions
            posterior = self.model.posterior(X)
            mean = posterior.mean.squeeze(-1)
            variance = posterior.variance.squeeze(-1)
            
            # Compute gradient features
            gradient_features = self._compute_gradient_features(X)
            grad_magnitudes = gradient_features[:, 0]
            
            # Normalize gradient magnitudes
            grad_magnitudes_norm = grad_magnitudes / (grad_magnitudes.max() + self.config.numerical_stability)
            
            # Adaptive beta based on gradient magnitude
            # High gradient regions get higher confidence bounds (more exploration)
            adaptive_beta = self.beta * (1.0 + self.config.gradient_weight * grad_magnitudes_norm)
            
            # Compute weighted UCB
            weighted_ucb = mean + adaptive_beta * torch.sqrt(variance)
            
            # Update performance tracking
            self.eval_count += X.shape[0]
            self.computation_time += time.time() - start_time
            
            return weighted_ucb
            
        except Exception as e:
            logger.error(f"Error in Gradient-Weighted UCB: {e}")
            # Fallback to base UCB
            return self.base_ucb(X)


class MultiObjectiveGradientAcquisition(SGLBOAcquisitionFunction):
    """
    Multi-Objective Gradient Acquisition function.
    
    Extends Expected Hypervolume Improvement with gradient information
    for multi-objective optimization problems.
    """
    
    def __init__(self, model: ModelListGP, ref_point: Tensor,
                 config: AcquisitionConfig = None, gradient_function: Optional[Callable] = None,
                 bounds: Optional[torch.Tensor] = None):
        """
        Initialize Multi-Objective Gradient Acquisition.
        
        Args:
            model: ModelListGP for multi-objective
            ref_point: Reference point for hypervolume computation
            config: Acquisition configuration
            gradient_function: Gradient computation function
            bounds: Parameter bounds
        """
        super().__init__(model, config, gradient_function, bounds)
        self.ref_point = ref_point
        
        # Initialize base EHVI
        from botorch.utils.multi_objective.box_decompositions.non_dominated import (
            FastNondominatedPartitioning
        )
        
        # Create dummy partitioning for initialization
        dummy_Y = torch.randn(5, len(ref_point), dtype=ref_point.dtype, device=ref_point.device)
        partitioning = FastNondominatedPartitioning(ref_point=ref_point, Y=dummy_Y)
        
        self.base_ehvi = ExpectedHypervolumeImprovement(
            model=model,
            ref_point=ref_point,
            partitioning=partitioning
        )
    
    @t_batch_mode_transform(expected_q=1)
    def forward(self, X: Tensor) -> Tensor:
        """
        Evaluate Multi-Objective Gradient Acquisition.
        
        Args:
            X: Input tensor [batch_size x d]
            
        Returns:
            Acquisition function values [batch_size]
        """
        start_time = time.time()
        
        try:
            # Compute base EHVI
            ehvi_values = self.base_ehvi(X)
            
            # Compute gradient features
            gradient_features = self._compute_gradient_features(X)
            grad_magnitudes = gradient_features[:, 0]
            grad_entropies = gradient_features[:, 1]
            
            # Normalize features
            grad_magnitudes_norm = grad_magnitudes / (grad_magnitudes.max() + self.config.numerical_stability)
            grad_entropies_norm = grad_entropies / (grad_entropies.max() + self.config.numerical_stability)
            
            # Multi-objective gradient enhancement
            # High gradient magnitude indicates potential for improvement
            # High entropy indicates balanced improvement across objectives
            mo_enhancement = (
                self.config.gradient_weight * grad_magnitudes_norm +
                self.config.exploration_weight * grad_entropies_norm
            )
            
            # Enhanced multi-objective acquisition
            enhanced_ehvi = ehvi_values + mo_enhancement
            
            # Update performance tracking
            self.eval_count += X.shape[0]
            self.computation_time += time.time() - start_time
            
            return enhanced_ehvi
            
        except Exception as e:
            logger.error(f"Error in Multi-Objective Gradient Acquisition: {e}")
            # Fallback to base EHVI
            try:
                return self.base_ehvi(X)
            except:
                return torch.zeros(X.shape[0], dtype=X.dtype, device=X.device)


class BatchGradientDiversityAcquisition:
    """
    Batch acquisition function that ensures gradient diversity.
    
    Selects batches of points that are not only high-acquisition
    but also diverse in gradient space for parallel evaluation.
    """
    
    def __init__(self, base_acquisition: SGLBOAcquisitionFunction,
                 config: AcquisitionConfig = None):
        """
        Initialize batch gradient diversity acquisition.
        
        Args:
            base_acquisition: Base acquisition function
            config: Acquisition configuration
        """
        self.base_acquisition = base_acquisition
        self.config = config or AcquisitionConfig()
    
    def select_batch(self, candidate_set: Tensor, batch_size: int) -> Tuple[Tensor, Tensor]:
        """
        Select diverse batch of candidates based on acquisition and gradient diversity.
        
        Args:
            candidate_set: Candidate points [n_candidates x d]
            batch_size: Number of points to select
            
        Returns:
            Tuple of (selected_points, acquisition_values)
        """
        try:
            if batch_size >= candidate_set.shape[0]:
                # Return all candidates if batch size is larger
                acq_values = self.base_acquisition(candidate_set)
                return candidate_set, acq_values
            
            # Compute acquisition values for all candidates
            acq_values = self.base_acquisition(candidate_set)
            
            # Compute gradient features for diversity
            gradient_features = self.base_acquisition._compute_gradient_features(candidate_set)
            
            # Select first point with highest acquisition
            selected_indices = [torch.argmax(acq_values).item()]
            selected_points = [candidate_set[selected_indices[0]]]
            
            # Greedily select remaining points to maximize diversity
            for _ in range(batch_size - 1):
                best_idx = None
                best_score = float('-inf')
                
                for i, candidate in enumerate(candidate_set):
                    if i in selected_indices:
                        continue
                    
                    # Compute diversity score
                    diversity_score = self._compute_diversity_score(
                        gradient_features[i], 
                        gradient_features[selected_indices]
                    )
                    
                    # Combined score: acquisition + diversity
                    combined_score = (
                        self.config.exploitation_weight * acq_values[i] +
                        self.config.exploration_weight * diversity_score
                    )
                    
                    if combined_score > best_score:
                        best_score = combined_score
                        best_idx = i
                
                if best_idx is not None:
                    selected_indices.append(best_idx)
                    selected_points.append(candidate_set[best_idx])
                else:
                    # Fallback: random selection
                    remaining = [i for i in range(len(candidate_set)) if i not in selected_indices]
                    if remaining:
                        idx = np.random.choice(remaining)
                        selected_indices.append(idx)
                        selected_points.append(candidate_set[idx])
            
            selected_tensor = torch.stack(selected_points)
            selected_acq_values = acq_values[selected_indices]
            
            return selected_tensor, selected_acq_values
            
        except Exception as e:
            logger.error(f"Error in batch selection: {e}")
            # Fallback: top acquisition values
            _, top_indices = torch.topk(acq_values, batch_size)
            return candidate_set[top_indices], acq_values[top_indices]
    
    def _compute_diversity_score(self, candidate_features: Tensor, selected_features: Tensor) -> float:
        """Compute diversity score for candidate relative to selected points."""
        try:
            # Compute minimum distance to selected points in gradient feature space
            distances = torch.norm(selected_features - candidate_features.unsqueeze(0), dim=1)
            min_distance = torch.min(distances)
            
            # Normalize and return as diversity score
            diversity_score = torch.clamp(min_distance / (distances.mean() + 1e-8), 0, 1)
            return diversity_score.item()
            
        except Exception:
            return 0.5  # Neutral diversity score on error


class AcquisitionFunctionManager:
    """
    Manager for SGLBO acquisition functions with automatic selection and optimization.
    
    Coordinates different acquisition functions and provides unified interface
    for optimization and batch selection.
    """
    
    def __init__(self, config: AcquisitionConfig = None):
        """
        Initialize acquisition function manager.
        
        Args:
            config: Acquisition function configuration
        """
        self.config = config or AcquisitionConfig()
        self.acquisition_functions = {}
        self.performance_history = {}
    
    def create_acquisition_function(self, 
                                  model: Union[SingleTaskGP, ModelListGP],
                                  acquisition_type: str = "gei",
                                  gradient_function: Optional[Callable] = None,
                                  bounds: Optional[torch.Tensor] = None,
                                  **kwargs) -> SGLBOAcquisitionFunction:
        """
        Create acquisition function of specified type.
        
        Args:
            model: GP model
            acquisition_type: Type of acquisition function
            gradient_function: Gradient computation function
            bounds: Parameter bounds
            **kwargs: Additional arguments
            
        Returns:
            Configured acquisition function
        """
        try:
            if acquisition_type.lower() == "gei":
                best_f = kwargs.get("best_f", None)
                return GradientEnhancedEI(model, best_f, self.config, gradient_function, bounds)
            
            elif acquisition_type.lower() == "gw_ucb":
                beta = kwargs.get("beta", self.config.beta)
                return GradientWeightedUCB(model, beta, self.config, gradient_function, bounds)
            
            elif acquisition_type.lower() == "mo_gradient":
                ref_point = kwargs.get("ref_point")
                if ref_point is None:
                    raise ValueError("Reference point required for multi-objective acquisition")
                return MultiObjectiveGradientAcquisition(model, ref_point, self.config, gradient_function, bounds)
            
            else:
                raise ValueError(f"Unknown acquisition type: {acquisition_type}")
                
        except Exception as e:
            logger.error(f"Error creating acquisition function: {e}")
            # Fallback to GEI
            return GradientEnhancedEI(model, None, self.config, gradient_function, bounds)
    
    def optimize_acquisition(self, acquisition_func: SGLBOAcquisitionFunction,
                           bounds: torch.Tensor, n_candidates: int = 1000,
                           n_restarts: int = 10) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Optimize acquisition function to find best candidates.
        
        Args:
            acquisition_func: Acquisition function to optimize
            bounds: Parameter bounds [2 x d]
            n_candidates: Number of candidate points to generate
            n_restarts: Number of optimization restarts
            
        Returns:
            Tuple of (best_candidates, acquisition_values)
        """
        try:
            device = bounds.device
            dtype = bounds.dtype
            d = bounds.shape[-1]
            
            # Generate candidate points using Latin Hypercube Sampling
            from scipy.stats import qmc
            sampler = qmc.LatinHypercube(d=d)
            candidates_unit = sampler.random(n=n_candidates)
            
            # Transform to parameter space
            candidates = torch.tensor(candidates_unit, dtype=dtype, device=device)
            candidates = bounds[0] + candidates * (bounds[1] - bounds[0])
            
            # Evaluate acquisition function
            with torch.no_grad():
                acq_values = acquisition_func(candidates)
            
            # Select top candidates
            _, top_indices = torch.topk(acq_values, min(n_restarts, len(acq_values)))
            best_candidates = candidates[top_indices]
            best_values = acq_values[top_indices]
            
            return best_candidates, best_values
            
        except Exception as e:
            logger.error(f"Error optimizing acquisition function: {e}")
            # Return random candidates as fallback
            random_candidates = torch.rand(n_restarts, bounds.shape[-1], dtype=bounds.dtype, device=bounds.device)
            random_candidates = bounds[0] + random_candidates * (bounds[1] - bounds[0])
            random_values = torch.zeros(n_restarts, dtype=bounds.dtype, device=bounds.device)
            return random_candidates, random_values
    
    def select_batch_diverse(self, acquisition_func: SGLBOAcquisitionFunction,
                           bounds: torch.Tensor, batch_size: int,
                           n_candidates: int = 1000) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Select diverse batch using gradient diversity acquisition.
        
        Args:
            acquisition_func: Base acquisition function
            bounds: Parameter bounds
            batch_size: Size of batch to select
            n_candidates: Number of candidate points
            
        Returns:
            Tuple of (selected_batch, acquisition_values)
        """
        try:
            # Generate candidate set
            device = bounds.device
            dtype = bounds.dtype  
            d = bounds.shape[-1]
            
            from scipy.stats import qmc
            sampler = qmc.LatinHypercube(d=d)
            candidates_unit = sampler.random(n=n_candidates)
            
            candidates = torch.tensor(candidates_unit, dtype=dtype, device=device)
            candidates = bounds[0] + candidates * (bounds[1] - bounds[0])
            
            # Use batch diversity selection
            batch_selector = BatchGradientDiversityAcquisition(acquisition_func, self.config)
            selected_batch, acq_values = batch_selector.select_batch(candidates, batch_size)
            
            return selected_batch, acq_values
            
        except Exception as e:
            logger.error(f"Error in batch selection: {e}")
            # Fallback to random batch
            random_batch = torch.rand(batch_size, bounds.shape[-1], dtype=bounds.dtype, device=bounds.device)
            random_batch = bounds[0] + random_batch * (bounds[1] - bounds[0])
            random_values = torch.zeros(batch_size, dtype=bounds.dtype, device=bounds.device)
            return random_batch, random_values