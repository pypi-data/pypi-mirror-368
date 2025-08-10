"""
Enhanced GUI Theme and Layout Improvements for PyMBO
===================================================

This module provides modern, professional GUI theming and layout improvements
for the PyMBO interface, addressing display issues and poor visual design.

Key Improvements:
- Modern color scheme with proper contrast
- Professional layout with better spacing
- Enhanced visual hierarchy and typography
- Responsive design elements
- Improved user experience

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Enhanced GUI Theme
"""

import sys
from typing import Dict, Any, Optional

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
        class QApplication: pass
        class QPalette: pass


class ModernPyMBOTheme:
    """Modern theme configuration for PyMBO GUI."""
    
    # Modern color palette
    COLORS = {
        # Primary colors
        'primary': '#2563eb',      # Blue
        'primary_dark': '#1d4ed8',
        'primary_light': '#3b82f6',
        
        # Secondary colors
        'secondary': '#64748b',    # Slate
        'secondary_dark': '#475569',
        'secondary_light': '#94a3b8',
        
        # Accent colors
        'accent': '#059669',       # Emerald
        'accent_light': '#10b981',
        'warning': '#f59e0b',      # Amber
        'error': '#dc2626',        # Red
        'success': '#059669',      # Emerald
        
        # Background colors
        'background': '#ffffff',    # White
        'background_secondary': '#f8fafc',  # Very light gray
        'background_tertiary': '#f1f5f9',   # Light gray
        'surface': '#ffffff',
        'card': '#ffffff',
        
        # Text colors
        'text_primary': '#0f172a',     # Very dark gray
        'text_secondary': '#475569',   # Medium gray
        'text_muted': '#64748b',       # Light gray
        'text_inverse': '#ffffff',
        
        # Border colors
        'border': '#e2e8f0',          # Light gray
        'border_focus': '#3b82f6',    # Blue
        'border_error': '#dc2626',    # Red
    }
    
    # Typography
    FONTS = {
        'heading_large': {'size': 18, 'weight': 'bold'},
        'heading_medium': {'size': 14, 'weight': 'bold'},
        'heading_small': {'size': 12, 'weight': 'bold'},
        'body': {'size': 10, 'weight': 'normal'},
        'caption': {'size': 9, 'weight': 'normal'},
        'button': {'size': 10, 'weight': 'medium'},
    }
    
    # Spacing system
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }
    
    # Component styles
    STYLES = {
        'border_radius': 8,
        'border_radius_small': 4,
        'shadow': '0 1px 3px rgba(0, 0, 0, 0.1)',
        'shadow_large': '0 4px 6px rgba(0, 0, 0, 0.1)',
    }


def get_modern_stylesheet() -> str:
    """Get complete modern stylesheet for PyMBO GUI."""
    theme = ModernPyMBOTheme()
    
    return f"""
    /* Main Window */
    QMainWindow {{
        background-color: {theme.COLORS['background']};
        color: {theme.COLORS['text_primary']};
        font-family: 'Segoe UI', 'Arial', sans-serif;
        font-size: 10pt;
    }}
    
    /* Widget Base */
    QWidget {{
        background-color: {theme.COLORS['background']};
        color: {theme.COLORS['text_primary']};
        selection-background-color: {theme.COLORS['primary_light']};
        selection-color: {theme.COLORS['text_inverse']};
    }}
    
    /* Group Boxes */
    QGroupBox {{
        font-weight: bold;
        font-size: 11pt;
        color: {theme.COLORS['text_primary']};
        border: 2px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        margin-top: 12px;
        padding-top: 8px;
        background-color: {theme.COLORS['card']};
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 4px 8px;
        background-color: {theme.COLORS['primary']};
        color: {theme.COLORS['text_inverse']};
        border-radius: 4px;
        margin-left: 8px;
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {theme.COLORS['primary']};
        color: {theme.COLORS['text_inverse']};
        border: none;
        border-radius: {theme.STYLES['border_radius']}px;
        padding: 8px 16px;
        font-weight: 500;
        font-size: 10pt;
        min-height: 32px;
    }}
    
    QPushButton:hover {{
        background-color: {theme.COLORS['primary_dark']};
    }}
    
    QPushButton:pressed {{
        background-color: {theme.COLORS['primary_dark']};
        transform: translateY(1px);
    }}
    
    QPushButton:disabled {{
        background-color: {theme.COLORS['secondary_light']};
        color: {theme.COLORS['text_muted']};
    }}
    
    /* Secondary Buttons */
    QPushButton.secondary {{
        background-color: {theme.COLORS['background_tertiary']};
        color: {theme.COLORS['text_primary']};
        border: 1px solid {theme.COLORS['border']};
    }}
    
    QPushButton.secondary:hover {{
        background-color: {theme.COLORS['background_secondary']};
        border-color: {theme.COLORS['border_focus']};
    }}
    
    /* Success Buttons */
    QPushButton.success {{
        background-color: {theme.COLORS['success']};
    }}
    
    QPushButton.success:hover {{
        background-color: {theme.COLORS['accent_light']};
    }}
    
    /* Warning Buttons */
    QPushButton.warning {{
        background-color: {theme.COLORS['warning']};
    }}
    
    /* Input Fields */
    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {theme.COLORS['surface']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius_small']}px;
        padding: 8px 12px;
        font-size: 10pt;
        color: {theme.COLORS['text_primary']};
        selection-background-color: {theme.COLORS['primary_light']};
    }}
    
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {theme.COLORS['border_focus']};
        outline: none;
    }}
    
    QLineEdit:disabled, QTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
        background-color: {theme.COLORS['background_tertiary']};
        color: {theme.COLORS['text_muted']};
        border-color: {theme.COLORS['border']};
    }}
    
    /* Combo Boxes */
    QComboBox {{
        background-color: {theme.COLORS['surface']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius_small']}px;
        padding: 8px 12px;
        font-size: 10pt;
        color: {theme.COLORS['text_primary']};
        min-height: 20px;
    }}
    
    QComboBox:focus {{
        border-color: {theme.COLORS['border_focus']};
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid {theme.COLORS['border']};
        border-radius: 0px;
        background-color: {theme.COLORS['background_secondary']};
    }}
    
    QComboBox::down-arrow {{
        width: 12px;
        height: 12px;
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSI+PHBhdGggZD0ibTMgNC41IDMgMyAzLTMiIHN0cm9rZT0iIzY0NzQ4YiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {theme.COLORS['surface']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius_small']}px;
        selection-background-color: {theme.COLORS['primary_light']};
        selection-color: {theme.COLORS['text_inverse']};
        outline: none;
    }}
    
    /* Check Boxes */
    QCheckBox {{
        color: {theme.COLORS['text_primary']};
        font-size: 10pt;
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: {theme.STYLES['border_radius_small']}px;
        border: 2px solid {theme.COLORS['border']};
        background-color: {theme.COLORS['surface']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {theme.COLORS['primary']};
        border-color: {theme.COLORS['primary']};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSI+PHBhdGggZD0ibTEwIDMtNiA2LTIuNS0yLjUiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz48L3N2Zz4=);
    }}
    
    QCheckBox::indicator:hover {{
        border-color: {theme.COLORS['border_focus']};
    }}
    
    /* Radio Buttons */
    QRadioButton {{
        color: {theme.COLORS['text_primary']};
        font-size: 10pt;
        spacing: 8px;
    }}
    
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 9px;
        border: 2px solid {theme.COLORS['border']};
        background-color: {theme.COLORS['surface']};
    }}
    
    QRadioButton::indicator:checked {{
        background-color: {theme.COLORS['primary']};
        border-color: {theme.COLORS['primary']};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSI+PGNpcmNsZSBjeD0iNiIgY3k9IjYiIHI9IjIiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4=);
    }}
    
    /* Progress Bars */
    QProgressBar {{
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        background-color: {theme.COLORS['background_tertiary']};
        height: 20px;
        text-align: center;
        color: {theme.COLORS['text_primary']};
        font-size: 9pt;
        font-weight: 500;
    }}
    
    QProgressBar::chunk {{
        background-color: {theme.COLORS['primary']};
        border-radius: {theme.STYLES['border_radius_small']}px;
        margin: 2px;
    }}
    
    /* Sliders */
    QSlider::groove:horizontal {{
        border: 1px solid {theme.COLORS['border']};
        height: 6px;
        background: {theme.COLORS['background_tertiary']};
        border-radius: 3px;
    }}
    
    QSlider::handle:horizontal {{
        background: {theme.COLORS['primary']};
        border: 2px solid {theme.COLORS['surface']};
        width: 20px;
        height: 20px;
        margin: -8px 0;
        border-radius: 10px;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {theme.COLORS['primary_dark']};
    }}
    
    /* Tab Widget */
    QTabWidget::pane {{
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        background-color: {theme.COLORS['card']};
        margin-top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {theme.COLORS['background_tertiary']};
        color: {theme.COLORS['text_secondary']};
        padding: 8px 16px;
        margin-right: 2px;
        border: 1px solid {theme.COLORS['border']};
        border-bottom: none;
        border-top-left-radius: {theme.STYLES['border_radius']}px;
        border-top-right-radius: {theme.STYLES['border_radius']}px;
        min-width: 80px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme.COLORS['primary']};
        color: {theme.COLORS['text_inverse']};
        border-color: {theme.COLORS['primary']};
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {theme.COLORS['background_secondary']};
        color: {theme.COLORS['text_primary']};
    }}
    
    /* Labels */
    QLabel {{
        color: {theme.COLORS['text_primary']};
        font-size: 10pt;
        background: transparent;
    }}
    
    QLabel.heading {{
        font-size: 14pt;
        font-weight: bold;
        color: {theme.COLORS['text_primary']};
        margin: 8px 0;
    }}
    
    QLabel.subheading {{
        font-size: 12pt;
        font-weight: 600;
        color: {theme.COLORS['text_secondary']};
        margin: 4px 0;
    }}
    
    QLabel.caption {{
        font-size: 9pt;
        color: {theme.COLORS['text_muted']};
    }}
    
    /* List Widget */
    QListWidget {{
        background-color: {theme.COLORS['surface']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        padding: 4px;
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 8px;
        border-radius: {theme.STYLES['border_radius_small']}px;
        margin-bottom: 2px;
    }}
    
    QListWidget::item:selected {{
        background-color: {theme.COLORS['primary']};
        color: {theme.COLORS['text_inverse']};
    }}
    
    QListWidget::item:hover {{
        background-color: {theme.COLORS['background_secondary']};
    }}
    
    /* Tree Widget */
    QTreeWidget {{
        background-color: {theme.COLORS['surface']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        outline: none;
        alternate-background-color: {theme.COLORS['background_secondary']};
    }}
    
    QTreeWidget::item {{
        padding: 4px 8px;
        border-bottom: 1px solid transparent;
    }}
    
    QTreeWidget::item:selected {{
        background-color: {theme.COLORS['primary']};
        color: {theme.COLORS['text_inverse']};
    }}
    
    QTreeWidget::item:hover {{
        background-color: {theme.COLORS['background_secondary']};
    }}
    
    QHeaderView::section {{
        background-color: {theme.COLORS['background_tertiary']};
        color: {theme.COLORS['text_primary']};
        padding: 8px;
        border: none;
        border-right: 1px solid {theme.COLORS['border']};
        font-weight: 600;
    }}
    
    /* Scroll Bars */
    QScrollBar:vertical {{
        background: {theme.COLORS['background_tertiary']};
        width: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:vertical {{
        background: {theme.COLORS['secondary_light']};
        border-radius: 6px;
        min-height: 20px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {theme.COLORS['secondary']};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    
    QScrollBar:horizontal {{
        background: {theme.COLORS['background_tertiary']};
        height: 12px;
        border-radius: 6px;
        margin: 0;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {theme.COLORS['secondary_light']};
        border-radius: 6px;
        min-width: 20px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {theme.COLORS['secondary']};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    
    /* Tool Tips */
    QToolTip {{
        background-color: {theme.COLORS['text_primary']};
        color: {theme.COLORS['text_inverse']};
        border: none;
        border-radius: {theme.STYLES['border_radius_small']}px;
        padding: 6px 8px;
        font-size: 9pt;
    }}
    
    /* Menu Bar */
    QMenuBar {{
        background-color: {theme.COLORS['background']};
        color: {theme.COLORS['text_primary']};
        border-bottom: 1px solid {theme.COLORS['border']};
    }}
    
    QMenuBar::item {{
        background: transparent;
        padding: 8px 12px;
    }}
    
    QMenuBar::item:selected {{
        background-color: {theme.COLORS['background_secondary']};
        border-radius: {theme.STYLES['border_radius_small']}px;
    }}
    
    QMenu {{
        background-color: {theme.COLORS['surface']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        padding: 4px;
    }}
    
    QMenu::item {{
        padding: 8px 12px;
        border-radius: {theme.STYLES['border_radius_small']}px;
    }}
    
    QMenu::item:selected {{
        background-color: {theme.COLORS['primary']};
        color: {theme.COLORS['text_inverse']};
    }}
    
    /* Status Bar */
    QStatusBar {{
        background-color: {theme.COLORS['background_secondary']};
        border-top: 1px solid {theme.COLORS['border']};
        color: {theme.COLORS['text_secondary']};
    }}
    
    /* Dock Widgets */
    QDockWidget {{
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
        font-weight: 600;
        color: {theme.COLORS['text_primary']};
    }}
    
    QDockWidget::title {{
        background-color: {theme.COLORS['background_tertiary']};
        border: 1px solid {theme.COLORS['border']};
        border-radius: {theme.STYLES['border_radius']}px;
        padding: 8px;
        text-align: center;
    }}
    
    /* Splitters */
    QSplitter::handle {{
        background-color: {theme.COLORS['border']};
        width: 2px;
        height: 2px;
    }}
    
    QSplitter::handle:hover {{
        background-color: {theme.COLORS['primary']};
    }}
    """


def apply_modern_theme(app: QApplication):
    """Apply modern theme to PyMBO application."""
    try:
        # Set application style
        app.setStyle('Fusion')
        
        # Apply stylesheet
        stylesheet = get_modern_stylesheet()
        app.setStyleSheet(stylesheet)
        
        # Set application font
        font = QFont("Segoe UI", 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        app.setFont(font)
        
        # Set color palette
        palette = QPalette()
        theme = ModernPyMBOTheme()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(theme.COLORS['background']))
        palette.setColor(QPalette.WindowText, QColor(theme.COLORS['text_primary']))
        
        # Base colors
        palette.setColor(QPalette.Base, QColor(theme.COLORS['surface']))
        palette.setColor(QPalette.AlternateBase, QColor(theme.COLORS['background_secondary']))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(theme.COLORS['text_primary']))
        palette.setColor(QPalette.BrightText, QColor(theme.COLORS['text_inverse']))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(theme.COLORS['primary']))
        palette.setColor(QPalette.ButtonText, QColor(theme.COLORS['text_inverse']))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(theme.COLORS['primary']))
        palette.setColor(QPalette.HighlightedText, QColor(theme.COLORS['text_inverse']))
        
        app.setPalette(palette)
        
        print("✅ Modern PyMBO theme applied successfully!")
        
    except Exception as e:
        print(f"❌ Error applying modern theme: {e}")


def create_enhanced_layout_widget(title: str = "", spacing: int = 16):
    """Create widget with enhanced modern layout."""
    try:
        theme = ModernPyMBOTheme()
        
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {theme.COLORS['card']};
                border: 1px solid {theme.COLORS['border']};
                border-radius: {theme.STYLES['border_radius']}px;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(spacing)
        layout.setContentsMargins(theme.SPACING['md'], theme.SPACING['md'], 
                                 theme.SPACING['md'], theme.SPACING['md'])
        
        if title:
            title_label = QLabel(title)
            title_label.setObjectName("heading")
            title_label.setStyleSheet(f"""
                QLabel#heading {{
                    font-size: 14pt;
                    font-weight: bold;
                    color: {theme.COLORS['text_primary']};
                    padding: {theme.SPACING['sm']}px 0;
                    border-bottom: 2px solid {theme.COLORS['primary']};
                    margin-bottom: {theme.SPACING['md']}px;
                }}
            """)
            layout.addWidget(title_label)
        
        return widget
    except NameError:
        # Qt not available, return None
        return None


def create_modern_button(text: str, button_type: str = "primary", icon: str = None):
    """Create modern styled button."""
    try:
        theme = ModernPyMBOTheme()
        
        button = QPushButton(text)
        
        if button_type == "secondary":
            button.setObjectName("secondary")
        elif button_type == "success":
            button.setObjectName("success")
        elif button_type == "warning":
            button.setObjectName("warning")
        
        # Add icon if provided
        if icon:
            button.setIcon(QIcon(icon))
            button.setIconSize(QSize(16, 16))
        
        return button
    except NameError:
        # Qt not available, return None
        return None


class EnhancedGroupBox:
    """Enhanced group box with modern styling."""
    
    def __init__(self, title: str = "", parent=None):
        try:
            self.group_box = QGroupBox(title, parent)
            self._setup_enhanced_style()
        except NameError:
            # Qt not available
            self.group_box = None
    
    def _setup_enhanced_style(self):
        """Setup enhanced styling."""
        if self.group_box is None:
            return
            
        theme = ModernPyMBOTheme()
        
        self.group_box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: 600;
                font-size: 11pt;
                color: {theme.COLORS['text_primary']};
                border: 2px solid {theme.COLORS['border']};
                border-radius: {theme.STYLES['border_radius']}px;
                margin-top: 16px;
                padding-top: 12px;
                background-color: {theme.COLORS['card']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 6px 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                                          stop:0 {theme.COLORS['primary']}, 
                                          stop:1 {theme.COLORS['primary_dark']});
                color: {theme.COLORS['text_inverse']};
                border-radius: 6px;
                margin-left: 12px;
                font-weight: 600;
            }}
        """)


def enhance_matplotlib_plots():
    """Apply modern styling to matplotlib plots."""
    import matplotlib.pyplot as plt
    import matplotlib as mpl
    
    # Set modern style
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Color palette
    theme = ModernPyMBOTheme()
    colors = [
        theme.COLORS['primary'],
        theme.COLORS['accent'],
        theme.COLORS['warning'],
        theme.COLORS['error'],
        theme.COLORS['secondary']
    ]
    
    # Apply custom rcParams
    mpl.rcParams.update({
        'figure.facecolor': theme.COLORS['background'],
        'axes.facecolor': theme.COLORS['surface'],
        'axes.edgecolor': theme.COLORS['border'],
        'axes.labelcolor': theme.COLORS['text_primary'],
        'axes.titlecolor': theme.COLORS['text_primary'],
        'text.color': theme.COLORS['text_primary'],
        'xtick.color': theme.COLORS['text_secondary'],
        'ytick.color': theme.COLORS['text_secondary'],
        'grid.color': theme.COLORS['border'],
        'axes.prop_cycle': mpl.cycler('color', colors),
        'font.family': 'sans-serif',
        'font.sans-serif': ['Segoe UI', 'Arial', 'DejaVu Sans'],
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 10,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,
        'figure.titlesize': 14,
    })
    
    print("Enhanced matplotlib styling applied successfully!")


# Utility functions for layout improvements
def add_stretch_spacer(layout, factor: int = 1):
    """Add stretch spacer to layout."""
    try:
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
    except NameError:
        # Qt not available
        pass


def create_horizontal_line():
    """Create horizontal separator line."""
    try:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line
    except NameError:
        # Qt not available
        return None


def create_vertical_line():
    """Create vertical separator line."""
    try:
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        return line
    except NameError:
        # Qt not available
        return None