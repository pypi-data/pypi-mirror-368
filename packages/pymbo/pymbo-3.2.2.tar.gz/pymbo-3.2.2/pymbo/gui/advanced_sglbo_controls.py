"""
Advanced SGLBO GUI Controls for PyMBO
=====================================

This module provides sophisticated GUI controls for the Advanced SGLBO optimizer,
including real-time gradient visualization, convergence monitoring, parameter
tuning, and interactive exploration controls. Integrates seamlessly with the
existing PyMBO GUI framework.

Key Features:
- Real-time gradient vector field visualization
- Interactive parameter space exploration
- Multi-phase optimization monitoring
- Convergence analysis with gradient-based metrics
- Adaptive parameter tuning controls
- Performance monitoring dashboard
- Batch selection and diversity controls

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Advanced SGLBO GUI Controls
"""

import sys
import logging
from typing import Any, Dict, List, Optional, Tuple, Callable
import traceback

try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except ImportError:
    try:
        from PySide2.QtWidgets import *
        from PySide2.QtCore import *
        from PySide2.QtGui import *
    except ImportError:
        # Fallback for systems without Qt
        logger = logging.getLogger(__name__)
        logger.warning("Qt not available - GUI controls will not function")
        
        # Define dummy base classes
        class QWidget:
            pass
        class QVBoxLayout:
            pass
        class QHBoxLayout:
            pass
        class QGridLayout:
            pass
        class QLabel:
            pass
        class QComboBox:
            pass
        class QSpinBox:
            pass
        class QDoubleSpinBox:
            pass
        class QCheckBox:
            pass
        class QPushButton:
            pass
        class QGroupBox:
            pass
        class QTabWidget:
            pass
        class QTextEdit:
            pass
        class QProgressBar:
            pass
        class QSlider:
            pass
        class pyqtSignal:
            def __init__(self, *args):
                pass
        class Qt:
            Horizontal = 1
            Vertical = 2

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import seaborn as sns

# PyMBO imports
try:
    from ..core.advanced_sglbo_optimizer import AdvancedSGLBOOptimizer, SGLBOConfig, GradientMethod, LineSearchMethod
    from ..core.sglbo_controller import HybridSGLBOController, OptimizationPhase, SGLBOControllerConfig
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("SGLBO modules not available - using dummy implementations")

logger = logging.getLogger(__name__)


class SGLBOConfigWidget(QWidget):
    """Widget for configuring SGLBO optimization parameters."""
    
    config_changed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = SGLBOConfig()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the configuration UI."""
        layout = QVBoxLayout(self)
        
        # Gradient Method Configuration
        gradient_group = QGroupBox("Gradient Estimation")
        gradient_layout = QGridLayout(gradient_group)
        
        gradient_layout.addWidget(QLabel("Method:"), 0, 0)
        self.gradient_method_combo = QComboBox()
        self.gradient_method_combo.addItems([method.value for method in GradientMethod])
        self.gradient_method_combo.setCurrentText(self.current_config.gradient_method.value)
        self.gradient_method_combo.currentTextChanged.connect(self._on_config_changed)
        gradient_layout.addWidget(self.gradient_method_combo, 0, 1)
        
        gradient_layout.addWidget(QLabel("Finite Diff Step:"), 1, 0)
        self.finite_diff_spin = QDoubleSpinBox()
        self.finite_diff_spin.setRange(1e-10, 1e-3)
        self.finite_diff_spin.setDecimals(10)
        self.finite_diff_spin.setValue(self.current_config.finite_diff_step)
        self.finite_diff_spin.setSingleStep(1e-7)
        self.finite_diff_spin.setToolTip("Step size for finite difference gradient estimation")
        self.finite_diff_spin.valueChanged.connect(self._on_config_changed)
        gradient_layout.addWidget(self.finite_diff_spin, 1, 1)
        
        layout.addWidget(gradient_group)
        
        # Line Search Configuration
        line_search_group = QGroupBox("Line Search")
        line_search_layout = QGridLayout(line_search_group)
        
        line_search_layout.addWidget(QLabel("Method:"), 0, 0)
        self.line_search_combo = QComboBox()
        self.line_search_combo.addItems([method.value for method in LineSearchMethod])
        self.line_search_combo.setCurrentText(self.current_config.line_search_method.value)
        self.line_search_combo.currentTextChanged.connect(self._on_config_changed)
        line_search_layout.addWidget(self.line_search_combo, 0, 1)
        
        line_search_layout.addWidget(QLabel("Armijo C1:"), 1, 0)
        self.armijo_c1_spin = QDoubleSpinBox()
        self.armijo_c1_spin.setRange(1e-6, 0.1)
        self.armijo_c1_spin.setDecimals(6)
        self.armijo_c1_spin.setValue(self.current_config.armijo_c1)
        self.armijo_c1_spin.setSingleStep(1e-5)
        self.armijo_c1_spin.setToolTip("Armijo sufficient decrease parameter")
        self.armijo_c1_spin.valueChanged.connect(self._on_config_changed)
        line_search_layout.addWidget(self.armijo_c1_spin, 1, 1)
        
        line_search_layout.addWidget(QLabel("Wolfe C2:"), 2, 0)
        self.wolfe_c2_spin = QDoubleSpinBox()
        self.wolfe_c2_spin.setRange(0.1, 0.99)
        self.wolfe_c2_spin.setDecimals(3)
        self.wolfe_c2_spin.setValue(self.current_config.wolfe_c2)
        self.wolfe_c2_spin.setSingleStep(0.01)
        self.wolfe_c2_spin.setToolTip("Wolfe curvature condition parameter")
        self.wolfe_c2_spin.valueChanged.connect(self._on_config_changed)
        line_search_layout.addWidget(self.wolfe_c2_spin, 2, 1)
        
        layout.addWidget(line_search_group)
        
        # Optimization Parameters
        opt_group = QGroupBox("Optimization Parameters")
        opt_layout = QGridLayout(opt_group)
        
        opt_layout.addWidget(QLabel("Max Iterations:"), 0, 0)
        self.max_iter_spin = QSpinBox()
        self.max_iter_spin.setRange(10, 1000)
        self.max_iter_spin.setValue(self.current_config.max_iterations)
        self.max_iter_spin.setToolTip("Maximum SGLBO iterations")
        self.max_iter_spin.valueChanged.connect(self._on_config_changed)
        opt_layout.addWidget(self.max_iter_spin, 0, 1)
        
        opt_layout.addWidget(QLabel("Exploration Factor:"), 1, 0)
        self.exploration_spin = QDoubleSpinBox()
        self.exploration_spin.setRange(0.0, 1.0)
        self.exploration_spin.setDecimals(3)
        self.exploration_spin.setValue(self.current_config.exploration_factor)
        self.exploration_spin.setSingleStep(0.01)
        self.exploration_spin.setToolTip("Balance between exploration and exploitation")
        self.exploration_spin.valueChanged.connect(self._on_config_changed)
        opt_layout.addWidget(self.exploration_spin, 1, 1)
        
        opt_layout.addWidget(QLabel("Convergence Tol:"), 2, 0)
        self.conv_tol_spin = QDoubleSpinBox()
        self.conv_tol_spin.setRange(1e-10, 1e-3)
        self.conv_tol_spin.setDecimals(10)
        self.conv_tol_spin.setValue(self.current_config.convergence_tolerance)
        self.conv_tol_spin.setSingleStep(1e-7)
        self.conv_tol_spin.setToolTip("Convergence tolerance for SGLBO")
        self.conv_tol_spin.valueChanged.connect(self._on_config_changed)
        opt_layout.addWidget(self.conv_tol_spin, 2, 1)
        
        layout.addWidget(opt_group)
        
        # Advanced Options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QGridLayout(advanced_group)
        
        self.adaptive_exploration_check = QCheckBox("Adaptive Exploration")
        self.adaptive_exploration_check.setChecked(self.current_config.adaptive_exploration)
        self.adaptive_exploration_check.setToolTip("Enable adaptive exploration based on gradient information")
        self.adaptive_exploration_check.toggled.connect(self._on_config_changed)
        advanced_layout.addWidget(self.adaptive_exploration_check, 0, 0)
        
        self.use_gpu_check = QCheckBox("Use GPU")
        self.use_gpu_check.setChecked(self.current_config.use_gpu)
        self.use_gpu_check.setToolTip("Enable GPU acceleration for computations")
        self.use_gpu_check.toggled.connect(self._on_config_changed)
        advanced_layout.addWidget(self.use_gpu_check, 0, 1)
        
        advanced_layout.addWidget(QLabel("Multi-start Points:"), 1, 0)
        self.multi_start_spin = QSpinBox()
        self.multi_start_spin.setRange(1, 10)
        self.multi_start_spin.setValue(self.current_config.multi_start_points)
        self.multi_start_spin.setToolTip("Number of starting points for SGLBO optimization")
        self.multi_start_spin.valueChanged.connect(self._on_config_changed)
        advanced_layout.addWidget(self.multi_start_spin, 1, 1)
        
        layout.addWidget(advanced_group)
        
        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self._reset_to_defaults)
        layout.addWidget(reset_button)
        
    def _on_config_changed(self):
        """Handle configuration changes."""
        try:
            # Update configuration
            self.current_config.gradient_method = GradientMethod(self.gradient_method_combo.currentText())
            self.current_config.line_search_method = LineSearchMethod(self.line_search_combo.currentText())
            self.current_config.finite_diff_step = self.finite_diff_spin.value()
            self.current_config.armijo_c1 = self.armijo_c1_spin.value()
            self.current_config.wolfe_c2 = self.wolfe_c2_spin.value()
            self.current_config.max_iterations = self.max_iter_spin.value()
            self.current_config.exploration_factor = self.exploration_spin.value()
            self.current_config.convergence_tolerance = self.conv_tol_spin.value()
            self.current_config.adaptive_exploration = self.adaptive_exploration_check.isChecked()
            self.current_config.use_gpu = self.use_gpu_check.isChecked()
            self.current_config.multi_start_points = self.multi_start_spin.value()
            
            # Emit signal
            self.config_changed.emit(self.current_config)
            
        except Exception as e:
            logger.error(f"Error updating SGLBO configuration: {e}")
    
    def _reset_to_defaults(self):
        """Reset configuration to default values."""
        try:
            self.current_config = SGLBOConfig()
            
            # Update UI controls
            self.gradient_method_combo.setCurrentText(self.current_config.gradient_method.value)
            self.line_search_combo.setCurrentText(self.current_config.line_search_method.value)
            self.finite_diff_spin.setValue(self.current_config.finite_diff_step)
            self.armijo_c1_spin.setValue(self.current_config.armijo_c1)
            self.wolfe_c2_spin.setValue(self.current_config.wolfe_c2)
            self.max_iter_spin.setValue(self.current_config.max_iterations)
            self.exploration_spin.setValue(self.current_config.exploration_factor)
            self.conv_tol_spin.setValue(self.current_config.convergence_tolerance)
            self.adaptive_exploration_check.setChecked(self.current_config.adaptive_exploration)
            self.use_gpu_check.setChecked(self.current_config.use_gpu)
            self.multi_start_spin.setValue(self.current_config.multi_start_points)
            
            self.config_changed.emit(self.current_config)
            
        except Exception as e:
            logger.error(f"Error resetting SGLBO configuration: {e}")
    
    def get_config(self) -> SGLBOConfig:
        """Get current configuration."""
        return self.current_config
    
    def set_config(self, config: SGLBOConfig):
        """Set configuration and update UI."""
        try:
            self.current_config = config
            
            # Update UI controls without triggering signals
            self.gradient_method_combo.blockSignals(True)
            self.gradient_method_combo.setCurrentText(config.gradient_method.value)
            self.gradient_method_combo.blockSignals(False)
            
            self.line_search_combo.blockSignals(True)
            self.line_search_combo.setCurrentText(config.line_search_method.value)
            self.line_search_combo.blockSignals(False)
            
            self.finite_diff_spin.setValue(config.finite_diff_step)
            self.armijo_c1_spin.setValue(config.armijo_c1)
            self.wolfe_c2_spin.setValue(config.wolfe_c2)
            self.max_iter_spin.setValue(config.max_iterations)
            self.exploration_spin.setValue(config.exploration_factor)
            self.conv_tol_spin.setValue(config.convergence_tolerance)
            self.adaptive_exploration_check.setChecked(config.adaptive_exploration)
            self.use_gpu_check.setChecked(config.use_gpu)
            self.multi_start_spin.setValue(config.multi_start_points)
            
        except Exception as e:
            logger.error(f"Error setting SGLBO configuration: {e}")


class SGLBOMonitoringWidget(QWidget):
    """Widget for monitoring SGLBO optimization progress."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.optimizer = None
        self.controller = None
        self.monitoring_data = []
        self.init_ui()
        
        # Timer for periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_monitoring)
        self.update_timer.start(1000)  # Update every second
        
    def init_ui(self):
        """Initialize monitoring UI."""
        layout = QVBoxLayout(self)
        
        # Status display
        status_group = QGroupBox("Optimization Status")
        status_layout = QGridLayout(status_group)
        
        status_layout.addWidget(QLabel("Current Phase:"), 0, 0)
        self.phase_label = QLabel("Not Started")
        self.phase_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.phase_label, 0, 1)
        
        status_layout.addWidget(QLabel("Total Evaluations:"), 1, 0)
        self.evaluations_label = QLabel("0")
        status_layout.addWidget(self.evaluations_label, 1, 1)
        
        status_layout.addWidget(QLabel("Gradient Evaluations:"), 2, 0)
        self.gradient_evals_label = QLabel("0")
        status_layout.addWidget(self.gradient_evals_label, 2, 1)
        
        status_layout.addWidget(QLabel("Current Best:"), 3, 0)
        self.best_value_label = QLabel("N/A")
        status_layout.addWidget(self.best_value_label, 3, 1)
        
        layout.addWidget(status_group)
        
        # Progress bars
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        progress_layout.addWidget(QLabel("Screening Progress:"))
        self.screening_progress = QProgressBar()
        self.screening_progress.setRange(0, 100)
        progress_layout.addWidget(self.screening_progress)
        
        progress_layout.addWidget(QLabel("Overall Progress:"))
        self.overall_progress = QProgressBar()
        self.overall_progress.setRange(0, 100)
        progress_layout.addWidget(self.overall_progress)
        
        layout.addWidget(progress_group)
        
        # Performance metrics
        perf_group = QGroupBox("Performance Metrics")
        perf_layout = QGridLayout(perf_group)
        
        perf_layout.addWidget(QLabel("Avg. Gradient Time:"), 0, 0)
        self.gradient_time_label = QLabel("N/A")
        perf_layout.addWidget(self.gradient_time_label, 0, 1)
        
        perf_layout.addWidget(QLabel("Avg. Line Search Time:"), 1, 0)
        self.line_search_time_label = QLabel("N/A")
        perf_layout.addWidget(self.line_search_time_label, 1, 1)
        
        perf_layout.addWidget(QLabel("Success Rate:"), 2, 0)
        self.success_rate_label = QLabel("N/A")
        perf_layout.addWidget(self.success_rate_label, 2, 1)
        
        layout.addWidget(perf_group)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.pause_button = QPushButton("Pause Monitoring")
        self.pause_button.clicked.connect(self._toggle_monitoring)
        controls_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("Reset Monitoring")
        self.reset_button.clicked.connect(self._reset_monitoring)
        controls_layout.addWidget(self.reset_button)
        
        layout.addLayout(controls_layout)
        
    def set_optimizer(self, optimizer: AdvancedSGLBOOptimizer):
        """Set the optimizer to monitor."""
        self.optimizer = optimizer
        
    def set_controller(self, controller: HybridSGLBOController):
        """Set the controller to monitor."""
        self.controller = controller
        
    def _update_monitoring(self):
        """Update monitoring display."""
        try:
            if self.controller is not None:
                self._update_from_controller()
            elif self.optimizer is not None:
                self._update_from_optimizer()
                
        except Exception as e:
            logger.error(f"Error updating SGLBO monitoring: {e}")
    
    def _update_from_controller(self):
        """Update monitoring from hybrid controller."""
        try:
            summary = self.controller.get_optimization_summary()
            
            # Update phase
            phase = summary.get("current_phase", "unknown")
            self.phase_label.setText(phase.replace("_", " ").title())
            
            # Update evaluation counts
            data_summary = summary.get("data_summary", {})
            total_samples = data_summary.get("total_samples", 0)
            self.evaluations_label.setText(str(total_samples))
            
            # Update progress bars
            if phase == "sglbo_screening":
                screening_samples = data_summary.get("screening_samples", 0)
                max_screening = getattr(self.controller.controller_config, 'max_screening_samples', 100)
                progress = min(100, (screening_samples / max_screening) * 100)
                self.screening_progress.setValue(int(progress))
                self.overall_progress.setValue(int(progress * 0.7))  # Screening is 70% of total
            elif phase == "detailed_bo":
                self.screening_progress.setValue(100)
                detailed_samples = data_summary.get("detailed_samples", 0)
                # Estimate progress based on detailed samples (arbitrary scale)
                detailed_progress = min(30, detailed_samples * 2)  # Rough estimate
                self.overall_progress.setValue(70 + int(detailed_progress))
            
            # Update SGLBO specific metrics if available
            sglbo_summary = summary.get("sglbo_summary", {})
            if sglbo_summary:
                gradient_evals = sglbo_summary.get("gradient_evaluations", 0)
                self.gradient_evals_label.setText(str(gradient_evals))
                
                # Timing stats
                timing_stats = sglbo_summary.get("timing_stats", {})
                if timing_stats:
                    gradient_time = timing_stats.get("gradient_computation", 0)
                    line_search_time = timing_stats.get("line_search", 0)
                    
                    if gradient_evals > 0:
                        avg_gradient_time = gradient_time / gradient_evals
                        self.gradient_time_label.setText(f"{avg_gradient_time:.4f}s")
                    
                    if gradient_evals > 0:
                        avg_line_search_time = line_search_time / gradient_evals
                        self.line_search_time_label.setText(f"{avg_line_search_time:.4f}s")
                
        except Exception as e:
            logger.debug(f"Error updating from controller: {e}")
    
    def _update_from_optimizer(self):
        """Update monitoring from SGLBO optimizer."""
        try:
            summary = self.optimizer.get_optimization_summary()
            
            # Update basic metrics
            total_experiments = summary.get("total_experiments", 0)
            gradient_evals = summary.get("gradient_evaluations", 0)
            
            self.evaluations_label.setText(str(total_experiments))
            self.gradient_evals_label.setText(str(gradient_evals))
            
            # Update timing stats
            timing_stats = summary.get("timing_stats", {})
            if timing_stats and gradient_evals > 0:
                gradient_time = timing_stats.get("gradient_computation", 0)
                line_search_time = timing_stats.get("line_search", 0)
                
                avg_gradient_time = gradient_time / gradient_evals
                avg_line_search_time = line_search_time / gradient_evals
                
                self.gradient_time_label.setText(f"{avg_gradient_time:.4f}s")
                self.line_search_time_label.setText(f"{avg_line_search_time:.4f}s")
            
            # Update progress (estimate based on iterations)
            max_iter = getattr(self.optimizer.config, 'max_iterations', 100)
            current_iter = len(summary.get("convergence_history", []))
            progress = min(100, (current_iter / max_iter) * 100)
            self.screening_progress.setValue(int(progress))
            
        except Exception as e:
            logger.debug(f"Error updating from optimizer: {e}")
    
    def _toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.update_timer.isActive():
            self.update_timer.stop()
            self.pause_button.setText("Resume Monitoring")
        else:
            self.update_timer.start(1000)
            self.pause_button.setText("Pause Monitoring")
    
    def _reset_monitoring(self):
        """Reset monitoring data."""
        self.monitoring_data.clear()
        self.phase_label.setText("Not Started")
        self.evaluations_label.setText("0")
        self.gradient_evals_label.setText("0")
        self.best_value_label.setText("N/A")
        self.gradient_time_label.setText("N/A")
        self.line_search_time_label.setText("N/A")
        self.success_rate_label.setText("N/A")
        self.screening_progress.setValue(0)
        self.overall_progress.setValue(0)


class SGLBOVisualizationWidget(QWidget):
    """Widget for SGLBO visualizations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.optimizer = None
        self.current_data = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize visualization UI."""
        layout = QVBoxLayout(self)
        
        # Visualization controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Visualization:"))
        self.viz_combo = QComboBox()
        self.viz_combo.addItems([
            "Convergence History",
            "Gradient Magnitude",
            "Parameter Evolution", 
            "Objective Progress",
            "Performance Metrics"
        ])
        self.viz_combo.currentTextChanged.connect(self._update_visualization)
        controls_layout.addWidget(self.viz_combo)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._update_visualization)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
    def set_optimizer(self, optimizer: AdvancedSGLBOOptimizer):
        """Set optimizer for visualization."""
        self.optimizer = optimizer
        self._update_visualization()
        
    def set_data(self, data: pd.DataFrame):
        """Set data for visualization."""
        self.current_data = data
        self._update_visualization()
        
    def _update_visualization(self):
        """Update the current visualization."""
        try:
            self.figure.clear()
            
            viz_type = self.viz_combo.currentText()
            
            if viz_type == "Convergence History":
                self._plot_convergence_history()
            elif viz_type == "Gradient Magnitude":
                self._plot_gradient_magnitude()
            elif viz_type == "Parameter Evolution":
                self._plot_parameter_evolution()
            elif viz_type == "Objective Progress":
                self._plot_objective_progress()
            elif viz_type == "Performance Metrics":
                self._plot_performance_metrics()
                
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating SGLBO visualization: {e}")
            self._show_error_message(str(e))
    
    def _plot_convergence_history(self):
        """Plot convergence history."""
        try:
            if self.optimizer is None:
                self._show_no_data_message()
                return
                
            summary = self.optimizer.get_optimization_summary()
            convergence_history = summary.get("convergence_history", [])
            
            if not convergence_history:
                self._show_no_data_message("No convergence data available")
                return
            
            ax = self.figure.add_subplot(111)
            
            iterations = [data.get("iteration", i) for i, data in enumerate(convergence_history)]
            function_values = [data.get("f", 0) for data in convergence_history]
            gradient_norms = [data.get("gradient_norm", 0) for data in convergence_history]
            
            # Plot function values
            ax2 = ax.twinx()
            ax.plot(iterations, function_values, 'b-', label='Function Value', linewidth=2)
            ax2.plot(iterations, gradient_norms, 'r--', label='Gradient Norm', alpha=0.7)
            
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Function Value', color='b')
            ax2.set_ylabel('Gradient Norm', color='r')
            
            ax.set_title('SGLBO Convergence History')
            ax.grid(True, alpha=0.3)
            
            # Legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='best')
            
        except Exception as e:
            logger.error(f"Error plotting convergence history: {e}")
            self._show_error_message(str(e))
    
    def _plot_gradient_magnitude(self):
        """Plot gradient magnitude over time."""
        try:
            if self.optimizer is None:
                self._show_no_data_message()
                return
                
            summary = self.optimizer.get_optimization_summary()
            convergence_history = summary.get("convergence_history", [])
            
            if not convergence_history:
                self._show_no_data_message("No gradient data available")
                return
            
            ax = self.figure.add_subplot(111)
            
            iterations = [data.get("iteration", i) for i, data in enumerate(convergence_history)]
            gradient_norms = [data.get("gradient_norm", 0) for data in convergence_history]
            
            ax.semilogy(iterations, gradient_norms, 'g-', linewidth=2, marker='o', markersize=4)
            ax.set_xlabel('Iteration')
            ax.set_ylabel('Gradient Norm (log scale)')
            ax.set_title('Gradient Magnitude Evolution')
            ax.grid(True, alpha=0.3)
            
            # Add convergence threshold line if available
            if hasattr(self.optimizer, 'config'):
                threshold = getattr(self.optimizer.config, 'min_gradient_norm', None)
                if threshold:
                    ax.axhline(y=threshold, color='r', linestyle='--', alpha=0.7, 
                              label=f'Convergence Threshold: {threshold:.2e}')
                    ax.legend()
                    
        except Exception as e:
            logger.error(f"Error plotting gradient magnitude: {e}")
            self._show_error_message(str(e))
    
    def _plot_parameter_evolution(self):
        """Plot parameter evolution over iterations."""
        try:
            if self.current_data is None or self.current_data.empty:
                self._show_no_data_message("No parameter data available")
                return
            
            ax = self.figure.add_subplot(111)
            
            # Get parameter columns (excluding objective columns)
            if hasattr(self.optimizer, 'parameter_names'):
                param_cols = [col for col in self.current_data.columns if col in self.optimizer.parameter_names]
            else:
                # Heuristic: assume first few columns are parameters
                param_cols = self.current_data.columns[:min(5, len(self.current_data.columns))]
            
            if not param_cols:
                self._show_no_data_message("No parameter columns found")
                return
            
            # Plot parameter evolution
            for i, param in enumerate(param_cols[:5]):  # Limit to 5 parameters for readability
                values = self.current_data[param].values
                iterations = range(len(values))
                ax.plot(iterations, values, label=param, linewidth=1.5, marker='o', markersize=3)
            
            ax.set_xlabel('Evaluation')
            ax.set_ylabel('Parameter Value')
            ax.set_title('Parameter Evolution')
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(True, alpha=0.3)
            
            self.figure.tight_layout()
            
        except Exception as e:
            logger.error(f"Error plotting parameter evolution: {e}")
            self._show_error_message(str(e))
    
    def _plot_objective_progress(self):
        """Plot objective progress over evaluations."""
        try:
            if self.current_data is None or self.current_data.empty:
                self._show_no_data_message("No objective data available")
                return
            
            ax = self.figure.add_subplot(111)
            
            # Get objective columns
            if hasattr(self.optimizer, 'objective_names'):
                obj_cols = [col for col in self.current_data.columns if col in self.optimizer.objective_names]
            else:
                # Heuristic: assume last few columns are objectives
                obj_cols = self.current_data.columns[-min(3, len(self.current_data.columns)):]
            
            if not obj_cols:
                self._show_no_data_message("No objective columns found")
                return
            
            evaluations = range(len(self.current_data))
            
            for obj in obj_cols:
                values = self.current_data[obj].values
                # Plot running best (cumulative best)
                running_best = np.maximum.accumulate(values)  # Assume maximization
                ax.plot(evaluations, running_best, label=f'{obj} (Best)', linewidth=2)
                ax.plot(evaluations, values, label=f'{obj} (Current)', alpha=0.5, linewidth=1)
            
            ax.set_xlabel('Evaluation')
            ax.set_ylabel('Objective Value')
            ax.set_title('Objective Progress')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            logger.error(f"Error plotting objective progress: {e}")
            self._show_error_message(str(e))
    
    def _plot_performance_metrics(self):
        """Plot performance metrics."""
        try:
            if self.optimizer is None:
                self._show_no_data_message()
                return
                
            summary = self.optimizer.get_optimization_summary()
            timing_stats = summary.get("timing_stats", {})
            
            if not timing_stats:
                self._show_no_data_message("No performance data available")
                return
            
            ax = self.figure.add_subplot(111)
            
            # Create bar chart of timing statistics
            metrics = list(timing_stats.keys())
            times = list(timing_stats.values())
            
            bars = ax.bar(metrics, times, alpha=0.7)
            ax.set_ylabel('Time (seconds)')
            ax.set_title('SGLBO Performance Metrics')
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, time in zip(bars, times):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{time:.3f}s', ha='center', va='bottom')
            
            self.figure.tight_layout()
            
        except Exception as e:
            logger.error(f"Error plotting performance metrics: {e}")
            self._show_error_message(str(e))
    
    def _show_no_data_message(self, message="No data available for visualization"):
        """Show message when no data is available."""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center', 
                transform=ax.transAxes, fontsize=14, style='italic')
        ax.set_xticks([])
        ax.set_yticks([])
    
    def _show_error_message(self, error_message):
        """Show error message in plot."""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, f"Error: {error_message}", ha='center', va='center',
                transform=ax.transAxes, fontsize=12, color='red')
        ax.set_xticks([])
        ax.set_yticks([])


class AdvancedSGLBOControlWidget(QWidget):
    """Main widget combining all SGLBO controls."""
    
    optimization_started = pyqtSignal()
    optimization_stopped = pyqtSignal()
    config_changed = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.optimizer = None
        self.controller = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the main UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Configuration tab
        self.config_widget = SGLBOConfigWidget()
        self.config_widget.config_changed.connect(self.config_changed)
        self.tab_widget.addTab(self.config_widget, "Configuration")
        
        # Monitoring tab
        self.monitoring_widget = SGLBOMonitoringWidget()
        self.tab_widget.addTab(self.monitoring_widget, "Monitoring")
        
        # Visualization tab
        self.visualization_widget = SGLBOVisualizationWidget()
        self.tab_widget.addTab(self.visualization_widget, "Visualization")
        
        layout.addWidget(self.tab_widget)
        
        # Control buttons
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Start SGLBO Optimization")
        self.start_button.clicked.connect(self._start_optimization)
        buttons_layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Optimization")
        self.stop_button.clicked.connect(self._stop_optimization)
        self.stop_button.setEnabled(False)
        buttons_layout.addWidget(self.stop_button)
        
        self.transition_button = QPushButton("Force Transition to BO")
        self.transition_button.clicked.connect(self._force_transition)
        self.transition_button.setEnabled(False)
        buttons_layout.addWidget(self.transition_button)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
    def set_optimizer(self, optimizer: AdvancedSGLBOOptimizer):
        """Set the SGLBO optimizer."""
        self.optimizer = optimizer
        self.monitoring_widget.set_optimizer(optimizer)
        self.visualization_widget.set_optimizer(optimizer)
        
    def set_controller(self, controller: HybridSGLBOController):
        """Set the hybrid controller."""
        self.controller = controller
        self.monitoring_widget.set_controller(controller)
        
    def set_experimental_data(self, data: pd.DataFrame):
        """Set experimental data for visualization."""
        self.visualization_widget.set_data(data)
        
    def get_sglbo_config(self) -> SGLBOConfig:
        """Get current SGLBO configuration."""
        return self.config_widget.get_config()
        
    def _start_optimization(self):
        """Start SGLBO optimization."""
        try:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.transition_button.setEnabled(True)
            self.optimization_started.emit()
            
        except Exception as e:
            logger.error(f"Error starting SGLBO optimization: {e}")
    
    def _stop_optimization(self):
        """Stop SGLBO optimization."""
        try:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.transition_button.setEnabled(False)
            self.optimization_stopped.emit()
            
        except Exception as e:
            logger.error(f"Error stopping SGLBO optimization: {e}")
    
    def _force_transition(self):
        """Force transition to detailed BO."""
        try:
            if self.controller is not None:
                result = self.controller.force_transition_to_detailed_bo()
                if result["success"]:
                    QMessageBox.information(self, "Transition", "Successfully transitioned to detailed BO")
                else:
                    QMessageBox.warning(self, "Transition Failed", result["message"])
            else:
                QMessageBox.warning(self, "No Controller", "No hybrid controller available")
                
        except Exception as e:
            logger.error(f"Error forcing transition: {e}")
            QMessageBox.critical(self, "Error", f"Failed to force transition: {e}")