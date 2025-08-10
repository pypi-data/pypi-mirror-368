"""
SGLBO Controller Integration for PyMBO
======================================

This module integrates the Advanced SGLBO optimizer with the existing PyMBO 
controller architecture. It provides seamless switching between SGLBO screening
and full Bayesian optimization, with hybrid workflows and performance monitoring.

Key Features:
- Hybrid SGLBO/BO workflow management  
- Seamless integration with existing SimpleController
- Automatic mode switching based on convergence criteria
- Performance monitoring and adaptive parameter tuning
- Data flow management between screening and detailed phases
- GUI integration support
- Multi-objective optimization coordination

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - SGLBO Controller Integration
"""

import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

# PyMBO imports
from .advanced_sglbo_optimizer import AdvancedSGLBOOptimizer, SGLBOConfig, GradientMethod, LineSearchMethod
from .controller import SimpleController

logger = logging.getLogger(__name__)


class OptimizationPhase(Enum):
    """Optimization phases in hybrid SGLBO/BO workflow."""
    INITIALIZATION = "initialization"
    SGLBO_SCREENING = "sglbo_screening"  
    TRANSITION = "transition"
    DETAILED_BO = "detailed_bo"
    COMPLETED = "completed"


@dataclass
class SGLBOControllerConfig:
    """Configuration for SGLBO Controller."""
    # Screening parameters
    screening_iterations: int = 50
    screening_convergence_tolerance: float = 1e-6
    min_screening_samples: int = 10
    max_screening_samples: int = 200
    
    # Transition criteria
    gradient_convergence_threshold: float = 1e-8
    function_improvement_threshold: float = 1e-6
    screening_success_rate_threshold: float = 0.8
    
    # Hybrid workflow parameters
    enable_automatic_transition: bool = True
    force_detailed_bo_after_screening: bool = True
    preserve_screening_data: bool = True
    
    # Performance parameters
    enable_performance_monitoring: bool = True
    adaptive_parameter_tuning: bool = True
    parallel_evaluation_threshold: int = 5
    
    # Integration parameters
    use_existing_controller: bool = True
    fallback_to_standard_bo: bool = True


class HybridSGLBOController:
    """
    Hybrid controller that manages SGLBO screening and detailed BO phases.
    
    This controller orchestrates the complete optimization workflow, starting
    with efficient SGLBO screening to explore the parameter space, then
    transitioning to detailed Bayesian optimization for fine-tuning.
    """
    
    def __init__(self,
                 params_config: Dict[str, Dict[str, Any]],
                 responses_config: Dict[str, Dict[str, Any]],
                 sglbo_config: Optional[SGLBOConfig] = None,
                 controller_config: Optional[SGLBOControllerConfig] = None,
                 objective_function: Optional[Callable] = None,
                 existing_controller: Optional[SimpleController] = None):
        """
        Initialize Hybrid SGLBO Controller.
        
        Args:
            params_config: Parameter configuration dictionary
            responses_config: Response configuration dictionary
            sglbo_config: SGLBO optimizer configuration
            controller_config: Controller-specific configuration
            objective_function: Optional objective function for direct evaluation
            existing_controller: Existing PyMBO controller to integrate with
        """
        self.params_config = params_config
        self.responses_config = responses_config
        self.sglbo_config = sglbo_config or SGLBOConfig()
        self.controller_config = controller_config or SGLBOControllerConfig()
        self.objective_function = objective_function
        
        # Initialize optimizers
        self.sglbo_optimizer = None
        self.standard_controller = existing_controller
        
        # Workflow state
        self.current_phase = OptimizationPhase.INITIALIZATION
        self.phase_history = []
        self.transition_log = []
        
        # Data management
        self.screening_data = pd.DataFrame()
        self.detailed_data = pd.DataFrame()
        self.combined_data = pd.DataFrame()
        
        # Performance tracking
        self.phase_performance = {}
        self.optimization_metrics = {
            "screening_time": 0.0,
            "detailed_time": 0.0,
            "total_time": 0.0,
            "screening_evaluations": 0,
            "detailed_evaluations": 0,
            "total_evaluations": 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        logger.info("Hybrid SGLBO Controller initialized")
        logger.info(f"  Parameters: {len(self.params_config)}")
        logger.info(f"  Objectives: {len(self.responses_config)}")
        logger.info(f"  SGLBO Method: {self.sglbo_config.gradient_method.value}")
        
    def initialize_optimization(self) -> Dict[str, Any]:
        """
        Initialize the optimization process and set up both optimizers.
        
        Returns:
            Initialization status and configuration
        """
        with self.lock:
            try:
                start_time = time.time()
                
                # Initialize SGLBO optimizer
                self.sglbo_optimizer = AdvancedSGLBOOptimizer(
                    params_config=self.params_config,
                    responses_config=self.responses_config,
                    config=self.sglbo_config,
                    objective_function=self.objective_function
                )
                
                # Initialize or connect to standard controller
                if self.standard_controller is None and self.controller_config.use_existing_controller:
                    try:
                        self.standard_controller = SimpleController()
                        self.standard_controller.configure_optimization(
                            self.params_config, 
                            self.responses_config
                        )
                    except Exception as e:
                        logger.warning(f"Failed to initialize standard controller: {e}")
                        if self.controller_config.fallback_to_standard_bo:
                            self.standard_controller = None
                
                # Set initial phase
                self.current_phase = OptimizationPhase.SGLBO_SCREENING
                self._log_phase_transition("initialization", OptimizationPhase.SGLBO_SCREENING)
                
                initialization_time = time.time() - start_time
                
                result = {
                    "success": True,
                    "phase": self.current_phase.value,
                    "message": "Hybrid SGLBO Controller initialized successfully",
                    "sglbo_available": self.sglbo_optimizer is not None,
                    "standard_bo_available": self.standard_controller is not None,
                    "initialization_time": initialization_time,
                    "config": {
                        "gradient_method": self.sglbo_config.gradient_method.value,
                        "line_search_method": self.sglbo_config.line_search_method.value,
                        "screening_iterations": self.controller_config.screening_iterations
                    }
                }
                
                logger.info("Optimization initialized - Starting SGLBO screening phase")
                return result
                
            except Exception as e:
                logger.error(f"Error initializing optimization: {e}")
                return {
                    "success": False,
                    "message": f"Initialization failed: {e}",
                    "phase": "error"
                }
    
    def add_experimental_data(self, data_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Add experimental data to the appropriate optimizer based on current phase.
        
        Args:
            data_df: New experimental data
            
        Returns:
            Data processing result and phase status
        """
        with self.lock:
            try:
                start_time = time.time()
                
                logger.info(f"Adding {len(data_df)} data points in {self.current_phase.value} phase")
                
                # Add to combined data
                if self.combined_data.empty:
                    self.combined_data = data_df.copy()
                else:
                    self.combined_data = pd.concat([self.combined_data, data_df], ignore_index=True)
                
                # Route to appropriate optimizer
                if self.current_phase == OptimizationPhase.SGLBO_SCREENING:
                    return self._process_screening_data(data_df)
                elif self.current_phase == OptimizationPhase.DETAILED_BO:
                    return self._process_detailed_data(data_df)
                else:
                    return {"success": False, "message": f"Cannot add data in phase: {self.current_phase.value}"}
                    
            except Exception as e:
                logger.error(f"Error adding experimental data: {e}")
                return {"success": False, "message": f"Data processing failed: {e}"}
    
    def _process_screening_data(self, data_df: pd.DataFrame) -> Dict[str, Any]:
        """Process data in SGLBO screening phase."""
        try:
            # Add to SGLBO optimizer
            self.sglbo_optimizer.add_experimental_data(data_df)
            
            # Store screening data
            if self.screening_data.empty:
                self.screening_data = data_df.copy()
            else:
                self.screening_data = pd.concat([self.screening_data, data_df], ignore_index=True)
            
            # Update metrics
            self.optimization_metrics["screening_evaluations"] += len(data_df)
            
            # Check convergence and transition criteria
            transition_check = self._check_transition_criteria()
            
            result = {
                "success": True,
                "phase": self.current_phase.value,
                "total_screening_samples": len(self.screening_data),
                "message": f"Added {len(data_df)} samples to SGLBO screening",
                "transition_ready": transition_check["ready"],
                "convergence_metrics": transition_check["metrics"]
            }
            
            # Auto-transition if enabled and criteria met
            if (transition_check["ready"] and 
                self.controller_config.enable_automatic_transition):
                transition_result = self._transition_to_detailed_bo()
                result["transition_result"] = transition_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing screening data: {e}")
            return {"success": False, "message": f"Screening data processing failed: {e}"}
    
    def _process_detailed_data(self, data_df: pd.DataFrame) -> Dict[str, Any]:
        """Process data in detailed BO phase."""
        try:
            # Add to detailed data storage
            if self.detailed_data.empty:
                self.detailed_data = data_df.copy()
            else:
                self.detailed_data = pd.concat([self.detailed_data, data_df], ignore_index=True)
            
            # Add to standard controller if available
            if self.standard_controller is not None:
                self.standard_controller.add_experimental_data(data_df)
            
            # Update metrics
            self.optimization_metrics["detailed_evaluations"] += len(data_df)
            
            return {
                "success": True,
                "phase": self.current_phase.value,
                "total_detailed_samples": len(self.detailed_data),
                "message": f"Added {len(data_df)} samples to detailed BO"
            }
            
        except Exception as e:
            logger.error(f"Error processing detailed data: {e}")
            return {"success": False, "message": f"Detailed data processing failed: {e}"}
    
    def suggest_next_experiment(self, n_suggestions: int = 1) -> List[Dict[str, Any]]:
        """
        Suggest next experiment based on current optimization phase.
        
        Args:
            n_suggestions: Number of suggestions to generate
            
        Returns:
            List of parameter dictionaries for suggested experiments
        """
        with self.lock:
            try:
                if self.current_phase == OptimizationPhase.INITIALIZATION:
                    # Generate initial suggestions
                    return self._generate_initial_suggestions(n_suggestions)
                
                elif self.current_phase == OptimizationPhase.SGLBO_SCREENING:
                    # Use SGLBO optimizer
                    if self.sglbo_optimizer is None:
                        raise ValueError("SGLBO optimizer not initialized")
                    
                    suggestions = []
                    for _ in range(n_suggestions):
                        suggestion = self.sglbo_optimizer.suggest_next_experiment()
                        suggestions.append(suggestion)
                    
                    logger.info(f"SGLBO suggested {len(suggestions)} experiments")
                    return suggestions
                
                elif self.current_phase == OptimizationPhase.DETAILED_BO:
                    # Use standard controller
                    if self.standard_controller is None:
                        raise ValueError("Standard controller not available")
                    
                    suggestions = self.standard_controller.suggest_next_experiments(n_suggestions)
                    logger.info(f"Detailed BO suggested {len(suggestions)} experiments")
                    return suggestions
                
                else:
                    raise ValueError(f"Cannot suggest experiments in phase: {self.current_phase.value}")
                    
            except Exception as e:
                logger.error(f"Error suggesting next experiment: {e}")
                # Fallback to random suggestions
                return self._generate_initial_suggestions(n_suggestions)
    
    def _generate_initial_suggestions(self, n_suggestions: int) -> List[Dict[str, Any]]:
        """Generate initial experimental suggestions."""
        try:
            if self.sglbo_optimizer is not None:
                return self.sglbo_optimizer.suggest_initial_experiments(n_suggestions)
            else:
                # Simple random sampling fallback
                suggestions = []
                for _ in range(n_suggestions):
                    suggestion = {}
                    for param_name, config in self.params_config.items():
                        param_type = config.get("type", "continuous")
                        if param_type == "continuous":
                            low = config.get("low", 0.0)
                            high = config.get("high", 1.0)
                            suggestion[param_name] = np.random.uniform(low, high)
                        elif param_type == "categorical":
                            choices = config.get("choices", ["A", "B"])
                            suggestion[param_name] = np.random.choice(choices)
                        else:
                            suggestion[param_name] = 0.5
                    suggestions.append(suggestion)
                return suggestions
        except Exception as e:
            logger.error(f"Error generating initial suggestions: {e}")
            return [{}] * n_suggestions
    
    def _check_transition_criteria(self) -> Dict[str, Any]:
        """Check if ready to transition from screening to detailed BO."""
        try:
            if self.sglbo_optimizer is None or len(self.screening_data) < self.controller_config.min_screening_samples:
                return {"ready": False, "reason": "insufficient_data", "metrics": {}}
            
            # Get SGLBO optimization summary
            summary = self.sglbo_optimizer.get_optimization_summary()
            
            metrics = {
                "total_evaluations": summary["total_experiments"],
                "gradient_evaluations": summary["gradient_evaluations"],
                "convergence_history": summary.get("convergence_history", [])
            }
            
            # Check various transition criteria
            ready_reasons = []
            
            # Maximum screening samples reached
            if len(self.screening_data) >= self.controller_config.max_screening_samples:
                ready_reasons.append("max_samples_reached")
            
            # Screening iterations completed
            if len(metrics["convergence_history"]) >= self.controller_config.screening_iterations:
                ready_reasons.append("max_iterations_reached")
            
            # Gradient convergence
            if len(metrics["convergence_history"]) >= 3:
                recent_gradients = [iter_data.get("gradient_norm", 0) 
                                 for iter_data in metrics["convergence_history"][-3:]]
                if all(g < self.controller_config.gradient_convergence_threshold for g in recent_gradients):
                    ready_reasons.append("gradient_converged")
            
            # Function improvement stagnation
            if len(metrics["convergence_history"]) >= 5:
                recent_values = [iter_data.get("f", 0) 
                               for iter_data in metrics["convergence_history"][-5:]]
                if len(set(recent_values)) == 1:  # All values identical
                    ready_reasons.append("function_stagnated")
                else:
                    improvements = [abs(recent_values[i] - recent_values[i-1]) 
                                  for i in range(1, len(recent_values))]
                    avg_improvement = np.mean(improvements)
                    if avg_improvement < self.controller_config.function_improvement_threshold:
                        ready_reasons.append("small_improvements")
            
            is_ready = len(ready_reasons) > 0
            
            return {
                "ready": is_ready,
                "reasons": ready_reasons,
                "metrics": metrics,
                "screening_samples": len(self.screening_data)
            }
            
        except Exception as e:
            logger.error(f"Error checking transition criteria: {e}")
            return {"ready": False, "reason": "error", "metrics": {}}
    
    def _transition_to_detailed_bo(self) -> Dict[str, Any]:
        """Transition from SGLBO screening to detailed BO."""
        try:
            logger.info("Transitioning from SGLBO screening to detailed BO")
            
            start_time = time.time()
            
            # Log phase transition
            self._log_phase_transition(OptimizationPhase.SGLBO_SCREENING, OptimizationPhase.DETAILED_BO)
            self.current_phase = OptimizationPhase.DETAILED_BO
            
            # Initialize standard controller if needed
            if self.standard_controller is None:
                if self.controller_config.use_existing_controller:
                    self.standard_controller = SimpleController()
                    self.standard_controller.configure_optimization(
                        self.params_config,
                        self.responses_config
                    )
                else:
                    return {
                        "success": False,
                        "message": "Standard controller not available for detailed BO"
                    }
            
            # Transfer screening data to detailed BO if configured
            if (self.controller_config.preserve_screening_data and 
                not self.screening_data.empty and 
                self.standard_controller is not None):
                
                self.standard_controller.add_experimental_data(self.screening_data)
                logger.info(f"Transferred {len(self.screening_data)} screening samples to detailed BO")
            
            transition_time = time.time() - start_time
            
            result = {
                "success": True,
                "message": "Successfully transitioned to detailed BO",
                "screening_samples_transferred": len(self.screening_data) if self.controller_config.preserve_screening_data else 0,
                "transition_time": transition_time,
                "new_phase": self.current_phase.value
            }
            
            logger.info("Transition to detailed BO completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error transitioning to detailed BO: {e}")
            return {
                "success": False,
                "message": f"Transition failed: {e}"
            }
    
    def _log_phase_transition(self, from_phase: Union[OptimizationPhase, str], to_phase: OptimizationPhase) -> None:
        """Log phase transition for tracking."""
        transition = {
            "timestamp": datetime.now().isoformat(),
            "from_phase": from_phase.value if isinstance(from_phase, OptimizationPhase) else from_phase,
            "to_phase": to_phase.value,
            "total_samples": len(self.combined_data),
            "screening_samples": len(self.screening_data),
            "detailed_samples": len(self.detailed_data)
        }
        
        self.transition_log.append(transition)
        self.phase_history.append(to_phase)
        
        logger.info(f"Phase transition: {transition['from_phase']} -> {transition['to_phase']}")
    
    def force_transition_to_detailed_bo(self) -> Dict[str, Any]:
        """Force transition to detailed BO regardless of criteria."""
        with self.lock:
            if self.current_phase == OptimizationPhase.SGLBO_SCREENING:
                return self._transition_to_detailed_bo()
            else:
                return {
                    "success": False,
                    "message": f"Cannot force transition from phase: {self.current_phase.value}"
                }
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get comprehensive optimization summary across all phases."""
        with self.lock:
            try:
                # Update total metrics
                self.optimization_metrics["total_evaluations"] = (
                    self.optimization_metrics["screening_evaluations"] + 
                    self.optimization_metrics["detailed_evaluations"]
                )
                
                # Get phase-specific summaries
                sglbo_summary = {}
                if self.sglbo_optimizer is not None:
                    sglbo_summary = self.sglbo_optimizer.get_optimization_summary()
                
                standard_summary = {}
                if self.standard_controller is not None:
                    try:
                        standard_summary = self.standard_controller.get_optimization_summary()
                    except Exception as e:
                        logger.warning(f"Error getting standard controller summary: {e}")
                
                return {
                    "current_phase": self.current_phase.value,
                    "phase_history": [phase.value for phase in self.phase_history],
                    "transition_log": self.transition_log,
                    "data_summary": {
                        "total_samples": len(self.combined_data),
                        "screening_samples": len(self.screening_data),
                        "detailed_samples": len(self.detailed_data)
                    },
                    "metrics": self.optimization_metrics,
                    "sglbo_summary": sglbo_summary,
                    "standard_bo_summary": standard_summary,
                    "configuration": {
                        "sglbo_config": {
                            "gradient_method": self.sglbo_config.gradient_method.value,
                            "line_search_method": self.sglbo_config.line_search_method.value,
                            "exploration_factor": self.sglbo_config.exploration_factor
                        },
                        "controller_config": {
                            "screening_iterations": self.controller_config.screening_iterations,
                            "enable_automatic_transition": self.controller_config.enable_automatic_transition,
                            "preserve_screening_data": self.controller_config.preserve_screening_data
                        }
                    }
                }
                
            except Exception as e:
                logger.error(f"Error generating optimization summary: {e}")
                return {
                    "current_phase": self.current_phase.value,
                    "error": str(e)
                }
    
    def cleanup(self) -> None:
        """Clean up resources and save optimization state."""
        with self.lock:
            try:
                logger.info("Cleaning up Hybrid SGLBO Controller")
                
                # Cleanup optimizers
                if self.sglbo_optimizer is not None:
                    self.sglbo_optimizer.cleanup()
                
                if self.standard_controller is not None:
                    try:
                        self.standard_controller.cleanup()
                    except Exception as e:
                        logger.warning(f"Error cleaning up standard controller: {e}")
                
                # Log final summary
                final_summary = self.get_optimization_summary()
                logger.info("=== Hybrid SGLBO Optimization Complete ===")
                logger.info(f"Total samples: {final_summary['data_summary']['total_samples']}")
                logger.info(f"Screening samples: {final_summary['data_summary']['screening_samples']}")
                logger.info(f"Detailed BO samples: {final_summary['data_summary']['detailed_samples']}")
                logger.info(f"Final phase: {final_summary['current_phase']}")
                
                self.current_phase = OptimizationPhase.COMPLETED
                
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")