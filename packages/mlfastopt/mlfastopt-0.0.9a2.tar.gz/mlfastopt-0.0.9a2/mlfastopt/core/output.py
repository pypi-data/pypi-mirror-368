"""
Output management and visualization for AE optimization.

This module handles results saving, visualization generation, and reporting.
"""

import json
import logging
import os
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt

from .config import AEConfig


class OutputManager:
    """Handles output generation, visualization and saving results"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = self._create_output_directory()
    
    def _create_output_directory(self) -> str:
        """Create timestamped output directory within src/outputs/"""
        # Get the directory structure from config
        outputs_dir = Path(self.config.OUTPUT_DIR)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = outputs_dir / f"run_{timestamp}"
        output_dir.mkdir(exist_ok=True)
        self.logger.info(f"Output directory created: {output_dir}")
        return str(output_dir)
    
    def _safe_extract_float(self, value):
        """Safely extract float from value that might be tuple (value, std_error)"""
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, (tuple, list)) and len(value) > 0:
            return float(value[0])
        else:
            return 0.0
    
    def _get_best_trial_file_suffix(self) -> str:
        """Get best trial file suffix from config or auto-extract from DATA_PATH"""
        if self.config.BEST_TRIAL_FILE_SUFFIX:
            return self.config.BEST_TRIAL_FILE_SUFFIX
        else:
            # Extract filename from DATA_PATH: "data/titanic.csv" → "titanic"
            data_path = Path(self.config.DATA_PATH)
            return data_path.stem  # Gets filename without extension
    
    def save_results(
        self, 
        best_parameters: Dict[str, Any], 
        trial_results: List[Dict],
        feature_names: List[str],
        optimizer=None
    ) -> None:
        """Save optimization results and generate reports"""
        try:
            # Save qualifying trials (new threshold-based approach)
            if optimizer and hasattr(optimizer, 'trials_to_save') and self.config.SAVE_THRESHOLD_ENABLED:
                self._save_qualifying_trials(optimizer.trials_to_save, optimizer.selection_reason, trial_results)
            else:
                # Legacy: Save best parameters
                self._save_best_parameters(best_parameters, trial_results)
            
            # Create optimization plots
            self._create_optimization_plots(trial_results)
            
            # Save configuration
            config_path = os.path.join(self.output_dir, 'config.json')
            self.config.save_to_file(config_path)
            
            # Generate summary report
            self._generate_summary_report(best_parameters, trial_results, feature_names)
            
            self.logger.info(f"All results saved to {self.output_dir}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
    
    def _save_best_parameters(
        self, 
        best_parameters: Dict[str, Any], 
        trial_results: List[Dict]
    ) -> None:
        """Save best parameters to JSON files"""
        # Save to output directory
        params_file = os.path.join(self.output_dir, 'best_parameters.json')
        
        best_metrics = None
        best_trial = None
        
        # First try to find trial marked as best
        for trial in trial_results:
            if trial.get('is_best', False):
                best_metrics = trial['results']
                best_trial = trial
                break
        
        # Fallback: find trial with highest recall if no trial is marked as best
        if best_metrics is None:
            self.logger.warning("No trial marked as 'is_best', finding trial with highest recall")
            best_recall = -1
            for trial in trial_results:
                current_recall = self._safe_extract_float(trial['results']['soft_recall'])
                if current_recall > best_recall:
                    best_recall = current_recall
                    best_metrics = trial['results']
                    best_trial = trial
            
            if best_trial:
                self.logger.info(f"Found best trial by recall: {best_recall:.4f} (Trial {best_trial['trial']})")
        else:
            best_recall = self._safe_extract_float(best_metrics['soft_recall'])
            self.logger.info(f"Using trial marked as best: recall={best_recall:.4f} (Trial {best_trial['trial']})")
        
        # Validate we found the best trial
        if best_metrics is None:
            self.logger.error("Could not find any trial for best parameters - this should not happen!")
            raise RuntimeError("No best trial found")
        
        # Calculate timing statistics from trial results
        trial_times = [t.get('trial_duration_seconds', 0) for t in trial_results if 'trial_duration_seconds' in t]
        timing_stats = {}
        if trial_times:
            timing_stats = {
                "average_trial_time_seconds": sum(trial_times) / len(trial_times),
                "min_trial_time_seconds": min(trial_times),
                "max_trial_time_seconds": max(trial_times),
                "total_trial_time_seconds": sum(trial_times)
            }
        
        results_dict = {
            "parameters": best_parameters,
            "metrics": best_metrics,
            "timestamp": datetime.datetime.now().isoformat(),
            "config": {
                "AE_NUM_TRIALS": self.config.AE_NUM_TRIALS,
                "N_ENSEMBLE_GROUP_NUMBER": self.config.N_ENSEMBLE_GROUP_NUMBER,
                "MIN_RECALL_THRESHOLD": self.config.MIN_RECALL_THRESHOLD,
                "PARALLEL_TRAINING": self.config.PARALLEL_TRAINING
            },
            "trial_results_summary": {
                "total_trials": len(trial_results),
                "successful_trials": len([t for t in trial_results if self._safe_extract_float(t['results']['soft_recall']) > 0])
            },
            "timing_stats": timing_stats
        }
        
        with open(params_file, 'w') as f:
            json.dump(results_dict, f, indent=4)
        
        # Save to best_trial directory for compatibility  
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        appendix = self._get_best_trial_file_suffix()
        best_trial_dir = Path(self.config.BEST_TRIAL_DIR)
        best_trial_file = best_trial_dir / f"{date_str}_{appendix}.json"
        
        # Load existing data if file exists
        existing_data = []
        if os.path.exists(best_trial_file):
            try:
                with open(best_trial_file, 'r') as f:
                    existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = [existing_data]
            except json.JSONDecodeError:
                existing_data = []
        
        existing_data.append(results_dict)
        
        with open(best_trial_file, 'w') as f:
            json.dump(existing_data, f, indent=4)
        
        self.logger.info(f"Best parameters saved to {params_file} and {best_trial_file}")
    
    def _save_qualifying_trials(
        self, 
        trials_to_save: List[Dict], 
        selection_reason: str, 
        all_trial_results: List[Dict]
    ) -> None:
        """Save multiple qualifying trials to a single consolidated file"""
        try:
            self.logger.info(f"Saving {len(trials_to_save)} qualifying trials using strategy: {selection_reason}")
            
            # Create consolidated data structure
            consolidated_data = {
                "selection_strategy": selection_reason,
                "num_trials_saved": len(trials_to_save),
                "threshold_config": {
                    "enabled": self.config.SAVE_THRESHOLD_ENABLED,
                    "metric": self.config.SAVE_THRESHOLD_METRIC,
                    "threshold": self.config.SAVE_THRESHOLD_VALUE,
                    "fallback_top_k": self.config.FALLBACK_TOP_K,
                    "fallback_metric": self.config.FALLBACK_METRIC
                },
                "qualifying_trials": [],
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            # Add each qualifying trial to the consolidated structure
            for trial in trials_to_save:
                trial_data = {
                    "trial_number": trial['trial'],
                    "trial_index": trial['trial_index'],
                    "parameters": trial['parameters'],
                    "results": trial['results'],
                    "trial_duration_seconds": trial.get('trial_duration_seconds', 0),
                    "qualifies_for_saving": trial.get('qualifies_for_saving', False),
                    "selection_reason": selection_reason,
                    "metrics_summary": {
                        "soft_recall": self._safe_extract_float(trial['results']['soft_recall']),
                        "soft_f1_score": self._safe_extract_float(trial['results']['soft_f1_score']),
                        "soft_precision": self._safe_extract_float(trial['results']['soft_precision']),
                        "hard_recall": self._safe_extract_float(trial['results'].get('hard_recall', 0)),
                        "hard_f1_score": self._safe_extract_float(trial['results'].get('hard_f1_score', 0)),
                        "hard_precision": self._safe_extract_float(trial['results'].get('hard_precision', 0))
                    }
                }
                consolidated_data["qualifying_trials"].append(trial_data)
            
            # Save consolidated file
            consolidated_file = os.path.join(self.output_dir, f"qualifying_trials_{selection_reason}.json")
            with open(consolidated_file, 'w') as f:
                json.dump(consolidated_data, f, indent=4)
            
            # Also save to best_trials directory for compatibility
            self._save_to_best_trials_directory(trials_to_save, selection_reason)
            
            self.logger.info(f"Saved {len(trials_to_save)} qualifying trials to {consolidated_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving qualifying trials: {e}")
    
    def _save_to_best_trials_directory(self, trials_to_save: List[Dict], selection_reason: str) -> None:
        """Save qualifying trials to best_trials directory for compatibility"""
        try:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            appendix = self._get_best_trial_file_suffix()
            best_trial_dir = Path(self.config.BEST_TRIAL_DIR)
            best_trial_file = best_trial_dir / f"{date_str}_{appendix}_{selection_reason}.json"
            
            # Load existing data if file exists
            existing_data = []
            if os.path.exists(best_trial_file):
                try:
                    with open(best_trial_file, 'r') as f:
                        existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    existing_data = []
            
            # Add all qualifying trials
            for trial in trials_to_save:
                trial_entry = {
                    "parameters": trial['parameters'],
                    "metrics": trial['results'],
                    "trial_number": trial['trial'],
                    "selection_reason": selection_reason,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                existing_data.append(trial_entry)
            
            # Save to best_trials directory
            with open(best_trial_file, 'w') as f:
                json.dump(existing_data, f, indent=4)
            
            self.logger.info(f"Qualifying trials also saved to {best_trial_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving to best_trials directory: {e}")
    
    def _create_optimization_plots(self, trial_results: List[Dict]) -> None:
        """Create optimization progress plots"""
        try:
            if not trial_results:
                return
            
            trials = [t['trial'] for t in trial_results]
            soft_recalls = [self._safe_extract_float(t['results']['soft_recall']) for t in trial_results]
            soft_f1s = [self._safe_extract_float(t['results']['soft_f1_score']) for t in trial_results]
            soft_precisions = [self._safe_extract_float(t['results']['soft_precision']) for t in trial_results]
            
            # Find best trials
            best_recall_idx = soft_recalls.index(max(soft_recalls))
            best_f1_idx = soft_f1s.index(max(soft_f1s))
            best_precision_idx = soft_precisions.index(max(soft_precisions))
            
            plt.figure(figsize=(18, 12))
            
            # Plot soft recall progress
            plt.subplot(2, 3, 1)
            plt.plot(trials, soft_recalls, 'b-o', linewidth=2, markersize=4, label='Soft Recall')
            plt.scatter(trials[best_recall_idx], soft_recalls[best_recall_idx], 
                       color='red', s=100, marker='*', label=f'Best ({trials[best_recall_idx]})', zorder=5)
            plt.axvline(x=self.config.NUM_SOBOL_TRIALS, color='gray', linestyle='--', 
                       alpha=0.7, label='Sobol → BO')
            plt.xlabel('Trial Number')
            plt.ylabel('Soft Recall')
            plt.title('Optimization Progress - Soft Recall')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Plot soft F1 score progress
            plt.subplot(2, 3, 2)
            plt.plot(trials, soft_f1s, 'g-o', linewidth=2, markersize=4, label='Soft F1')
            plt.scatter(trials[best_f1_idx], soft_f1s[best_f1_idx], 
                       color='red', s=100, marker='*', label=f'Best ({trials[best_f1_idx]})', zorder=5)
            plt.axvline(x=self.config.NUM_SOBOL_TRIALS, color='gray', linestyle='--', 
                       alpha=0.7, label='Sobol → BO')
            plt.xlabel('Trial Number')
            plt.ylabel('Soft F1 Score')
            plt.title('Optimization Progress - Soft F1 Score')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Plot soft precision progress
            plt.subplot(2, 3, 3)
            plt.plot(trials, soft_precisions, 'm-o', linewidth=2, markersize=4, label='Soft Precision')
            plt.scatter(trials[best_precision_idx], soft_precisions[best_precision_idx], 
                       color='red', s=100, marker='*', label=f'Best ({trials[best_precision_idx]})', zorder=5)
            plt.axvline(x=self.config.NUM_SOBOL_TRIALS, color='gray', linestyle='--', 
                       alpha=0.7, label='Sobol → BO')
            plt.xlabel('Trial Number')
            plt.ylabel('Soft Precision')
            plt.title('Optimization Progress - Soft Precision')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Scatter plot: Recall vs F1
            plt.subplot(2, 3, 4)
            plt.scatter(soft_recalls, soft_f1s, c=trials, cmap='viridis', alpha=0.7)
            plt.scatter(soft_recalls[best_recall_idx], soft_f1s[best_recall_idx], 
                       color='red', s=100, marker='*', label='Best Recall', zorder=5)
            plt.scatter(soft_recalls[best_f1_idx], soft_f1s[best_f1_idx], 
                       color='orange', s=100, marker='*', label='Best F1', zorder=5)
            plt.scatter(soft_recalls[best_precision_idx], soft_f1s[best_precision_idx], 
                       color='magenta', s=100, marker='*', label='Best Precision', zorder=5)
            plt.xlabel('Soft Recall')
            plt.ylabel('Soft F1 Score')
            plt.title('Recall vs F1 Score Trade-off')
            plt.colorbar(label='Trial Number')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Precision vs Recall plot
            plt.subplot(2, 3, 5)
            plt.scatter(soft_recalls, soft_precisions, c=trials, cmap='plasma', alpha=0.7)
            plt.scatter(soft_recalls[best_recall_idx], soft_precisions[best_recall_idx], 
                       color='red', s=100, marker='*', label='Best Recall', zorder=5)
            plt.scatter(soft_recalls[best_precision_idx], soft_precisions[best_precision_idx], 
                       color='magenta', s=100, marker='*', label='Best Precision', zorder=5)
            plt.xlabel('Soft Recall')
            plt.ylabel('Soft Precision')
            plt.title('Precision vs Recall Trade-off')
            plt.colorbar(label='Trial Number')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Distribution of metrics
            plt.subplot(2, 3, 6)
            plt.hist(soft_recalls, bins=15, alpha=0.7, label='Soft Recall', color='blue')
            plt.hist(soft_f1s, bins=15, alpha=0.7, label='Soft F1', color='green')
            plt.hist(soft_precisions, bins=15, alpha=0.7, label='Soft Precision', color='magenta')
            plt.xlabel('Metric Value')
            plt.ylabel('Frequency')
            plt.title('Distribution of Metrics')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save plot
            plot_path = os.path.join(self.output_dir, 'optimization_progress.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()  # Close figure to free memory
            
            self.logger.info(f"Optimization plots saved to {plot_path}")
            
        except Exception as e:
            self.logger.error(f"Error creating optimization plots: {e}")
    
    def _generate_summary_report(
        self, 
        best_parameters: Dict[str, Any], 
        trial_results: List[Dict],
        feature_names: List[str]
    ) -> None:
        """Generate comprehensive summary report"""
        try:
            report_path = os.path.join(self.output_dir, 'README.md')
            
            # Calculate summary statistics
            soft_recalls = [self._safe_extract_float(t['results']['soft_recall']) for t in trial_results]
            soft_f1s = [self._safe_extract_float(t['results']['soft_f1_score']) for t in trial_results]
            
            best_trial = max(trial_results, key=lambda x: self._safe_extract_float(x['results']['soft_recall']))
            best_f1_trial = max(trial_results, key=lambda x: self._safe_extract_float(x['results']['soft_f1_score']))
            
            with open(report_path, 'w') as f:
                f.write(f"# AE Optimization Summary Report\n\n")
                f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"## Configuration\n\n")
                f.write(f"- **Dataset**: {self.config.DATA_PATH}\n")
                f.write(f"- **Label**: {self.config.LABEL_COLUMN}\n")
                f.write(f"- **Features**: {len(feature_names)} features\n")
                f.write(f"- **Trials**: {self.config.AE_NUM_TRIALS}\n")
                f.write(f"- **Ensemble Size**: {self.config.N_ENSEMBLE_GROUP_NUMBER}\n")
                f.write(f"- **Min Recall Threshold**: {self.config.MIN_RECALL_THRESHOLD}\n\n")
                
                f.write(f"## Results\n\n")
                f.write(f"### Best Performance\n")
                f.write(f"- **Best Soft Recall**: {max(soft_recalls):.4f} (Trial {best_trial['trial']})\n")
                f.write(f"- **Best Soft F1**: {max(soft_f1s):.4f} (Trial {best_f1_trial['trial']})\n")
                f.write(f"- **Average Recall**: {np.mean(soft_recalls):.4f} ± {np.std(soft_recalls):.4f}\n")
                f.write(f"- **Average F1**: {np.mean(soft_f1s):.4f} ± {np.std(soft_f1s):.4f}\n\n")
                
                # Add timing information if available
                trial_times = [t.get('trial_duration_seconds', 0) for t in trial_results if 'trial_duration_seconds' in t]
                if trial_times:
                    avg_time = sum(trial_times) / len(trial_times)
                    total_time = sum(trial_times)
                    min_time = min(trial_times)
                    max_time = max(trial_times)
                    
                    f.write(f"### Timing Performance\n")
                    f.write(f"- **Total Optimization Time**: {total_time:.1f}s ({total_time/60:.1f}m)\n")
                    f.write(f"- **Average Time per Trial**: {avg_time:.1f}s\n")
                    f.write(f"- **Fastest Trial**: {min_time:.1f}s\n")
                    f.write(f"- **Slowest Trial**: {max_time:.1f}s\n")
                    f.write(f"- **Training Mode**: {'Parallel' if self.config.PARALLEL_TRAINING else 'Sequential'}\n")
                    if self.config.PARALLEL_TRAINING:
                        f.write(f"- **CPU Cores Used**: {self.config.N_JOBS if self.config.N_JOBS > 0 else 'All available'}\n")
                    f.write(f"\n")
                
                f.write(f"### Best Parameters\n")
                f.write(f"```json\n")
                f.write(json.dumps(best_parameters, indent=2))
                f.write(f"\n```\n\n")
                
                f.write(f"## Files Generated\n\n")
                f.write(f"- `best_parameters.json`: Best parameters and metrics\n")
                f.write(f"- `optimization_progress.png`: Optimization progress plots\n")
                f.write(f"- `config.json`: Configuration used for this run\n")
                f.write(f"- `README.md`: This summary report\n\n")
                
                f.write(f"## Feature Information\n\n")
                f.write(f"**Features used**: {', '.join(feature_names)}\n\n")
                
                f.write(f"## Usage\n\n")
                f.write(f"To use the best parameters:\n\n")
                f.write(f"```python\n")
                f.write(f"import json\n")
                f.write(f"with open('best_parameters.json', 'r') as f:\n")
                f.write(f"    results = json.load(f)\n")
                f.write(f"    best_params = results['parameters']\n")
                f.write(f"```\n")
            
            self.logger.info(f"Summary report saved to {report_path}")
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {e}")
    
    def create_feature_importance_visualization(
        self, 
        feature_importance_data: Dict[str, Any]
    ) -> None:
        """Create comprehensive feature importance visualization plots"""
        try:
            if not feature_importance_data:
                self.logger.warning("No feature importance data available for visualization")
                return
            
            feature_names = feature_importance_data['feature_names']
            lgb_importance = feature_importance_data['lgb_importance']
            lgb_std = feature_importance_data['lgb_importance_std']
            perm_importance = feature_importance_data['permutation_importance']
            perm_std = feature_importance_data['permutation_importance_std']
            
            # Create 2x2 subplot layout for feature importance
            plt.figure(figsize=(16, 12))
            
            # 1. LightGBM Feature Importance (Top 10)
            plt.subplot(2, 2, 1)
            top_10_lgb = sorted(
                zip(feature_names, lgb_importance, lgb_std), 
                key=lambda x: x[1], reverse=True
            )[:10]
            
            names, importances, stds = zip(*top_10_lgb)
            y_pos = np.arange(len(names))
            
            plt.barh(y_pos, importances, xerr=stds, alpha=0.7, color='skyblue', capsize=5)
            plt.yticks(y_pos, names)
            plt.xlabel('LightGBM Feature Importance')
            plt.title('Top 10 Features - LightGBM Gain-based Importance')
            plt.gca().invert_yaxis()
            plt.grid(True, alpha=0.3)
            
            # 2. Permutation Feature Importance (Top 10)
            plt.subplot(2, 2, 2)
            top_10_perm = sorted(
                zip(feature_names, perm_importance, perm_std), 
                key=lambda x: x[1], reverse=True
            )[:10]
            
            names_perm, importances_perm, stds_perm = zip(*top_10_perm)
            y_pos_perm = np.arange(len(names_perm))
            
            plt.barh(y_pos_perm, importances_perm, xerr=stds_perm, alpha=0.7, color='lightcoral', capsize=5)
            plt.yticks(y_pos_perm, names_perm)
            plt.xlabel('Permutation Importance (F1 Score)')
            plt.title('Top 10 Features - Permutation Importance')
            plt.gca().invert_yaxis()
            plt.grid(True, alpha=0.3)
            
            # 3. Comparison: LightGBM vs Permutation (Top 10 combined)
            plt.subplot(2, 2, 3)
            
            # Get top features from both methods
            all_top_features = list(set([name for name, _, _ in top_10_lgb] + 
                                      [name for name, _, _ in top_10_perm]))
            
            lgb_dict = {name: imp for name, imp, _ in zip(feature_names, lgb_importance, lgb_std)}
            perm_dict = {name: imp for name, imp, _ in zip(feature_names, perm_importance, perm_std)}
            
            # Normalize for comparison (0-1 scale)
            max_lgb = max(lgb_importance) if max(lgb_importance) > 0 else 1
            max_perm = max(perm_importance) if max(perm_importance) > 0 else 1
            
            lgb_normalized = [lgb_dict[name] / max_lgb for name in all_top_features]
            perm_normalized = [perm_dict[name] / max_perm for name in all_top_features]
            
            x = np.arange(len(all_top_features))
            width = 0.35
            
            plt.bar(x - width/2, lgb_normalized, width, label='LightGBM (normalized)', alpha=0.7, color='skyblue')
            plt.bar(x + width/2, perm_normalized, width, label='Permutation (normalized)', alpha=0.7, color='lightcoral')
            
            plt.xlabel('Features')
            plt.ylabel('Normalized Importance')
            plt.title('Feature Importance Comparison')
            plt.xticks(x, all_top_features, rotation=45, ha='right')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 4. Feature Importance Correlation
            plt.subplot(2, 2, 4)
            
            # Create scatter plot comparing both importance methods
            plt.scatter(lgb_importance, perm_importance, alpha=0.7, s=60)
            
            # Add feature names for top features
            top_features_combined = set([name for name, _, _ in top_10_lgb[:5]] + 
                                      [name for name, _, _ in top_10_perm[:5]])
            
            for i, name in enumerate(feature_names):
                if name in top_features_combined:
                    plt.annotate(name, (lgb_importance[i], perm_importance[i]), 
                               xytext=(5, 5), textcoords='offset points', fontsize=8)
            
            plt.xlabel('LightGBM Feature Importance')
            plt.ylabel('Permutation Importance')
            plt.title('Feature Importance Correlation')
            plt.grid(True, alpha=0.3)
            
            # Add correlation coefficient
            correlation = np.corrcoef(lgb_importance, perm_importance)[0, 1]
            plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                    transform=plt.gca().transAxes, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            # Save feature importance plot
            plot_path = os.path.join(self.output_dir, 'feature_importance.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()  # Close figure to free memory
            
            self.logger.info(f"Feature importance visualization saved to {plot_path}")
            
            # Save numerical feature importance data
            self._save_feature_importance_data(feature_importance_data)
            
            # Log important insights
            if 'consensus_features' in feature_importance_data:
                consensus = feature_importance_data['consensus_features']
                if consensus:
                    self.logger.info(f"Consensus top features (both methods): {consensus}")
                else:
                    self.logger.info("No consensus features found between LightGBM and permutation methods")
            
        except Exception as e:
            self.logger.error(f"Error creating feature importance visualization: {e}")
    
    def _save_feature_importance_data(self, feature_importance_data: Dict[str, Any]) -> None:
        """Save numerical feature importance data to CSV and JSON files"""
        try:
            import pandas as pd
            
            feature_names = feature_importance_data['feature_names']
            lgb_importance = feature_importance_data['lgb_importance']
            lgb_std = feature_importance_data['lgb_importance_std']
            perm_importance = feature_importance_data['permutation_importance']
            perm_std = feature_importance_data['permutation_importance_std']
            
            # Create DataFrame with all feature importance data
            df = pd.DataFrame({
                'feature_name': feature_names,
                'lgb_importance': lgb_importance,
                'lgb_importance_std': lgb_std,
                'permutation_importance': perm_importance,
                'permutation_importance_std': perm_std
            })
            
            # Sort by LightGBM importance (descending)
            df = df.sort_values('lgb_importance', ascending=False)
            
            # Add ranking columns
            df['lgb_rank'] = range(1, len(df) + 1)
            df['permutation_rank'] = df['permutation_importance'].rank(ascending=False, method='min').astype(int)
            
            # Save to CSV
            csv_path = os.path.join(self.output_dir, 'feature_importance.csv')
            df.to_csv(csv_path, index=False, float_format='%.6f')
            
            # Create summary dictionary for JSON
            summary_data = {
                'metadata': {
                    'total_features': len(feature_names),
                    'lgb_max_importance': float(max(lgb_importance)),
                    'perm_max_importance': float(max(perm_importance)),
                    'correlation': float(np.corrcoef(lgb_importance, perm_importance)[0, 1])
                },
                'top_10_lgb': [
                    {
                        'feature': row['feature_name'],
                        'importance': float(row['lgb_importance']),
                        'std': float(row['lgb_importance_std']),
                        'rank': int(row['lgb_rank'])
                    }
                    for _, row in df.head(10).iterrows()
                ],
                'top_10_permutation': [
                    {
                        'feature': row['feature_name'],
                        'importance': float(row['permutation_importance']),
                        'std': float(row['permutation_importance_std']),
                        'rank': int(row['permutation_rank'])
                    }
                    for _, row in df.nsmallest(10, 'permutation_rank').iterrows()
                ],
                'all_features': [
                    {
                        'feature': row['feature_name'],
                        'lgb_importance': float(row['lgb_importance']),
                        'lgb_std': float(row['lgb_importance_std']),
                        'lgb_rank': int(row['lgb_rank']),
                        'permutation_importance': float(row['permutation_importance']),
                        'permutation_std': float(row['permutation_importance_std']),
                        'permutation_rank': int(row['permutation_rank'])
                    }
                    for _, row in df.iterrows()
                ]
            }
            
            # Add consensus features if available
            if 'consensus_features' in feature_importance_data:
                summary_data['consensus_features'] = feature_importance_data['consensus_features']
            
            # Save to JSON
            json_path = os.path.join(self.output_dir, 'feature_importance.json')
            with open(json_path, 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            self.logger.info(f"Feature importance data saved to {csv_path} and {json_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving feature importance numerical data: {e}")