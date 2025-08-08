"""
Configuration management for AE optimization.

This module handles loading, validation, and management of configuration
parameters for the AE optimization system.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Union

def get_project_root() -> Path:
    """Get the project root directory.
    
    When installed as a package, this should be the current working directory
    where the user is running the command from, not the package installation directory.
    """
    return Path.cwd()

class AEConfig:
    """Configuration class for Automated Ensemble optimization"""
    
    def __init__(self, project_root: Path = None):
        """Initialize with default directory paths and empty values for JSON loading"""
        if project_root is None:
            project_root = get_project_root()
            
        # Output configuration - use new structure
        self.OUTPUT_DIR: str = str(project_root / "outputs" / "runs")
        self.BEST_TRIAL_DIR: str = str(project_root / "outputs" / "best_trials")
        self.LOGS_DIR: str = str(project_root / "outputs" / "logs")
        self.VISUALIZATIONS_DIR: str = str(project_root / "outputs" / "visualizations")
        
        # Create all necessary directories automatically
        self._create_directories()
        
        # Initialize all other attributes that will be loaded from JSON
        self.SOFT_PREDICTION_THRESHOLD: float = None
        self.F1_THRESHOLD: float = 0.7  # Default value
        self.MIN_RECALL_THRESHOLD: float = None
        self.OPTIMIZATION_METRICS: str = "soft_recall"  # Default optimization metric
        self.BEST_TRIAL_FILE_SUFFIX: str = ""  # Optional suffix for best trial file names
        self.DATA_PATH: str = None
        self.HYPERPARAMETER_PATH: str = None
        self.FEATURES: List[str] = None
        self.LABEL_COLUMN: str = None
        self.CLASS_WEIGHT: Dict[int, int] = None
        self.UNDER_SAMPLE_MAJORITY_RATIO: int = None
        self.N_ENSEMBLE_GROUP_NUMBER: int = None
        self.AE_NUM_TRIALS: int = None
        self.NUM_SOBOL_TRIALS: int = None
        self.RANDOM_SEED: int = None
        self.PARALLEL_TRAINING: bool = None
        self.N_JOBS: int = None
        
        # Data preprocessing options
        self.ENABLE_DATA_IMPUTATION: bool = False  # Default: LightGBM handles nulls
        self.IMPUTE_TARGET_NULLS: bool = True      # Target nulls should still be handled
        
        # Threshold-based trial selection options
        self.SAVE_THRESHOLD_ENABLED: bool = False            # Enable threshold mode
        self.SAVE_THRESHOLD_METRIC: str = "soft_recall"      # Metric to threshold on
        self.SAVE_THRESHOLD_VALUE: float = 0.85              # Save trials >= this value
        self.FALLBACK_TOP_K: int = 5                         # Top-K fallback if no trials meet threshold
        self.FALLBACK_METRIC: str = "soft_recall"            # Metric for top-K ranking
    
    @classmethod
    def from_file(cls, config_path: str, project_root: Path = None) -> 'AEConfig':
        """Load configuration from JSON file"""
        try:
            if project_root is None:
                project_root = get_project_root()
                
            # If path is relative, make it relative to project root
            if not os.path.isabs(config_path):
                config_path = project_root / config_path
            
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            
            config = cls(project_root)
            for key, value in config_dict.items():
                if hasattr(config, key):
                    # Handle CLASS_WEIGHT dictionary conversion
                    if key == "CLASS_WEIGHT" and isinstance(value, dict):
                        # Convert string keys to int keys for CLASS_WEIGHT
                        value = {int(k): v for k, v in value.items()}
                    setattr(config, key, value)
                elif key.startswith('_'):
                    # Silently ignore metadata fields (starting with _)
                    pass
                else:
                    logging.warning(f"Unknown config parameter: {key}")
            
            # Validate that all required parameters are loaded
            config._validate_config()
            
            logging.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logging.error(f"Config file {config_path} not found. Cannot proceed without configuration.")
            raise
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing config file: {e}")
            raise
    
    def _validate_config(self) -> None:
        """Validate that all required configuration parameters are set"""
        required_params = [
            'SOFT_PREDICTION_THRESHOLD', 'MIN_RECALL_THRESHOLD',
            'DATA_PATH', 'FEATURES', 'LABEL_COLUMN',
            'CLASS_WEIGHT', 'UNDER_SAMPLE_MAJORITY_RATIO', 'N_ENSEMBLE_GROUP_NUMBER',
            'AE_NUM_TRIALS', 'NUM_SOBOL_TRIALS', 'RANDOM_SEED', 'PARALLEL_TRAINING', 'N_JOBS'
        ]
        
        missing_params = []
        for param in required_params:
            if getattr(self, param, None) is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValueError(f"Missing required configuration parameters: {missing_params}")
        
        # Validate optimization metric
        valid_metrics = [
            "soft_recall", "hard_recall", "soft_f1_score", "hard_f1_score", 
            "soft_precision", "hard_precision"
        ]
        if self.OPTIMIZATION_METRICS not in valid_metrics:
            raise ValueError(f"Invalid OPTIMIZATION_METRICS '{self.OPTIMIZATION_METRICS}'. "
                           f"Must be one of: {valid_metrics}")
    
    def save_to_file(self, config_path: str) -> None:
        """Save current configuration to JSON file"""
        # If path is relative, make it relative to project root
        if not os.path.isabs(config_path):
            config_path = get_project_root() / config_path
        
        config_dict = {
            attr: getattr(self, attr) 
            for attr in dir(self) 
            if not attr.startswith('_') and not callable(getattr(self, attr))
        }
        
        # Convert Path objects to strings for JSON serialization
        for key, value in config_dict.items():
            if isinstance(value, Path):
                config_dict[key] = str(value)
        
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=4)
        
        logging.info(f"Configuration saved to {config_path}")
    
    def _create_directories(self) -> None:
        """Create all necessary output directories"""
        directories_to_create = [
            self.OUTPUT_DIR,
            self.BEST_TRIAL_DIR, 
            self.LOGS_DIR,
            self.VISUALIZATIONS_DIR,
            # Also create the parent outputs directory
            str(Path(self.OUTPUT_DIR).parent)
        ]
        
        for dir_path in directories_to_create:
            try:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
                logging.debug(f"Created directory: {dir_path}")
            except Exception as e:
                logging.warning(f"Could not create directory {dir_path}: {e}")