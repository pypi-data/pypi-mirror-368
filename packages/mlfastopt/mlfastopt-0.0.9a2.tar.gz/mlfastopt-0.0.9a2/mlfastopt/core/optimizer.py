"""
Optimization engine for AE using Meta's Ax platform.

This module contains the Bayesian optimization functionality and main orchestration
for hyperparameter tuning of LightGBM ensemble models using Meta's Ax platform 
with multi-objective optimization.

Classes:
    AxOptimizer: Bayesian optimization using Meta's Ax platform
    AEModelTuner: Main orchestration class for complete optimization pipeline

Functions:
    main: CLI entry point for running optimization
"""

import json
import logging
import os
import sys
import time
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import pandas as pd
import numpy as np

# Ax imports
from ax.service.ax_client import AxClient
from ax.modelbridge.registry import Generators

# Handle different Ax versions for ObjectiveProperties import
try:
    from ax.service.ax_client import ObjectiveProperties
except ImportError:
    try:
        from ax.core.objective import ObjectiveProperties
    except ImportError:
        # Create a simple fallback for older versions
        class ObjectiveProperties:
            def __init__(self, minimize=False, threshold=0.0):
                self.minimize = minimize
                self.threshold = threshold

# Handle different Ax versions for GenerationStrategy imports
try:
    from ax.generation_strategy.generation_strategy import GenerationStrategy, GenerationStep
except ImportError:
    try:
        from ax.generation.generation_strategy import GenerationStrategy, GenerationStep
    except ImportError:
        from ax.service.utils.best_point import get_best_parameters
        from ax.core.generation_strategy import GenerationStrategy, GenerationStep

# Local imports
from .config import AEConfig
from .data import DataProcessor
from .models import EnsembleModel, ModelEvaluator
from .output import OutputManager


def safe_float_extract(value):
    """Safely extract float from value that might be tuple (value, std_error)"""
    if isinstance(value, (int, float)):
        return float(value)
    elif isinstance(value, (tuple, list)) and len(value) > 0:
        return float(value[0])
    else:
        return 0.0


class AxOptimizer:
    """Handles Ax-based Bayesian optimization"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ax_client: Optional[AxClient] = None
        self.trial_results: List[Dict] = []
    
    def setup_optimization(self) -> AxClient:
        """Setup Ax client and experiment"""
        try:
            # Import parameter space from configurable path (REQUIRED)
            try:
                # Get the hyperparameter file path from config
                hyperparams_path = Path(self.config.HYPERPARAMETER_PATH)
                
                # If path is relative, resolve it relative to current working directory
                if not hyperparams_path.is_absolute():
                    hyperparams_path = Path.cwd() / hyperparams_path
                
                if not hyperparams_path.exists():
                    raise ImportError(f"Hyperparameter file not found at {hyperparams_path}")
                
                # Add the directory containing the hyperparameters file to Python path
                hyperparams_dir = str(hyperparams_path.parent)
                if hyperparams_dir not in sys.path:
                    sys.path.insert(0, hyperparams_dir)
                
                # Import the parameter space function from the specified file
                hyperparams_module = hyperparams_path.stem  # filename without extension
                exec(f"from {hyperparams_module} import get_parameter_space")
                parameters = locals()['get_parameter_space']()
                self.logger.info(f"Loaded parameter space with {len(parameters)} parameters from {hyperparams_path}")
                
            except ImportError as e:
                # No fallback - parameter space is required
                self.logger.error(f"Hyperparameter file is required but not found: {e}")
                raise ImportError(
                    f"Parameter space configuration is required. "
                    f"Please ensure {self.config.HYPERPARAMETER_PATH} exists and contains get_parameter_space() function. "
                    f"Original error: {e}"
                )
            
            # Setup generation strategy
            generation_strategy = GenerationStrategy(
                steps=[
                    GenerationStep(
                        model=Generators.SOBOL,
                        num_trials=self.config.NUM_SOBOL_TRIALS,
                        min_trials_observed=self.config.NUM_SOBOL_TRIALS,
                        max_parallelism=4,
                    ),
                    GenerationStep(
                        model=Generators.BOTORCH_MODULAR,
                        num_trials=self.config.AE_NUM_TRIALS - self.config.NUM_SOBOL_TRIALS,
                        max_parallelism=1,
                    ),
                ]
            )
            
            self.ax_client = AxClient(generation_strategy=generation_strategy)
            
            # Determine which metrics are tracked vs optimized
            all_metrics = [
                "soft_recall", "hard_recall", "soft_f1_score", "hard_f1_score", 
                "soft_precision", "hard_precision"
            ]
            
            # Remove the optimization metric from tracking metrics
            tracking_metrics = [m for m in all_metrics if m != self.config.OPTIMIZATION_METRICS]
            
            # Create single-objective experiment
            experiment = self.ax_client.create_experiment(
                name="ensemble_lightgbm_single_objective",
                parameters=parameters,
                objectives={
                    self.config.OPTIMIZATION_METRICS: ObjectiveProperties(minimize=False, threshold=0.0)
                },
                tracking_metric_names=tracking_metrics
            )
            
            self.logger.info("Ax optimization setup completed")
            return self.ax_client
            
        except Exception as e:
            self.logger.error(f"Error setting up optimization: {e}")
            raise
    
    
    def train_and_evaluate_trial(
        self, 
        parameters: Dict[str, Any], 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        ensemble_model: EnsembleModel,
        evaluator: ModelEvaluator
    ) -> Tuple[Dict[str, float], List]:
        """Train model and evaluate for a single trial"""
        try:
            # Train ensemble with given parameters
            models = ensemble_model.train_ensemble(X_train, y_train, parameters)
            
            # Evaluate model performance
            results = evaluator.evaluate_model(models, X_test, y_test, ensemble_model)
            
            return results, models
            
        except Exception as e:
            self.logger.error(f"Error in trial evaluation: {e}")
            return {
                "soft_recall": 0.0,
                "hard_recall": 0.0,
                "soft_f1_score": 0.0,
                "hard_f1_score": 0.0
            }, []
    
    def run_optimization(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        X_test: pd.DataFrame, 
        y_test: pd.Series
    ) -> Tuple[Dict[str, Any], List[Dict]]:
        """Run complete optimization process"""
        if not self.ax_client:
            self.setup_optimization()
        
        ensemble_model = EnsembleModel(self.config)
        evaluator = ModelEvaluator(self.config)
        
        # Start timing
        optimization_start_time = time.time()
        
        # Log optimization configuration
        self.logger.info(f"📊 OPTIMIZATION CONFIGURATION:")
        self.logger.info(f"   • Total trials: {self.config.AE_NUM_TRIALS}")
        self.logger.info(f"   • Sobol trials: {self.config.NUM_SOBOL_TRIALS}")
        self.logger.info(f"   • Bayesian trials: {self.config.AE_NUM_TRIALS - self.config.NUM_SOBOL_TRIALS}")
        self.logger.info(f"   • Ensemble size: {self.config.N_ENSEMBLE_GROUP_NUMBER} models per trial")
        self.logger.info(f"   • Total models to train: {self.config.AE_NUM_TRIALS * self.config.N_ENSEMBLE_GROUP_NUMBER:,}")
        self.logger.info(f"   • Random seed: {self.config.RANDOM_SEED}")
        self.logger.info(f"🚀 Starting optimization...")
        
        trial_results = []
        trial_times = []
        
        # Threshold-based trial selection
        qualifying_trials = []          # Trials meeting threshold
        all_trial_models = {}          # All models for potential saving
        threshold_met = False          # Track if any trials qualify
        
        # Legacy best trial tracking (for backward compatibility)
        best_recall = 0
        best_trial_idx = 0
        best_trial_models = None
        
        for i in range(self.config.AE_NUM_TRIALS):
            trial_start_time = time.time()
            try:
                # Get next trial parameters
                parameters, trial_index = self.ax_client.get_next_trial()
                
                # Train and evaluate
                results, trial_models = self.train_and_evaluate_trial(
                    parameters, X_train, y_train, X_test, y_test, 
                    ensemble_model, evaluator
                )
                
                # Complete trial
                self.ax_client.complete_trial(trial_index=trial_index, raw_data=results)
                
                # Calculate trial time
                trial_end_time = time.time()
                trial_duration = trial_end_time - trial_start_time
                trial_times.append(trial_duration)
                
                # Track results - safely extract float values from potential tuples
                def safe_float_extract(value):
                    """Safely extract float from value that might be tuple (value, std_error)"""
                    if isinstance(value, (int, float)):
                        return float(value)
                    elif isinstance(value, (tuple, list)) and len(value) > 0:
                        return float(value[0])
                    else:
                        return 0.0
                
                current_optimization_value = safe_float_extract(results[self.config.OPTIMIZATION_METRICS])
                
                # Store models for potential saving
                all_trial_models[i] = trial_models
                
                # Evaluate for threshold-based selection
                qualifies_for_saving = False
                if self.config.SAVE_THRESHOLD_ENABLED:
                    threshold_metric_value = safe_float_extract(results[self.config.SAVE_THRESHOLD_METRIC])
                    if threshold_metric_value >= self.config.SAVE_THRESHOLD_VALUE:
                        qualifies_for_saving = True
                        threshold_met = True
                
                # Legacy best trial tracking (for backward compatibility)
                is_best_trial = current_optimization_value > best_recall
                if is_best_trial:
                    best_recall = current_optimization_value
                    best_trial_idx = i
                    best_trial_models = trial_models
                
                trial_data = {
                    'trial': i + 1,
                    'trial_index': trial_index,
                    'parameters': parameters,
                    'results': results,
                    'is_best': is_best_trial,
                    'qualifies_for_saving': qualifies_for_saving,
                    'trial_duration_seconds': trial_duration
                }
                
                trial_results.append(trial_data)
                
                # Add to qualifying trials if it meets threshold
                if qualifies_for_saving:
                    qualifying_trials.append(trial_data)
                
                current_f1 = safe_float_extract(results['soft_f1_score'])
                self.logger.info(
                    f"Trial {i+1}/{self.config.AE_NUM_TRIALS}: "
                    f"Soft Recall={current_recall:.4f}, "
                    f"Soft F1={current_f1:.4f}, "
                    f"Duration={trial_duration:.1f}s"
                )
                
            except Exception as e:
                trial_end_time = time.time()
                trial_duration = trial_end_time - trial_start_time
                trial_times.append(trial_duration)
                
                self.logger.error(f"Error in trial {i+1}: {e}")
                # Complete failed trial with zero metrics
                try:
                    self.ax_client.complete_trial(trial_index=trial_index, raw_data={
                        "soft_recall": 0.0, "hard_recall": 0.0,
                        "soft_f1_score": 0.0, "hard_f1_score": 0.0
                    })
                except:
                    pass
        
        # Calculate timing statistics
        optimization_end_time = time.time()
        total_optimization_time = optimization_end_time - optimization_start_time
        avg_trial_time = sum(trial_times) / len(trial_times) if trial_times else 0
        
        # Select trials to save based on threshold or fallback logic
        trials_to_save, selection_reason = self._select_trials_to_save(
            trial_results, qualifying_trials, threshold_met, all_trial_models
        )
        
        # Legacy best trial logic (for backward compatibility)
        if not self.config.SAVE_THRESHOLD_ENABLED:
            self._update_best_trial_flags(trial_results, best_trial_idx)
            # Debug: Log summary of all trials
            self._log_trial_summary(trial_results)
        
        # Get best parameters - ensure consistency with trial tracking
        best_parameters = self.extract_best_parameters_from_trials(trial_results)
        
        # Log comprehensive completion summary
        self.logger.info(f"🎉 OPTIMIZATION COMPLETED!")
        self.logger.info(f"📊 FINAL RESULTS SUMMARY:")
        self.logger.info(f"   • Best {self.config.OPTIMIZATION_METRICS} achieved: {best_recall:.4f}")
        self.logger.info(f"   • Trials completed: {len(trial_results)}/{self.config.AE_NUM_TRIALS}")
        self.logger.info(f"   • Models trained: {len(trial_results) * self.config.N_ENSEMBLE_GROUP_NUMBER:,}")
        self.logger.info(f"   • Total optimization time: {total_optimization_time:.1f}s ({total_optimization_time/60:.1f}m)")
        self.logger.info(f"   • Average time per trial: {avg_trial_time:.1f}s")
        self.logger.info(f"   • Selection strategy: {selection_reason}")
        if trial_times:
            self.logger.info(f"   • Fastest trial: {min(trial_times):.1f}s")
            self.logger.info(f"   • Slowest trial: {max(trial_times):.1f}s")
        
        # Store timing information for later use
        self.timing_stats = {
            'total_optimization_time_seconds': total_optimization_time,
            'average_trial_time_seconds': avg_trial_time,
            'min_trial_time_seconds': min(trial_times) if trial_times else 0,
            'max_trial_time_seconds': max(trial_times) if trial_times else 0,
            'num_trials': len(trial_times)
        }
        
        self.trial_results = trial_results
        self.best_trial_models = best_trial_models  # Store for later use
        self.trials_to_save = trials_to_save        # Store trials to save
        self.selection_reason = selection_reason    # Store selection reason
        
        return best_parameters, trial_results
    
    def _select_trials_to_save(self, trial_results: List[Dict], qualifying_trials: List[Dict], 
                             threshold_met: bool, all_trial_models: Dict) -> Tuple[List[Dict], str]:
        """Select trials to save based on threshold or fallback logic"""
        if not self.config.SAVE_THRESHOLD_ENABLED:
            # Legacy mode - return single best trial
            best_trial = next((t for t in trial_results if t.get('is_best', False)), None)
            if best_trial:
                return [best_trial], "legacy_best_trial"
            else:
                return [], "no_best_trial"
        
        if threshold_met and len(qualifying_trials) > 0:
            # Threshold-based selection
            self.logger.info(f"Threshold mode: {self.config.SAVE_THRESHOLD_METRIC} >= {self.config.SAVE_THRESHOLD_VALUE}")
            self.logger.info(f"Found {len(qualifying_trials)} trials meeting threshold: {[t['trial'] for t in qualifying_trials]}")
            
            # Store models for all qualifying trials
            self.qualifying_trial_models = {}
            for trial in qualifying_trials:
                trial_idx = trial['trial'] - 1  # Convert to 0-based index
                if trial_idx in all_trial_models:
                    self.qualifying_trial_models[trial_idx] = all_trial_models[trial_idx]
            
            selection_reason = f"threshold_{self.config.SAVE_THRESHOLD_METRIC}_{self.config.SAVE_THRESHOLD_VALUE}"
            return qualifying_trials, selection_reason
        else:
            # Fallback to top-K
            self.logger.info(f"Threshold mode: {self.config.SAVE_THRESHOLD_METRIC} >= {self.config.SAVE_THRESHOLD_VALUE}")
            self.logger.info(f"No trials met threshold of {self.config.SAVE_THRESHOLD_VALUE}")
            self.logger.info(f"Falling back to top {self.config.FALLBACK_TOP_K} trials by {self.config.FALLBACK_METRIC}")
            
            # Sort all trials by fallback metric
            sorted_trials = sorted(trial_results, 
                                 key=lambda t: safe_float_extract(t['results'][self.config.FALLBACK_METRIC]), 
                                 reverse=True)
            
            top_k_trials = sorted_trials[:self.config.FALLBACK_TOP_K]
            
            # Log the top-K selection
            top_k_values = [safe_float_extract(t['results'][self.config.FALLBACK_METRIC]) for t in top_k_trials]
            self.logger.info(f"Saving top {len(top_k_trials)} trials: {[t['trial'] for t in top_k_trials]} "
                           f"with {self.config.FALLBACK_METRIC} scores {[f'{v:.4f}' for v in top_k_values]}")
            
            # Store models for top-K trials
            self.qualifying_trial_models = {}
            for trial in top_k_trials:
                trial_idx = trial['trial'] - 1  # Convert to 0-based index
                if trial_idx in all_trial_models:
                    self.qualifying_trial_models[trial_idx] = all_trial_models[trial_idx]
            
            selection_reason = f"top_{self.config.FALLBACK_TOP_K}_{self.config.FALLBACK_METRIC}"
            return top_k_trials, selection_reason
    
    def _update_best_trial_flags(self, trial_results: List[Dict], best_trial_idx: int) -> None:
        """Ensure only the final best trial is marked as 'is_best'"""
        try:
            # Clear all is_best flags first
            for trial in trial_results:
                trial['is_best'] = False
            
            # Mark only the final best trial
            if 0 <= best_trial_idx < len(trial_results):
                trial_results[best_trial_idx]['is_best'] = True
                best_recall = safe_float_extract(trial_results[best_trial_idx]['results'][self.config.OPTIMIZATION_METRICS])
                self.logger.info(f"Marked trial {best_trial_idx + 1} as best with {self.config.OPTIMIZATION_METRICS}: {best_recall:.4f}")
            else:
                self.logger.warning(f"Invalid best_trial_idx: {best_trial_idx}")
                
        except Exception as e:
            self.logger.error(f"Error updating best trial flags: {e}")
    
    def _log_trial_summary(self, trial_results: List[Dict]) -> None:
        """Log summary of all trials for debugging"""
        try:
            self.logger.info("=== TRIAL SUMMARY ===")
            best_trials = []
            for trial in trial_results:
                recall = safe_float_extract(trial['results']['soft_recall'])
                is_best = trial.get('is_best', False)
                trial_num = trial['trial']
                
                self.logger.info(f"Trial {trial_num}: Recall={recall:.4f}, is_best={is_best}")
                if is_best:
                    best_trials.append(trial_num)
            
            self.logger.info(f"Trials marked as best: {best_trials}")
            self.logger.info("=== END TRIAL SUMMARY ===")
            
        except Exception as e:
            self.logger.error(f"Error logging trial summary: {e}")
    
    def extract_best_parameters_from_trials(self, trial_results: List[Dict]) -> Dict[str, Any]:
        """Extract best parameters from trial results, ensuring consistency with trial tracking"""
        try:
            # Find the trial marked as best
            best_trial = None
            for trial in trial_results:
                if trial.get('is_best', False):
                    best_trial = trial
                    break
            
            if best_trial is not None:
                self.logger.info(
                    f"Using best trial {best_trial['trial']}: "
                    f"Recall={safe_float_extract(best_trial['results']['soft_recall']):.4f}, "
                    f"F1={safe_float_extract(best_trial['results']['soft_f1_score']):.4f}"
                )
                return best_trial['parameters']
            else:
                self.logger.warning("No trial marked as best, falling back to Pareto optimal selection")
                return self.extract_best_parameters()
                
        except Exception as e:
            self.logger.error(f"Error extracting best parameters from trials: {e}")
            return self.extract_best_parameters()
    
    def extract_best_parameters(self) -> Dict[str, Any]:
        """Extract best parameters from Pareto optimal solutions"""
        try:
            pareto_optimal = self.ax_client.get_pareto_optimal_parameters()
            
            valid_solutions = []
            for arm_name, arm_data in pareto_optimal.items():
                try:
                    if isinstance(arm_data, tuple) and len(arm_data) > 1:
                        parameters_dict = arm_data[0]
                        metrics_dict = arm_data[1][0] if isinstance(arm_data[1], tuple) else arm_data[1]
                        
                        if isinstance(parameters_dict, dict) and isinstance(metrics_dict, dict):
                            soft_recall = float(metrics_dict.get('soft_recall', 0.0))
                            soft_f1 = float(metrics_dict.get('soft_f1_score', 0.0))
                            
                            if soft_recall >= self.config.MIN_RECALL_THRESHOLD:
                                valid_solutions.append({
                                    'parameters': parameters_dict,
                                    'soft_recall': soft_recall,
                                    'soft_f1_score': soft_f1
                                })
                
                except Exception as e:
                    self.logger.warning(f"Error processing solution {arm_name}: {e}")
            
            if valid_solutions:
                # Select solution with highest F1 score among valid solutions
                best_solution = max(valid_solutions, key=lambda x: x['soft_f1_score'])
                self.logger.info(
                    f"Selected best solution: Recall={best_solution['soft_recall']:.4f}, "
                    f"F1={best_solution['soft_f1_score']:.4f}"
                )
                return best_solution['parameters']
            else:
                # Fallback to highest recall if no solution meets threshold
                self.logger.warning("No solution meets minimum recall threshold, using highest recall")
                all_solutions = []
                for arm_name, arm_data in pareto_optimal.items():
                    try:
                        if isinstance(arm_data, tuple) and len(arm_data) > 1:
                            parameters_dict = arm_data[0]
                            metrics_dict = arm_data[1][0] if isinstance(arm_data[1], tuple) else arm_data[1]
                            if isinstance(parameters_dict, dict) and isinstance(metrics_dict, dict):
                                all_solutions.append({
                                    'parameters': parameters_dict,
                                    'soft_recall': float(metrics_dict.get('soft_recall', 0.0))
                                })
                    except:
                        continue
                
                if all_solutions:
                    best_solution = max(all_solutions, key=lambda x: x['soft_recall'])
                    return best_solution['parameters']
                
            # Ultimate fallback - default parameters
            self.logger.warning("Using default parameters as fallback")
            return {
                "boosting_type": "gbdt", "num_leaves": 31, "max_depth": -1,
                "learning_rate": 0.1, "n_estimators": 100, "subsample_for_bin": 200000,
                "min_split_gain": 0.0, "min_child_weight": 0.001, "min_child_samples": 20,
                "subsample": 1.0, "subsample_freq": 0, "colsample_bytree": 1.0,
                "reg_alpha": 0.0, "reg_lambda": 0.0, "is_unbalance": False
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting best parameters: {e}")
            return {}


class AEModelTuner:
    """Main class that orchestrates the entire AE optimization process"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Use config/config.json as default if no path provided
        if config_path is None:
            config_path = "config/config.json"
        self.config = AEConfig.from_file(config_path)
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_processor = DataProcessor(self.config)
        self.optimizer = AxOptimizer(self.config)
        self.output_manager = OutputManager(self.config)
    
    def run_complete_optimization(self) -> Dict[str, Any]:
        """Run the complete optimization pipeline"""
        try:
            # Start overall timing
            pipeline_start_time = time.time()
            
            self.logger.info("=" * 60)
            self.logger.info("Starting AE Model Optimization")
            self.logger.info("=" * 60)
            
            # Step 1: Load and preprocess data
            step1_start = time.time()
            self.logger.info("Step 1: Loading and preprocessing data...")
            X, y, feature_names = self.data_processor.load_and_preprocess_data()
            X_train, X_test, y_train, y_test = self.data_processor.split_data(X, y)
            step1_duration = time.time() - step1_start
            
            # Step 2: Run optimization
            step2_start = time.time()
            self.logger.info("Step 2: Running Ax optimization...")
            best_parameters, trial_results = self.optimizer.run_optimization(
                X_train, y_train, X_test, y_test
            )
            step2_duration = time.time() - step2_start
            
            # Step 2.5: Calculate feature importance using best parameters
            step2_5_start = time.time()
            self.logger.info("Step 2.5: Calculating feature importance using best parameters...")
            feature_importance_data = self._calculate_final_feature_importance(
                best_parameters, X_train, y_train, X_test, y_test, feature_names
            )
            step2_5_duration = time.time() - step2_5_start
            
            # Step 3: Save results and generate outputs
            step3_start = time.time()
            self.logger.info("Step 3: Saving results and generating reports...")
            self.output_manager.save_results(best_parameters, trial_results, feature_names, self.optimizer)
            step3_duration = time.time() - step3_start
            
            # Step 3.5: Generate feature importance visualization
            step3_5_start = time.time()
            if feature_importance_data:
                self.logger.info("Step 3.5: Generating feature importance visualization...")
                self.output_manager.create_feature_importance_visualization(feature_importance_data)
            step3_5_duration = time.time() - step3_5_start
            
            # Calculate total pipeline time
            pipeline_end_time = time.time()
            total_pipeline_time = pipeline_end_time - pipeline_start_time
            
            # Clean up
            del self.optimizer.ax_client
            
            # Log timing summary
            self.logger.info("=" * 60)
            self.logger.info("TIMING SUMMARY")
            self.logger.info("=" * 60)
            self.logger.info(f"Step 1 (Data Loading): {step1_duration:.1f}s")
            self.logger.info(f"Step 2 (Optimization): {step2_duration:.1f}s ({step2_duration/60:.1f}m)")
            if hasattr(self.optimizer, 'timing_stats'):
                stats = self.optimizer.timing_stats
                self.logger.info(f"  - Average per trial: {stats['average_trial_time_seconds']:.1f}s")
                self.logger.info(f"  - Fastest trial: {stats['min_trial_time_seconds']:.1f}s")
                self.logger.info(f"  - Slowest trial: {stats['max_trial_time_seconds']:.1f}s")
            self.logger.info(f"Step 2.5 (Feature Importance): {step2_5_duration:.1f}s")
            self.logger.info(f"Step 3 (Results Saving): {step3_duration:.1f}s")
            self.logger.info(f"Step 3.5 (Visualization): {step3_5_duration:.1f}s")
            self.logger.info(f"TOTAL PIPELINE TIME: {total_pipeline_time:.1f}s ({total_pipeline_time/60:.1f}m)")
            self.logger.info("=" * 60)
            self.logger.info("AE Model Optimization Completed Successfully!")
            self.logger.info(f"Results saved to: {self.output_manager.output_dir}")
            self.logger.info("=" * 60)
            
            return {
                "best_parameters": best_parameters,
                "trial_results": trial_results,
                "output_dir": self.output_manager.output_dir,
                "feature_names": feature_names,
                "timing_stats": {
                    "total_pipeline_time_seconds": total_pipeline_time,
                    "step_1_duration_seconds": step1_duration,
                    "step_2_duration_seconds": step2_duration,
                    "step_2_5_duration_seconds": step2_5_duration,
                    "step_3_duration_seconds": step3_duration,
                    "step_3_5_duration_seconds": step3_5_duration,
                    "optimization_stats": getattr(self.optimizer, 'timing_stats', {})
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in optimization pipeline: {e}")
            raise
    
    def _calculate_final_feature_importance(
        self,
        best_parameters: Dict[str, Any],
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        feature_names: List[str]
    ) -> Dict[str, Any]:
        """Calculate feature importance using the best parameters from optimization"""
        try:
            # Use models from qualifying trials if threshold mode is enabled
            if (self.config.SAVE_THRESHOLD_ENABLED and 
                hasattr(self.optimizer, 'qualifying_trial_models') and 
                self.optimizer.qualifying_trial_models):
                self.logger.info("Using saved models from qualifying trials for feature importance calculation")
                # Use models from the first qualifying trial for feature importance
                # In the future, this could be enhanced to use all qualifying trial models
                first_qualifying_trial = next(iter(self.optimizer.qualifying_trial_models.values()))
                final_models = first_qualifying_trial
                ensemble_model = EnsembleModel(self.config)  # Still need this for calculate_feature_importance
            elif hasattr(self.optimizer, 'best_trial_models') and self.optimizer.best_trial_models:
                self.logger.info("Using saved models from best trial for feature importance calculation")
                final_models = self.optimizer.best_trial_models
                ensemble_model = EnsembleModel(self.config)  # Still need this for calculate_feature_importance
            else:
                self.logger.info("Retraining ensemble with best parameters for feature importance calculation")
                ensemble_model = EnsembleModel(self.config)
                final_models = ensemble_model.train_ensemble(X_train, y_train, best_parameters)
            
            if not final_models:
                self.logger.warning("No models available for feature importance calculation")
                return {}
            
            # Calculate comprehensive feature importance
            feature_importance_data = ensemble_model.calculate_feature_importance(
                models=final_models,
                X_test=X_test,
                y_test=y_test,
                feature_names=feature_names,
                n_repeats=5  # Reduced for faster computation
            )
            
            # Log key insights
            if feature_importance_data:
                top_lgb = feature_importance_data.get('top_lgb_features', [])
                top_perm = feature_importance_data.get('top_perm_features', [])
                consensus = feature_importance_data.get('consensus_features', [])
                
                self.logger.info(f"Top 5 LightGBM features: {top_lgb}")
                self.logger.info(f"Top 5 Permutation features: {top_perm}")
                if consensus:
                    self.logger.info(f"Consensus important features: {consensus}")
                else:
                    self.logger.info("No consensus features found between methods")
            
            return feature_importance_data
            
        except Exception as e:
            self.logger.error(f"Error calculating final feature importance: {e}")
            return {}


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AE Model Tuning - Clean Version')
    parser.add_argument('--config', type=str, help='Path to configuration JSON file')
    parser.add_argument('--trials', type=int, help='Number of optimization trials')
    parser.add_argument('--ensemble-size', type=int, help='Number of models in ensemble')
    parser.add_argument('--random-seed', type=int, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    try:
        # Initialize tuner
        tuner = AEModelTuner(config_path=args.config)
        
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