#!/usr/bin/env python3
"""
Main CLI entry point for AE optimization.

This module provides the command-line interface for running AE optimization
with support for different environments and configuration overrides.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mlfastopt.core import AEModelTuner


def validate_config(config_path: str) -> bool:
    """Validate configuration and dataset without running optimization"""
    try:
        print("🔍 Validating configuration...")
        
        # Load and validate config
        tuner = AEModelTuner(config_path=config_path)
        print(f"✅ Configuration loaded successfully from {config_path}")
        
        # Check parameter space
        from pathlib import Path
        hyperparams_path = Path(tuner.config.HYPERPARAMETER_PATH)
        
        # If path is relative, resolve it relative to project root
        if not hyperparams_path.is_absolute():
            from mlfastopt.core.config import get_project_root
            project_root = get_project_root()
            hyperparams_path = project_root / hyperparams_path
            
        if not hyperparams_path.exists():
            print(f"❌ Parameter space file not found: {hyperparams_path}")
            return False
        print(f"✅ Parameter space configuration found: {hyperparams_path}")
        
        # Validate data loading
        print("🔍 Validating dataset...")
        data_processor = tuner.data_processor
        X, y, feature_cols = data_processor.load_and_preprocess_data()
        
        print(f"✅ Dataset loaded successfully:")
        print(f"   - Samples: {len(X)}")
        print(f"   - Features: {len(feature_cols)}")
        print(f"   - Class distribution: {y.value_counts().to_dict()}")
        
        # Check for potential issues
        if len(X) < 100:
            print("⚠️  Warning: Dataset is very small (< 100 samples)")
        
        if len(y.value_counts()) != 2:
            print("❌ Error: Target must be binary (0/1)")
            return False
        
        minority_class = min(y.value_counts().values)
        if minority_class < 10:
            print(f"⚠️  Warning: Minority class has very few samples ({minority_class})")
        
        print("✅ Configuration and dataset validation passed!")
        print("")
        print("💡 Ready to run optimization:")
        print(f"   OMP_NUM_THREADS=1 python -m mlfastopt.cli --config {config_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False


def main():
    """Main entry point for AE optimization CLI"""
    parser = argparse.ArgumentParser(description='AE Model Tuning - Modular Version')
    parser.add_argument('--config', type=str, help='Path to configuration JSON file')
    parser.add_argument('--environment', type=str, help='Environment configuration to use')
    parser.add_argument('--trials', type=int, help='Number of optimization trials')
    parser.add_argument('--ensemble-size', type=int, help='Number of models in ensemble')
    parser.add_argument('--random-seed', type=int, help='Random seed for reproducibility')
    parser.add_argument('--validate', action='store_true', help='Validate configuration and dataset without running optimization')
    
    args = parser.parse_args()
    
    try:
        # Determine config path
        config_path = None
        if args.config:
            config_path = args.config
        elif args.environment:
            config_path = f"config/environments/{args.environment}.json"
        else:
            config_path = "config/environments/default.json"
        
        # If validation requested, run validation and exit
        if args.validate:
            success = validate_config(config_path)
            exit(0 if success else 1)
        
        # Initialize tuner
        tuner = AEModelTuner(config_path=config_path)
        
        # Override config with command line arguments if provided
        if args.trials:
            tuner.config.AE_NUM_TRIALS = args.trials
            # Adjust NUM_SOBOL_TRIALS to be at most half of total trials
            tuner.config.NUM_SOBOL_TRIALS = min(tuner.config.NUM_SOBOL_TRIALS, max(1, args.trials // 2))
        if args.ensemble_size:
            tuner.config.N_ENSEMBLE_GROUP_NUMBER = args.ensemble_size
        if args.random_seed:
            tuner.config.RANDOM_SEED = args.random_seed
        
        # Run optimization
        results = tuner.run_complete_optimization()
        
        print(f"\n🎉 Optimization completed successfully!")
        print(f"📁 Results saved to: {results['output_dir']}")
        
        # Safe extraction for final results display
        def safe_extract_final(value):
            return float(value[0]) if isinstance(value, (tuple, list)) else float(value)
        
        best_metric_value = max([safe_extract_final(t['results'][tuner.config.OPTIMIZATION_METRICS]) for t in results['trial_results']])
        print(f"🏆 Best parameters found with {tuner.config.OPTIMIZATION_METRICS}: {best_metric_value:.4f}")
        
    except Exception as e:
        logging.error(f"Failed to complete optimization: {e}")
        raise


if __name__ == "__main__":
    main()