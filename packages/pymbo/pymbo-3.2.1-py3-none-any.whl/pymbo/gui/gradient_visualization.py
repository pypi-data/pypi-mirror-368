"""
Advanced Gradient Visualization for SGLBO
=========================================

This module provides sophisticated visualization tools for gradient information
in SGLBO optimization. It includes gradient vector fields, exploration heat maps,
parameter sensitivity analysis, and interactive gradient flow visualizations.

Key Features:
- Real-time gradient vector field visualization
- Interactive parameter space exploration
- Gradient magnitude heat maps
- Optimization trajectory visualization
- Parameter sensitivity ranking
- Multi-dimensional gradient projections
- Convergence analysis with gradient metrics

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Advanced Gradient Visualization
"""

import sys
import logging
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
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
        logger = logging.getLogger(__name__)
        logger.warning("Qt not available - gradient visualization will not function")
        
        # Define dummy base classes
        class QWidget:
            pass
        class QVBoxLayout:
            pass
        class QHBoxLayout:
            pass
        class QComboBox:
            pass
        class QCheckBox:
            pass
        class QPushButton:
            pass
        class QSlider:
            pass
        class QLabel:
            pass
        class pyqtSignal:
            def __init__(self, *args):
                pass
        class Qt:
            Horizontal = 1

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from scipy.interpolate import griddata
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class GradientVectorFieldWidget(QWidget):
    """Widget for visualizing gradient vector fields in parameter space."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gradient_data = []
        self.parameter_names = []
        self.current_x_param = None
        self.current_y_param = None
        self.gradient_function = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("X Parameter:"))
        self.x_param_combo = QComboBox()
        self.x_param_combo.currentTextChanged.connect(self._update_plot)
        controls_layout.addWidget(self.x_param_combo)
        
        controls_layout.addWidget(QLabel("Y Parameter:"))
        self.y_param_combo = QComboBox()
        self.y_param_combo.currentTextChanged.connect(self._update_plot)
        controls_layout.addWidget(self.y_param_combo)
        
        self.show_trajectory_check = QCheckBox("Show Trajectory")
        self.show_trajectory_check.toggled.connect(self._update_plot)
        controls_layout.addWidget(self.show_trajectory_check)
        
        self.show_heatmap_check = QCheckBox("Show Heat Map")
        self.show_heatmap_check.setChecked(True)
        self.show_heatmap_check.toggled.connect(self._update_plot)
        controls_layout.addWidget(self.show_heatmap_check)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Additional controls
        controls2_layout = QHBoxLayout()
        
        controls2_layout.addWidget(QLabel("Grid Resolution:"))
        self.resolution_slider = QSlider(Qt.Horizontal)
        self.resolution_slider.setRange(10, 50)
        self.resolution_slider.setValue(20)
        self.resolution_slider.valueChanged.connect(self._update_plot)
        controls2_layout.addWidget(self.resolution_slider)
        
        self.resolution_label = QLabel("20")
        controls2_layout.addWidget(self.resolution_label)
        self.resolution_slider.valueChanged.connect(
            lambda v: self.resolution_label.setText(str(v))
        )
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._update_plot)
        controls2_layout.addWidget(self.refresh_button)
        
        controls2_layout.addStretch()
        layout.addLayout(controls2_layout)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
    def set_parameters(self, parameter_names: List[str]):
        """Set available parameters for visualization."""
        self.parameter_names = parameter_names
        
        # Update combo boxes
        self.x_param_combo.clear()
        self.y_param_combo.clear()
        
        self.x_param_combo.addItems(parameter_names)
        self.y_param_combo.addItems(parameter_names)
        
        # Set default selections
        if len(parameter_names) >= 2:
            self.x_param_combo.setCurrentText(parameter_names[0])
            self.y_param_combo.setCurrentText(parameter_names[1])
            self.current_x_param = parameter_names[0]
            self.current_y_param = parameter_names[1]
        elif len(parameter_names) == 1:
            self.x_param_combo.setCurrentText(parameter_names[0])
            self.current_x_param = parameter_names[0]
            
    def set_gradient_function(self, gradient_function: Callable):
        """Set function for computing gradients."""
        self.gradient_function = gradient_function
        
    def add_gradient_data(self, x_values: np.ndarray, gradients: np.ndarray):
        """Add gradient data point."""
        if len(x_values) == len(self.parameter_names):
            self.gradient_data.append({
                'x_values': x_values.copy(),
                'gradients': gradients.copy()
            })
            
        # Limit data storage
        if len(self.gradient_data) > 1000:
            self.gradient_data = self.gradient_data[-500:]
    
    def clear_gradient_data(self):
        """Clear all gradient data."""
        self.gradient_data.clear()
        
    def _update_plot(self):
        """Update the gradient vector field plot."""
        try:
            self.figure.clear()
            
            if (not self.parameter_names or 
                self.x_param_combo.currentText() == "" or
                self.y_param_combo.currentText() == ""):
                self._show_message("No parameters selected")
                return
                
            self.current_x_param = self.x_param_combo.currentText()
            self.current_y_param = self.y_param_combo.currentText()
            
            x_idx = self.parameter_names.index(self.current_x_param)
            y_idx = self.parameter_names.index(self.current_y_param)
            
            ax = self.figure.add_subplot(111)
            
            # Generate grid for vector field
            resolution = self.resolution_slider.value()
            x_grid = np.linspace(0, 1, resolution)
            y_grid = np.linspace(0, 1, resolution)
            X_grid, Y_grid = np.meshgrid(x_grid, y_grid)
            
            # Compute gradients on grid if gradient function available
            if self.gradient_function is not None:
                U_grid = np.zeros_like(X_grid)
                V_grid = np.zeros_like(Y_grid)
                magnitude_grid = np.zeros_like(X_grid)
                
                for i in range(resolution):
                    for j in range(resolution):
                        # Create parameter vector
                        x_point = np.zeros(len(self.parameter_names))
                        x_point[x_idx] = X_grid[i, j]
                        x_point[y_idx] = Y_grid[i, j]
                        
                        # For other parameters, use midpoint (could be improved)
                        for k in range(len(self.parameter_names)):
                            if k != x_idx and k != y_idx:
                                x_point[k] = 0.5
                        
                        try:
                            grad = self.gradient_function(x_point)
                            U_grid[i, j] = grad[x_idx]
                            V_grid[i, j] = grad[y_idx]
                            magnitude_grid[i, j] = np.linalg.norm(grad)
                        except Exception:
                            U_grid[i, j] = 0
                            V_grid[i, j] = 0
                            magnitude_grid[i, j] = 0
                
                # Show heat map of gradient magnitude
                if self.show_heatmap_check.isChecked():
                    im = ax.contourf(X_grid, Y_grid, magnitude_grid, levels=20, alpha=0.6, cmap='viridis')
                    self.figure.colorbar(im, ax=ax, label='Gradient Magnitude')
                
                # Plot vector field
                skip = max(1, resolution // 15)  # Don't plot too many arrows
                ax.quiver(X_grid[::skip, ::skip], Y_grid[::skip, ::skip], 
                         U_grid[::skip, ::skip], V_grid[::skip, ::skip],
                         scale=10, alpha=0.8, width=0.003)
            
            # Plot trajectory from gradient data
            if self.show_trajectory_check.isChecked() and self.gradient_data:
                x_traj = [data['x_values'][x_idx] for data in self.gradient_data]
                y_traj = [data['x_values'][y_idx] for data in self.gradient_data]
                
                # Plot trajectory line
                ax.plot(x_traj, y_traj, 'r-', linewidth=2, alpha=0.8, label='Optimization Path')
                
                # Plot trajectory points
                ax.scatter(x_traj, y_traj, c=range(len(x_traj)), 
                          cmap='Reds', s=30, alpha=0.8, zorder=5)
                
                # Mark start and end points
                if len(x_traj) > 0:
                    ax.scatter(x_traj[0], y_traj[0], c='green', s=100, 
                              marker='o', label='Start', zorder=6, edgecolors='black')
                    ax.scatter(x_traj[-1], y_traj[-1], c='red', s=100, 
                              marker='s', label='Current', zorder=6, edgecolors='black')
                
                ax.legend()
            
            ax.set_xlabel(self.current_x_param)
            ax.set_ylabel(self.current_y_param)
            ax.set_title(f'Gradient Vector Field: {self.current_x_param} vs {self.current_y_param}')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.grid(True, alpha=0.3)
            
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating gradient vector field: {e}")
            self._show_message(f"Error: {e}")
    
    def _show_message(self, message: str):
        """Show message on the plot."""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center',
                transform=ax.transAxes, fontsize=14, style='italic')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()


class ParameterSensitivityWidget(QWidget):
    """Widget for visualizing parameter sensitivity analysis."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sensitivity_data = {}
        self.parameter_names = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Analysis Type:"))
        self.analysis_combo = QComboBox()
        self.analysis_combo.addItems([
            "Gradient Magnitude",
            "Gradient Components", 
            "Parameter Importance",
            "Sensitivity Ranking"
        ])
        self.analysis_combo.currentTextChanged.connect(self._update_plot)
        controls_layout.addWidget(self.analysis_combo)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._update_plot)
        controls_layout.addWidget(self.refresh_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
    def set_parameters(self, parameter_names: List[str]):
        """Set parameter names."""
        self.parameter_names = parameter_names
        
    def add_sensitivity_data(self, x_values: np.ndarray, gradients: np.ndarray):
        """Add sensitivity data point."""
        if len(x_values) == len(self.parameter_names) and len(gradients) == len(self.parameter_names):
            for i, param_name in enumerate(self.parameter_names):
                if param_name not in self.sensitivity_data:
                    self.sensitivity_data[param_name] = {
                        'x_values': [],
                        'gradients': [],
                        'magnitudes': []
                    }
                
                self.sensitivity_data[param_name]['x_values'].append(x_values[i])
                self.sensitivity_data[param_name]['gradients'].append(gradients[i])
                self.sensitivity_data[param_name]['magnitudes'].append(abs(gradients[i]))
                
                # Limit data storage
                if len(self.sensitivity_data[param_name]['x_values']) > 500:
                    self.sensitivity_data[param_name]['x_values'] = \
                        self.sensitivity_data[param_name]['x_values'][-250:]
                    self.sensitivity_data[param_name]['gradients'] = \
                        self.sensitivity_data[param_name]['gradients'][-250:]
                    self.sensitivity_data[param_name]['magnitudes'] = \
                        self.sensitivity_data[param_name]['magnitudes'][-250:]
    
    def clear_sensitivity_data(self):
        """Clear all sensitivity data."""
        self.sensitivity_data.clear()
        
    def _update_plot(self):
        """Update sensitivity visualization."""
        try:
            self.figure.clear()
            
            if not self.sensitivity_data:
                self._show_message("No sensitivity data available")
                return
                
            analysis_type = self.analysis_combo.currentText()
            
            if analysis_type == "Gradient Magnitude":
                self._plot_gradient_magnitude()
            elif analysis_type == "Gradient Components":
                self._plot_gradient_components()
            elif analysis_type == "Parameter Importance":
                self._plot_parameter_importance()
            elif analysis_type == "Sensitivity Ranking":
                self._plot_sensitivity_ranking()
                
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating sensitivity plot: {e}")
            self._show_message(f"Error: {e}")
    
    def _plot_gradient_magnitude(self):
        """Plot gradient magnitude over time."""
        ax = self.figure.add_subplot(111)
        
        for param_name, data in self.sensitivity_data.items():
            if data['magnitudes']:
                iterations = range(len(data['magnitudes']))
                ax.plot(iterations, data['magnitudes'], label=param_name, 
                       linewidth=1.5, alpha=0.8)
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Gradient Magnitude')
        ax.set_title('Parameter Gradient Magnitudes Over Time')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
    
    def _plot_gradient_components(self):
        """Plot gradient components."""
        ax = self.figure.add_subplot(111)
        
        for param_name, data in self.sensitivity_data.items():
            if data['gradients']:
                iterations = range(len(data['gradients']))
                ax.plot(iterations, data['gradients'], label=param_name,
                       linewidth=1.5, alpha=0.8)
        
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Gradient Component')
        ax.set_title('Parameter Gradient Components Over Time')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        self.figure.tight_layout()
    
    def _plot_parameter_importance(self):
        """Plot parameter importance based on average gradient magnitude."""
        # Calculate average gradient magnitudes
        importance_scores = {}
        for param_name, data in self.sensitivity_data.items():
            if data['magnitudes']:
                importance_scores[param_name] = np.mean(data['magnitudes'])
        
        if not importance_scores:
            self._show_message("No importance data available")
            return
        
        ax = self.figure.add_subplot(111)
        
        params = list(importance_scores.keys())
        scores = list(importance_scores.values())
        
        # Sort by importance
        sorted_indices = np.argsort(scores)[::-1]  # Descending order
        params_sorted = [params[i] for i in sorted_indices]
        scores_sorted = [scores[i] for i in sorted_indices]
        
        bars = ax.barh(params_sorted, scores_sorted, alpha=0.7)
        
        # Color bars by importance
        colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, len(bars)))
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        ax.set_xlabel('Average Gradient Magnitude')
        ax.set_title('Parameter Importance Ranking')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (param, score) in enumerate(zip(params_sorted, scores_sorted)):
            ax.text(score + max(scores_sorted) * 0.01, i, f'{score:.4f}',
                   va='center', ha='left', fontsize=10)
    
    def _plot_sensitivity_ranking(self):
        """Plot sensitivity ranking over time."""
        if len(self.parameter_names) < 2:
            self._show_message("Need at least 2 parameters for ranking")
            return
        
        ax = self.figure.add_subplot(111)
        
        # Calculate rolling rankings
        max_length = max(len(data['magnitudes']) for data in self.sensitivity_data.values())
        
        if max_length < 5:
            self._show_message("Need more data for ranking analysis")
            return
        
        rankings = {param: [] for param in self.parameter_names}
        window_size = min(10, max_length // 5)
        
        for i in range(window_size, max_length):
            window_scores = {}
            for param_name, data in self.sensitivity_data.items():
                if i < len(data['magnitudes']):
                    # Calculate average over window
                    window_data = data['magnitudes'][max(0, i-window_size):i+1]
                    window_scores[param_name] = np.mean(window_data)
            
            # Rank parameters (1 = most important)
            sorted_params = sorted(window_scores.keys(), key=lambda x: window_scores[x], reverse=True)
            for rank, param in enumerate(sorted_params, 1):
                rankings[param].append(rank)
        
        # Plot rankings
        iterations = range(window_size, max_length)
        for param_name, rank_history in rankings.items():
            if rank_history:
                ax.plot(iterations[:len(rank_history)], rank_history, 
                       label=param_name, linewidth=2, marker='o', markersize=4)
        
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Importance Rank')
        ax.set_title('Parameter Importance Ranking Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()  # Rank 1 at top
    
    def _show_message(self, message: str):
        """Show message on the plot."""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center',
                transform=ax.transAxes, fontsize=14, style='italic')
        ax.set_xticks([])
        ax.set_yticks([])


class GradientExplorationWidget(QWidget):
    """Widget for interactive gradient exploration."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parameter_names = []
        self.gradient_function = None
        self.current_point = None
        self.exploration_history = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.explore_button = QPushButton("Explore Current Point")
        self.explore_button.clicked.connect(self._explore_current_point)
        controls_layout.addWidget(self.explore_button)
        
        self.random_point_button = QPushButton("Random Point")
        self.random_point_button.clicked.connect(self._explore_random_point)
        controls_layout.addWidget(self.random_point_button)
        
        self.clear_history_button = QPushButton("Clear History")
        self.clear_history_button.clicked.connect(self._clear_history)
        controls_layout.addWidget(self.clear_history_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Parameter sliders (will be added dynamically)
        self.sliders_layout = QVBoxLayout()
        layout.addLayout(self.sliders_layout)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.parameter_sliders = {}
        
    def set_parameters(self, parameter_names: List[str]):
        """Set parameter names and create sliders."""
        self.parameter_names = parameter_names
        self.current_point = np.array([0.5] * len(parameter_names))  # Start at center
        
        # Clear existing sliders
        for i in reversed(range(self.sliders_layout.count())):
            child = self.sliders_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        self.parameter_sliders.clear()
        
        # Create sliders for each parameter
        for param_name in parameter_names:
            param_layout = QHBoxLayout()
            
            label = QLabel(f"{param_name}:")
            label.setFixedWidth(100)
            param_layout.addWidget(label)
            
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 1000)
            slider.setValue(500)  # Middle position
            slider.valueChanged.connect(self._on_slider_changed)
            param_layout.addWidget(slider)
            
            value_label = QLabel("0.50")
            value_label.setFixedWidth(50)
            param_layout.addWidget(value_label)
            
            self.sliders_layout.addLayout(param_layout)
            
            self.parameter_sliders[param_name] = {
                'slider': slider,
                'label': value_label
            }
        
    def set_gradient_function(self, gradient_function: Callable):
        """Set function for computing gradients."""
        self.gradient_function = gradient_function
        
    def _on_slider_changed(self):
        """Handle slider value changes."""
        if not self.parameter_names:
            return
            
        # Update current point from sliders
        for i, param_name in enumerate(self.parameter_names):
            slider_value = self.parameter_sliders[param_name]['slider'].value()
            param_value = slider_value / 1000.0  # Convert to [0, 1]
            self.current_point[i] = param_value
            
            # Update label
            self.parameter_sliders[param_name]['label'].setText(f"{param_value:.3f}")
        
        # Auto-explore if gradient function is available
        if self.gradient_function is not None:
            self._explore_current_point()
    
    def _explore_current_point(self):
        """Explore gradient at current point."""
        if self.gradient_function is None or self.current_point is None:
            return
            
        try:
            # Compute gradient at current point
            gradient = self.gradient_function(self.current_point)
            
            # Store in history
            self.exploration_history.append({
                'point': self.current_point.copy(),
                'gradient': gradient.copy(),
                'magnitude': np.linalg.norm(gradient)
            })
            
            # Update visualization
            self._update_exploration_plot()
            
        except Exception as e:
            logger.error(f"Error exploring current point: {e}")
    
    def _explore_random_point(self):
        """Explore gradient at random point."""
        if not self.parameter_names:
            return
            
        # Generate random point
        random_point = np.random.random(len(self.parameter_names))
        
        # Update sliders
        for i, param_name in enumerate(self.parameter_names):
            slider_value = int(random_point[i] * 1000)
            self.parameter_sliders[param_name]['slider'].setValue(slider_value)
        
        # This will trigger _on_slider_changed which will explore the point
    
    def _clear_history(self):
        """Clear exploration history."""
        self.exploration_history.clear()
        self._update_exploration_plot()
    
    def _update_exploration_plot(self):
        """Update exploration visualization."""
        try:
            self.figure.clear()
            
            if not self.exploration_history:
                self._show_message("No exploration data")
                return
            
            # Create subplots
            if len(self.parameter_names) >= 2:
                ax1 = self.figure.add_subplot(121)
                ax2 = self.figure.add_subplot(122)
            else:
                ax1 = self.figure.add_subplot(111)
                ax2 = None
            
            # Plot gradient magnitude over exploration
            iterations = range(len(self.exploration_history))
            magnitudes = [data['magnitude'] for data in self.exploration_history]
            
            ax1.plot(iterations, magnitudes, 'b-o', linewidth=2, markersize=4)
            ax1.set_xlabel('Exploration Step')
            ax1.set_ylabel('Gradient Magnitude')
            ax1.set_title('Gradient Magnitude During Exploration')
            ax1.grid(True, alpha=0.3)
            
            # Mark current point
            if magnitudes:
                ax1.scatter([len(magnitudes)-1], [magnitudes[-1]], 
                           c='red', s=100, marker='s', zorder=5, 
                           label='Current', edgecolors='black')
                ax1.legend()
            
            # Plot parameter space exploration (if 2D available)
            if ax2 is not None and len(self.parameter_names) >= 2:
                x_values = [data['point'][0] for data in self.exploration_history]
                y_values = [data['point'][1] for data in self.exploration_history]
                
                # Color by gradient magnitude
                colors = magnitudes
                
                scatter = ax2.scatter(x_values, y_values, c=colors, cmap='viridis',
                                    s=50, alpha=0.8, edgecolors='black', linewidth=0.5)
                
                # Add trajectory line
                ax2.plot(x_values, y_values, 'k--', alpha=0.5, linewidth=1)
                
                # Mark start and current points
                if x_values:
                    ax2.scatter(x_values[0], y_values[0], c='green', s=100,
                               marker='o', label='Start', zorder=5, edgecolors='black')
                    ax2.scatter(x_values[-1], y_values[-1], c='red', s=100,
                               marker='s', label='Current', zorder=5, edgecolors='black')
                
                ax2.set_xlabel(self.parameter_names[0])
                ax2.set_ylabel(self.parameter_names[1])
                ax2.set_title('Parameter Space Exploration')
                ax2.set_xlim(0, 1)
                ax2.set_ylim(0, 1)
                ax2.grid(True, alpha=0.3)
                ax2.legend()
                
                # Add colorbar
                self.figure.colorbar(scatter, ax=ax2, label='Gradient Magnitude')
            
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating exploration plot: {e}")
            self._show_message(f"Error: {e}")
    
    def _show_message(self, message: str):
        """Show message on the plot."""
        ax = self.figure.add_subplot(111)
        ax.text(0.5, 0.5, message, ha='center', va='center',
                transform=ax.transAxes, fontsize=14, style='italic')
        ax.set_xticks([])
        ax.set_yticks([])
        self.canvas.draw()


class GradientVisualizationWidget(QWidget):
    """Main widget combining all gradient visualization components."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parameter_names = []
        self.gradient_function = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the main UI."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Vector field tab
        self.vector_field_widget = GradientVectorFieldWidget()
        self.tab_widget.addTab(self.vector_field_widget, "Vector Field")
        
        # Sensitivity analysis tab
        self.sensitivity_widget = ParameterSensitivityWidget()
        self.tab_widget.addTab(self.sensitivity_widget, "Sensitivity Analysis")
        
        # Interactive exploration tab
        self.exploration_widget = GradientExplorationWidget()
        self.tab_widget.addTab(self.exploration_widget, "Interactive Exploration")
        
        layout.addWidget(self.tab_widget)
        
    def set_parameters(self, parameter_names: List[str]):
        """Set parameter names for all widgets."""
        self.parameter_names = parameter_names
        self.vector_field_widget.set_parameters(parameter_names)
        self.sensitivity_widget.set_parameters(parameter_names)
        self.exploration_widget.set_parameters(parameter_names)
        
    def set_gradient_function(self, gradient_function: Callable):
        """Set gradient function for all widgets."""
        self.gradient_function = gradient_function
        self.vector_field_widget.set_gradient_function(gradient_function)
        self.exploration_widget.set_gradient_function(gradient_function)
        
    def add_gradient_data(self, x_values: np.ndarray, gradients: np.ndarray):
        """Add gradient data to relevant widgets."""
        self.vector_field_widget.add_gradient_data(x_values, gradients)
        self.sensitivity_widget.add_sensitivity_data(x_values, gradients)
        
    def clear_all_data(self):
        """Clear all gradient data."""
        self.vector_field_widget.clear_gradient_data()
        self.sensitivity_widget.clear_sensitivity_data()
        self.exploration_widget._clear_history()
        
    def refresh_all_plots(self):
        """Refresh all plots."""
        self.vector_field_widget._update_plot()
        self.sensitivity_widget._update_plot()
        self.exploration_widget._update_exploration_plot()