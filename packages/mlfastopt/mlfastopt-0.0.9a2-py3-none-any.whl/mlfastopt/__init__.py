"""
MLFastOpt Package

A comprehensive ensemble optimization system using Meta's Ax platform for 
Bayesian hyperparameter optimization of LightGBM models.

Key Components:
- Core optimization engine (mlfastopt.core)
- Command-line interface (mlfastopt.cli)  
- Web visualization tools (mlfastopt.web)
- Utilities and helpers (mlfastopt.utils)
"""

import warnings
import logging

# Suppress SQLAlchemy warnings from ax-platform
warnings.filterwarnings("ignore", 
                       message=".*sqlalchemy version below 2.0.*")

# Suppress Ax parameter warnings 
warnings.filterwarnings("ignore", 
                       message=".*is not specified for.*ChoiceParameter.*")

# Also suppress at the logging level
logging.getLogger("ax.service.utils.with_db_settings_base").setLevel(logging.ERROR)

__version__ = "0.0.9a2"
__author__ = "MLFastOpt Development Team"

# Main imports for easy access
from mlfastopt.core.config import AEConfig
from mlfastopt.core.optimizer import AEModelTuner

__all__ = [
    "AEConfig",
    "AEModelTuner",
    "__version__"
]