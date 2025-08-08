"""
Interactive web visualization for AE optimization results.

This module provides a Flask-based web application for real-time exploration
of optimization runs, comparison analysis, and result visualization.
"""

from .app import create_app, InteractiveVisualizer

__all__ = ["create_app", "InteractiveVisualizer"]