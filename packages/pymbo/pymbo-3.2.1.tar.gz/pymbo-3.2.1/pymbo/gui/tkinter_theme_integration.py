"""
Tkinter Theme Integration for PyMBO
==================================

This module provides modern theme integration for Tkinter-based PyMBO GUI,
addressing the display issues shown in the screenshot by applying professional
styling, improved color schemes, and enhanced visual hierarchy.

Key Improvements:
- Professional color palette with proper contrast
- Modern styling for Tkinter widgets
- Improved layout and spacing
- Enhanced typography and readability
- Cohesive visual design system

Author: Multi-Objective Optimization Laboratory
Version: 1.0.0 - Tkinter Theme Integration
"""

import tkinter as tk
from tkinter import ttk, font
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ModernTkinterTheme:
    """Modern theme configuration for Tkinter-based PyMBO GUI."""
    
    # Modern color palette - matches enhanced_gui_theme.py
    COLORS = {
        # Primary colors
        'primary': '#2563eb',         # Professional blue
        'primary_dark': '#1d4ed8',   
        'primary_light': '#3b82f6',
        
        # Secondary colors
        'secondary': '#64748b',       # Slate gray
        'secondary_dark': '#475569',
        'secondary_light': '#94a3b8',
        
        # Accent colors
        'accent': '#059669',          # Emerald green
        'accent_light': '#10b981',
        'warning': '#f59e0b',         # Amber
        'error': '#dc2626',           # Red
        'success': '#059669',         # Emerald
        
        # Background colors  
        'background': '#ffffff',      # White
        'background_secondary': '#f8fafc',  # Very light gray
        'background_tertiary': '#f1f5f9',   # Light gray
        'surface': '#ffffff',
        'card': '#ffffff',
        
        # Text colors
        'text_primary': '#0f172a',    # Very dark gray
        'text_secondary': '#475569',  # Medium gray
        'text_muted': '#64748b',      # Light gray
        'text_inverse': '#ffffff',
        
        # Border colors
        'border': '#e2e8f0',         # Light gray
        'border_focus': '#3b82f6',   # Blue
        'border_error': '#dc2626',   # Red
    }
    
    # Typography settings
    FONTS = {
        'default_family': 'Segoe UI',
        'fallback_families': ['Arial', 'Helvetica', 'sans-serif'],
        'heading_size': 12,
        'body_size': 10,
        'small_size': 9,
        'button_size': 10,
    }
    
    # Spacing system
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
    }


def get_system_font(family: str, size: int, weight: str = 'normal') -> font.Font:
    """Get system font with fallback support."""
    theme = ModernTkinterTheme()
    
    try:
        # Try primary font family
        test_font = font.Font(family=family, size=size, weight=weight)
        return test_font
    except tk.TclError:
        # Fall back to system defaults
        for fallback in theme.FONTS['fallback_families']:
            try:
                return font.Font(family=fallback, size=size, weight=weight)
            except tk.TclError:
                continue
        
        # Ultimate fallback
        return font.Font(size=size, weight=weight)


def configure_ttk_theme(root: tk.Tk) -> None:
    """Configure ttk theme with modern styling."""
    theme = ModernTkinterTheme()
    
    try:
        style = ttk.Style(root)
        
        # Set theme base
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        else:
            style.theme_use('default')
        
        logger.info(f"Using ttk theme: {style.theme_use()}")
        
        # Configure modern button style
        style.configure(
            'Modern.TButton',
            background=theme.COLORS['primary'],
            foreground=theme.COLORS['text_inverse'],
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(12, 8),
        )
        
        style.map(
            'Modern.TButton',
            background=[
                ('active', theme.COLORS['primary_dark']),
                ('pressed', theme.COLORS['primary_dark']),
                ('disabled', theme.COLORS['secondary_light'])
            ],
            foreground=[
                ('disabled', theme.COLORS['text_muted'])
            ]
        )
        
        # Configure modern entry style  
        style.configure(
            'Modern.TEntry',
            fieldbackground=theme.COLORS['surface'],
            borderwidth=1,
            insertcolor=theme.COLORS['text_primary'],
            relief='solid',
            padding=(8, 6),
        )
        
        style.map(
            'Modern.TEntry',
            bordercolor=[
                ('focus', theme.COLORS['border_focus']),
                ('!focus', theme.COLORS['border'])
            ],
            lightcolor=[
                ('focus', theme.COLORS['border_focus']),
                ('!focus', theme.COLORS['border'])
            ],
            darkcolor=[
                ('focus', theme.COLORS['border_focus']),
                ('!focus', theme.COLORS['border'])
            ]
        )
        
        # Configure modern frame style
        style.configure(
            'Modern.TFrame',
            background=theme.COLORS['background'],
            borderwidth=1,
            relief='solid',
        )
        
        style.configure(
            'Card.TFrame',
            background=theme.COLORS['card'],
            borderwidth=1,
            relief='solid',
        )
        
        # Configure modern label style
        style.configure(
            'Modern.TLabel',
            background=theme.COLORS['background'],
            foreground=theme.COLORS['text_primary'],
        )
        
        style.configure(
            'Heading.TLabel',
            background=theme.COLORS['background'],
            foreground=theme.COLORS['text_primary'],
            font=('Segoe UI', 12, 'bold'),
        )
        
        style.configure(
            'Secondary.TLabel',
            background=theme.COLORS['background'],
            foreground=theme.COLORS['text_secondary'],
        )
        
        # Configure modern combobox style
        style.configure(
            'Modern.TCombobox',
            fieldbackground=theme.COLORS['surface'],
            borderwidth=1,
            relief='solid',
        )
        
        # Configure modern checkbutton style
        style.configure(
            'Modern.TCheckbutton',
            background=theme.COLORS['background'],
            foreground=theme.COLORS['text_primary'],
            focuscolor='none',
        )
        
        # Configure modern notebook style
        style.configure(
            'Modern.TNotebook',
            background=theme.COLORS['background'],
            borderwidth=1,
        )
        
        style.configure(
            'Modern.TNotebook.Tab',
            background=theme.COLORS['background_tertiary'],
            foreground=theme.COLORS['text_secondary'],
            padding=(12, 6),
            borderwidth=1,
        )
        
        style.map(
            'Modern.TNotebook.Tab',
            background=[
                ('selected', theme.COLORS['primary']),
                ('active', theme.COLORS['background_secondary'])
            ],
            foreground=[
                ('selected', theme.COLORS['text_inverse']),
                ('active', theme.COLORS['text_primary'])
            ]
        )
        
        logger.info("✓ TTK modern theme configured successfully")
        
    except Exception as e:
        logger.error(f"Error configuring TTK theme: {e}")


def apply_modern_tkinter_theme(root: tk.Tk) -> None:
    """Apply comprehensive modern theme to Tkinter application."""
    theme = ModernTkinterTheme()
    
    try:
        # Configure main window
        root.configure(bg=theme.COLORS['background'])
        
        # Configure TTK theme
        configure_ttk_theme(root)
        
        # Set default fonts
        default_font = get_system_font(
            theme.FONTS['default_family'], 
            theme.FONTS['body_size']
        )
        
        heading_font = get_system_font(
            theme.FONTS['default_family'], 
            theme.FONTS['heading_size'], 
            'bold'
        )
        
        small_font = get_system_font(
            theme.FONTS['default_family'], 
            theme.FONTS['small_size']
        )
        
        # Configure default fonts
        root.option_add('*Font', default_font)
        root.option_add('*Background', theme.COLORS['background'])
        root.option_add('*Foreground', theme.COLORS['text_primary'])
        
        # Configure specific widget defaults
        root.option_add('*Button.Background', theme.COLORS['primary'])
        root.option_add('*Button.Foreground', theme.COLORS['text_inverse'])
        root.option_add('*Button.activeBackground', theme.COLORS['primary_dark'])
        root.option_add('*Button.Relief', 'flat')
        root.option_add('*Button.BorderWidth', '0')
        
        root.option_add('*Entry.Background', theme.COLORS['surface'])
        root.option_add('*Entry.Foreground', theme.COLORS['text_primary'])
        root.option_add('*Entry.insertBackground', theme.COLORS['text_primary'])
        root.option_add('*Entry.Relief', 'solid')
        root.option_add('*Entry.BorderWidth', '1')
        
        root.option_add('*Text.Background', theme.COLORS['surface'])
        root.option_add('*Text.Foreground', theme.COLORS['text_primary'])
        root.option_add('*Text.insertBackground', theme.COLORS['text_primary'])
        root.option_add('*Text.Relief', 'solid')
        root.option_add('*Text.BorderWidth', '1')
        
        root.option_add('*Listbox.Background', theme.COLORS['surface'])
        root.option_add('*Listbox.Foreground', theme.COLORS['text_primary'])
        root.option_add('*Listbox.selectBackground', theme.COLORS['primary_light'])
        root.option_add('*Listbox.selectForeground', theme.COLORS['text_inverse'])
        
        # Configure frame defaults
        root.option_add('*Frame.Background', theme.COLORS['background'])
        root.option_add('*LabelFrame.Background', theme.COLORS['card'])
        root.option_add('*LabelFrame.Foreground', theme.COLORS['text_primary'])
        
        logger.info("✓ Modern Tkinter theme applied successfully")
        
    except Exception as e:
        logger.error(f"Error applying Tkinter theme: {e}")


def enhance_widget_styling(widget: tk.Widget, style_type: str = "default") -> None:
    """Apply enhanced styling to individual widgets."""
    theme = ModernTkinterTheme()
    
    try:
        if isinstance(widget, tk.Button):
            if style_type == "primary":
                widget.configure(
                    bg=theme.COLORS['primary'],
                    fg=theme.COLORS['text_inverse'],
                    activebackground=theme.COLORS['primary_dark'],
                    relief='flat',
                    bd=0,
                    padx=12,
                    pady=8,
                    font=get_system_font(
                        theme.FONTS['default_family'], 
                        theme.FONTS['button_size'], 
                        'normal'
                    )
                )
            elif style_type == "secondary":
                widget.configure(
                    bg=theme.COLORS['background_tertiary'],
                    fg=theme.COLORS['text_primary'],
                    activebackground=theme.COLORS['background_secondary'],
                    relief='solid',
                    bd=1,
                    padx=12,
                    pady=8
                )
            elif style_type == "success":
                widget.configure(
                    bg=theme.COLORS['success'],
                    fg=theme.COLORS['text_inverse'],
                    activebackground=theme.COLORS['accent_light'],
                    relief='flat',
                    bd=0,
                    padx=12,
                    pady=8
                )
                
        elif isinstance(widget, tk.Label):
            if style_type == "heading":
                widget.configure(
                    bg=theme.COLORS['background'],
                    fg=theme.COLORS['text_primary'],
                    font=get_system_font(
                        theme.FONTS['default_family'], 
                        theme.FONTS['heading_size'], 
                        'bold'
                    )
                )
            elif style_type == "secondary":
                widget.configure(
                    bg=theme.COLORS['background'],
                    fg=theme.COLORS['text_secondary'],
                )
                
        elif isinstance(widget, (tk.Entry, tk.Text)):
            widget.configure(
                bg=theme.COLORS['surface'],
                fg=theme.COLORS['text_primary'],
                insertbackground=theme.COLORS['text_primary'],
                relief='solid',
                bd=1,
                highlightthickness=1,
                highlightcolor=theme.COLORS['border_focus'],
                highlightbackground=theme.COLORS['border']
            )
            
        elif isinstance(widget, tk.Frame):
            if style_type == "card":
                widget.configure(
                    bg=theme.COLORS['card'],
                    relief='solid',
                    bd=1
                )
            else:
                widget.configure(bg=theme.COLORS['background'])
                
        elif isinstance(widget, tk.LabelFrame):
            widget.configure(
                bg=theme.COLORS['card'],
                fg=theme.COLORS['text_primary'],
                relief='solid',
                bd=1,
                font=get_system_font(
                    theme.FONTS['default_family'], 
                    theme.FONTS['body_size'], 
                    'bold'
                )
            )
            
    except Exception as e:
        logger.warning(f"Error enhancing widget styling: {e}")


def apply_theme_recursively(parent: tk.Widget, style_map: Dict[str, str] = None) -> None:
    """Apply modern theme to all child widgets recursively."""
    if style_map is None:
        style_map = {}
        
    try:
        # Apply theme to current widget
        widget_class = parent.__class__.__name__
        style_type = style_map.get(widget_class, "default")
        enhance_widget_styling(parent, style_type)
        
        # Apply to all children
        for child in parent.winfo_children():
            apply_theme_recursively(child, style_map)
            
    except Exception as e:
        logger.warning(f"Error in recursive theme application: {e}")


# Convenience functions for common styling patterns
def create_modern_button(parent: tk.Widget, text: str, command: callable = None, 
                        style: str = "primary") -> tk.Button:
    """Create a button with modern styling."""
    button = tk.Button(parent, text=text, command=command)
    enhance_widget_styling(button, style)
    return button


def create_modern_label(parent: tk.Widget, text: str, style: str = "default") -> tk.Label:
    """Create a label with modern styling."""
    label = tk.Label(parent, text=text)
    enhance_widget_styling(label, style)
    return label


def create_modern_entry(parent: tk.Widget, **kwargs) -> tk.Entry:
    """Create an entry with modern styling."""
    entry = tk.Entry(parent, **kwargs)
    enhance_widget_styling(entry)
    return entry


def create_modern_frame(parent: tk.Widget, style: str = "default", **kwargs) -> tk.Frame:
    """Create a frame with modern styling."""
    frame = tk.Frame(parent, **kwargs)
    enhance_widget_styling(frame, style)
    return frame


def create_modern_labelframe(parent: tk.Widget, text: str, **kwargs) -> tk.LabelFrame:
    """Create a labelframe with modern styling."""
    labelframe = tk.LabelFrame(parent, text=text, **kwargs)
    enhance_widget_styling(labelframe)
    return labelframe


# Export main function
__all__ = [
    'apply_modern_tkinter_theme',
    'enhance_widget_styling', 
    'apply_theme_recursively',
    'create_modern_button',
    'create_modern_label',
    'create_modern_entry',
    'create_modern_frame',
    'create_modern_labelframe',
    'ModernTkinterTheme'
]