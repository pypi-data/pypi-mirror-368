"""
Model components for AE optimization.

This module contains ensemble model training and evaluation classes.
"""

import logging
import time
from typing import Dict, List, Tuple, Optional, Any

import pandas as pd
import numpy as np
from sklearn.metrics import recall_score, f1_score, precision_score
from sklearn.inspection import permutation_importance
from lightgbm import LGBMClassifier

from .config import AEConfig

# Parallel processing import (optional)
try:
    from joblib import Parallel, delayed
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    logging.warning("joblib not available. Parallel training will fall back to sequential mode.")


class EnsembleModel:
    """Ensemble model trainer and predictor"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.models: List[LGBMClassifier] = []
    
    def create_balanced_sample(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        minority_label: int = 1, 
        majority_label: int = 0
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Create balanced sample using undersampling"""
        try:
            # Combine features and target
            df = pd.concat([X_train, y_train], axis=1)
            
            minority_samples = df[df[self.config.LABEL_COLUMN] == minority_label]
            majority_samples = df[df[self.config.LABEL_COLUMN] == majority_label]
            
            # Calculate desired sample size
            desired_sample_size = int(len(minority_samples) * self.config.UNDER_SAMPLE_MAJORITY_RATIO)
            
            # Sample majority class
            if len(majority_samples) < desired_sample_size:
                self.logger.warning(
                    f"Requested {desired_sample_size} majority samples but only "
                    f"{len(majority_samples)} available. Using replacement."
                )
                sampled_majority = majority_samples.sample(
                    n=desired_sample_size, 
                    replace=True, 
                    random_state=self.config.RANDOM_SEED
                )
            else:
                sampled_majority = majority_samples.sample(
                    n=desired_sample_size, 
                    random_state=self.config.RANDOM_SEED
                )
            
            # Combine samples
            balanced_df = pd.concat([minority_samples, sampled_majority])
            
            # Split back into features and target
            X_balanced = balanced_df.drop(self.config.LABEL_COLUMN, axis=1)
            y_balanced = balanced_df[self.config.LABEL_COLUMN]
            
            # Calculate before/after statistics
            original_label_1 = len(minority_samples)
            original_label_0 = len(majority_samples)
            balanced_label_1 = len(minority_samples)
            balanced_label_0 = len(sampled_majority)
            
            reduction_ratio = original_label_0 / balanced_label_0 if balanced_label_0 > 0 else 1
            
            self.logger.info(f"📊 BALANCED SAMPLING APPLIED:")
            self.logger.info(f"   • Original training data: {len(X_train):,} rows")
            self.logger.info(f"     - Label=1: {original_label_1:,}, Label=0: {original_label_0:,}")
            self.logger.info(f"   • Balanced sample: {len(balanced_df):,} rows")
            self.logger.info(f"     - Label=1: {balanced_label_1:,}, Label=0: {balanced_label_0:,}")
            self.logger.info(f"   • Undersampling ratio: {reduction_ratio:.1f}:1 (majority class reduced)")
            self.logger.info(f"   • Final class balance: 1:1 (perfect balance achieved)")
            
            return X_balanced, y_balanced
            
        except Exception as e:
            self.logger.error(f"Error creating balanced sample: {e}")
            return X_train, y_train
    
    def _train_single_model(
        self, 
        model_index: int, 
        X_balanced: pd.DataFrame, 
        y_balanced: pd.Series, 
        parameters: Dict[str, Any]
    ) -> Optional[LGBMClassifier]:
        """Train a single LightGBM model (for parallel processing)"""
        try:
            model = LGBMClassifier(
                boosting_type=parameters["boosting_type"],
                num_leaves=parameters["num_leaves"],
                max_depth=parameters["max_depth"],
                learning_rate=parameters["learning_rate"],
                n_estimators=parameters["n_estimators"],
                subsample_for_bin=parameters["subsample_for_bin"],
                min_split_gain=parameters["min_split_gain"],
                min_child_weight=parameters["min_child_weight"],
                min_child_samples=parameters["min_child_samples"],
                subsample=parameters["subsample"],
                subsample_freq=parameters["subsample_freq"],
                colsample_bytree=parameters["colsample_bytree"],
                reg_alpha=parameters["reg_alpha"],
                reg_lambda=parameters["reg_lambda"],
                is_unbalance=parameters["is_unbalance"],
                random_state=self.config.RANDOM_SEED + model_index,
                class_weight=self.config.CLASS_WEIGHT,
                verbose=-1
            )
            
            model.fit(X_balanced, y_balanced)
            return model
            
        except Exception as e:
            self.logger.warning(f"Failed to train model {model_index+1}: {e}")
            return None
    
    def _train_ensemble_parallel(
        self, 
        X_balanced: pd.DataFrame, 
        y_balanced: pd.Series, 
        parameters: Dict[str, Any]
    ) -> List[LGBMClassifier]:
        """Train ensemble models in parallel using joblib"""
        if not JOBLIB_AVAILABLE:
            self.logger.warning("joblib not available, falling back to sequential training")
            return self._train_ensemble_sequential(X_balanced, y_balanced, parameters)
        
        try:
            self.logger.info(f"Training ensemble of {self.config.N_ENSEMBLE_GROUP_NUMBER} models in parallel (n_jobs={self.config.N_JOBS})")
            
            # Train models in parallel
            trained_models = Parallel(n_jobs=self.config.N_JOBS)(
                delayed(self._train_single_model)(i, X_balanced, y_balanced, parameters)
                for i in range(self.config.N_ENSEMBLE_GROUP_NUMBER)
            )
            
            # Filter out None results (failed models)
            models = [model for model in trained_models if model is not None]
            
            self.logger.info(f"Successfully trained {len(models)}/{self.config.N_ENSEMBLE_GROUP_NUMBER} models in parallel")
            return models
            
        except Exception as e:
            self.logger.error(f"Error in parallel training: {e}")
            self.logger.info("Falling back to sequential training")
            return self._train_ensemble_sequential(X_balanced, y_balanced, parameters)
    
    def _train_ensemble_sequential(
        self, 
        X_balanced: pd.DataFrame, 
        y_balanced: pd.Series, 
        parameters: Dict[str, Any]
    ) -> List[LGBMClassifier]:
        """Train ensemble models sequentially (original implementation)"""
        models = []
        successful_models = 0
        
        self.logger.info(f"Training ensemble of {self.config.N_ENSEMBLE_GROUP_NUMBER} models sequentially")
        
        for i in range(self.config.N_ENSEMBLE_GROUP_NUMBER):
            try:
                model = LGBMClassifier(
                    boosting_type=parameters["boosting_type"],
                    num_leaves=parameters["num_leaves"],
                    max_depth=parameters["max_depth"],
                    learning_rate=parameters["learning_rate"],
                    n_estimators=parameters["n_estimators"],
                    subsample_for_bin=parameters["subsample_for_bin"],
                    min_split_gain=parameters["min_split_gain"],
                    min_child_weight=parameters["min_child_weight"],
                    min_child_samples=parameters["min_child_samples"],
                    subsample=parameters["subsample"],
                    subsample_freq=parameters["subsample_freq"],
                    colsample_bytree=parameters["colsample_bytree"],
                    reg_alpha=parameters["reg_alpha"],
                    reg_lambda=parameters["reg_lambda"],
                    is_unbalance=parameters["is_unbalance"],
                    random_state=self.config.RANDOM_SEED + i,
                    class_weight=self.config.CLASS_WEIGHT,
                    verbose=-1
                )
                
                model.fit(X_balanced, y_balanced)
                models.append(model)
                successful_models += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to train model {i+1}: {e}")
        
        self.logger.info(f"Successfully trained {successful_models}/{self.config.N_ENSEMBLE_GROUP_NUMBER} models sequentially")
        return models
    
    def train_ensemble(
        self, 
        X_train: pd.DataFrame, 
        y_train: pd.Series, 
        parameters: Dict[str, Any]
    ) -> List[LGBMClassifier]:
        """Train ensemble of LightGBM models (parallel or sequential based on config)"""
        # Create balanced sample
        X_balanced, y_balanced = self.create_balanced_sample(X_train, y_train)
        
        # Choose training mode based on configuration
        if self.config.PARALLEL_TRAINING:
            models = self._train_ensemble_parallel(X_balanced, y_balanced, parameters)
        else:
            models = self._train_ensemble_sequential(X_balanced, y_balanced, parameters)
        
        self.models = models
        return models
    
    def predict_soft_voting(self, models: List[LGBMClassifier], X: pd.DataFrame) -> np.ndarray:
        """Make predictions using soft voting (probability averaging)"""
        if not models:
            self.logger.warning("No models available for prediction")
            return np.zeros(len(X))
        
        try:
            probas = np.array([model.predict_proba(X)[:, 1] for model in models])
            return np.mean(probas, axis=0)
        except Exception as e:
            self.logger.error(f"Error in soft voting prediction: {e}")
            return np.zeros(len(X))
    
    def predict_hard_voting(self, models: List[LGBMClassifier], X: pd.DataFrame) -> np.ndarray:
        """Make predictions using hard voting (prediction averaging)"""
        if not models:
            self.logger.warning("No models available for prediction")
            return np.zeros(len(X))
        
        try:
            preds = np.array([model.predict(X) for model in models])
            return np.mean(preds, axis=0)
        except Exception as e:
            self.logger.error(f"Error in hard voting prediction: {e}")
            return np.zeros(len(X))
    
    def calculate_feature_importance(
        self, 
        models: List[LGBMClassifier], 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        feature_names: List[str],
        n_repeats: int = 10
    ) -> Dict[str, Any]:
        """
        Calculate feature importance using both built-in and permutation importance
        
        Args:
            models: List of trained LightGBM models
            X_test: Test features
            y_test: Test targets  
            feature_names: List of feature names
            n_repeats: Number of permutation repeats for stability
            
        Returns:
            Dictionary containing both importance types and analysis
        """
        try:
            if not models:
                self.logger.warning("No models available for feature importance calculation")
                return {}
            
            # 1. Built-in Feature Importance (averaged across ensemble)
            lgb_importances = []
            for model in models:
                # Get feature importance from LightGBM (gain-based)
                importance = model.feature_importances_
                lgb_importances.append(importance)
            
            # Average importance across all models in ensemble
            avg_lgb_importance = np.mean(lgb_importances, axis=0)
            
            # 2. Permutation Importance (model-agnostic)
            # Create a wrapper class for permutation importance
            class EnsembleWrapper:
                def __init__(self, ensemble_model, models, feature_names, config):
                    self.ensemble_model = ensemble_model
                    self.models = models
                    self.feature_names = feature_names
                    self.config = config
                
                def fit(self, X, y):
                    # Required by scikit-learn interface but not used
                    # since models are already trained
                    return self
                
                def predict(self, X):
                    # Convert to DataFrame if needed
                    if isinstance(X, np.ndarray):
                        X = pd.DataFrame(X, columns=self.feature_names)
                    # Get soft voting predictions and convert to binary
                    soft_predictions = self.ensemble_model.predict_soft_voting(self.models, X)
                    # Use config threshold for consistency
                    return (soft_predictions > self.config.SOFT_PREDICTION_THRESHOLD).astype(int)
            
            # Create wrapper and calculate permutation importance
            ensemble_wrapper = EnsembleWrapper(self, models, feature_names, self.config)
            perm_importance = permutation_importance(
                estimator=ensemble_wrapper,
                X=X_test.values,
                y=y_test.values,
                scoring='f1',  # Use F1 score as it's one of our optimization targets
                n_repeats=n_repeats,
                random_state=42,
                n_jobs=1  # Use single job to avoid pickling issues
            )
            
            # 3. Create comprehensive results
            feature_importance_results = {
                'feature_names': feature_names,
                'lgb_importance': avg_lgb_importance,
                'lgb_importance_std': np.std(lgb_importances, axis=0),
                'permutation_importance': perm_importance.importances_mean,
                'permutation_importance_std': perm_importance.importances_std,
                'n_models': len(models),
                'n_repeats': n_repeats
            }
            
            # 4. Create sorted importance rankings
            lgb_ranking = sorted(
                zip(feature_names, avg_lgb_importance), 
                key=lambda x: x[1], reverse=True
            )
            perm_ranking = sorted(
                zip(feature_names, perm_importance.importances_mean), 
                key=lambda x: x[1], reverse=True
            )
            
            feature_importance_results['lgb_ranking'] = lgb_ranking
            feature_importance_results['perm_ranking'] = perm_ranking
            
            # 5. Identify top features from both methods
            top_lgb_features = [name for name, _ in lgb_ranking[:5]]
            top_perm_features = [name for name, _ in perm_ranking[:5]]
            consensus_features = list(set(top_lgb_features) & set(top_perm_features))
            
            feature_importance_results['top_lgb_features'] = top_lgb_features
            feature_importance_results['top_perm_features'] = top_perm_features
            feature_importance_results['consensus_features'] = consensus_features
            
            self.logger.info(f"Feature importance calculated successfully")
            self.logger.info(f"Top LGB features: {top_lgb_features}")
            self.logger.info(f"Top permutation features: {top_perm_features}")
            self.logger.info(f"Consensus features: {consensus_features}")
            
            return feature_importance_results
            
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {e}")
            return {}


class ModelEvaluator:
    """Handles model evaluation and metrics calculation"""
    
    def __init__(self, config: AEConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def evaluate_model(
        self, 
        models: List[LGBMClassifier], 
        X_test: pd.DataFrame, 
        y_test: pd.Series,
        ensemble_model: EnsembleModel
    ) -> Dict[str, float]:
        """Evaluate ensemble model performance"""
        try:
            # Soft voting predictions
            soft_predictions = ensemble_model.predict_soft_voting(models, X_test)
            soft_binary_predictions = (soft_predictions > self.config.SOFT_PREDICTION_THRESHOLD).astype(int)
            
            # Hard voting predictions  
            hard_predictions = ensemble_model.predict_hard_voting(models, X_test)
            hard_binary_predictions = (hard_predictions > self.config.SOFT_PREDICTION_THRESHOLD).astype(int)
            
            # Calculate metrics
            soft_recall = recall_score(y_test, soft_binary_predictions)
            hard_recall = recall_score(y_test, hard_binary_predictions)
            
            soft_f1 = f1_score(y_test, soft_binary_predictions)
            hard_f1 = f1_score(y_test, hard_binary_predictions)
            
            soft_precision = precision_score(y_test, soft_binary_predictions)
            hard_precision = precision_score(y_test, hard_binary_predictions)
            
            results = {
                "soft_recall": soft_recall,
                "hard_recall": hard_recall,
                "soft_f1_score": soft_f1,
                "hard_f1_score": hard_f1,
                "soft_precision": soft_precision,
                "hard_precision": hard_precision
            }
            
            self.logger.info(
                f"Model evaluation: "
                f"Soft Recall={soft_recall:.4f}, "
                f"Soft F1={soft_f1:.4f}, "
                f"Soft Precision={soft_precision:.4f}, "
                f"Hard Recall={hard_recall:.4f}, "
                f"Hard F1={hard_f1:.4f}, "
                f"Hard Precision={hard_precision:.4f}"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {
                "soft_recall": 0.0,
                "hard_recall": 0.0,
                "soft_f1_score": 0.0,
                "hard_f1_score": 0.0,
                "soft_precision": 0.0,
                "hard_precision": 0.0
            }