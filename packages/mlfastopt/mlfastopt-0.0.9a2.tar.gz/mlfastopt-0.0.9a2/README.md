# MLFastOpt

[![PyPI version](https://badge.fury.io/py/mlfastopt.svg)](https://badge.fury.io/py/mlfastopt)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MLFastOpt is a comprehensive ensemble optimization system for Bayesian hyperparameter optimization of **LightGBM models only**. It provides automated machine learning capabilities with a focus on speed, accuracy, and ease of use.

**Why LightGBM Only?** We chose to focus exclusively on LightGBM because it offers similar performance to XGBoost but with significantly faster training times. Our objective is not to debate which gradient boosting framework is superior, but rather to provide the fastest possible hyperparameter optimization experience. By specializing in LightGBM, we can optimize the entire pipeline for maximum speed and efficiency.

## Features

- 🚀 **Fast Optimization**: Advanced Bayesian optimization algorithms
- 🎯 **LightGBM Ensembles**: Automated ensemble model creation and tuning
- 🌐 **Web Interface**: Interactive visualization and analysis tools
- ⚙️ **Flexible Configuration**: Environment-based configuration system
- 📊 **Rich Analytics**: Comprehensive performance analysis and visualization
- 🔧 **Easy CLI**: Simple command-line interface for all operations

## Installation

```bash
pip install mlfastopt
```

For development installation:

```bash
git clone https://github.com/your-repo/mlfastopt
cd mlfastopt
pip install -e .[dev]
```

## Quick Start

MLFastOpt is a framework that requires you to provide your own configuration files. Here's how to get started:

### 1. Create Directory Structure

```bash
mkdir -p config/hyperparameters
mkdir -p data
# Note: Output directories (outputs/, outputs/runs/, etc.) are created automatically
```

### 2. Create Hyperparameter Space

Create a hyperparameter space file (e.g., `config/hyperparameters/my_space.py`):

This file needs to be included in config file(e.g., `my_config.json`)
```python
# config/hyperparameters/my_space.py
PARAMETERS = [
    {"name": "boosting_type", "type": "choice", "values": ["gbdt", "dart"], "value_type": "str"},
    {"name": "num_leaves", "type": "range", "bounds": [20, 200], "value_type": "int"},
    {"name": "learning_rate", "type": "range", "bounds": [0.01, 0.3], "value_type": "float", "log_scale": True},
    {"name": "n_estimators", "type": "range", "bounds": [100, 300], "value_type": "int"},
    {"name": "subsample", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    {"name": "colsample_bytree", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    {"name": "reg_alpha", "type": "range", "bounds": [1e-8, 0.5], "value_type": "float", "log_scale": True},
    {"name": "reg_lambda", "type": "range", "bounds": [1e-8, 0.5], "value_type": "float", "log_scale": True},
    {"name": "is_unbalance", "type": "choice", "values": [True, False], "value_type": "bool"},
]

def get_parameter_space():
    return PARAMETERS
```

### 3. Create Configuration File

Create your optimization configuration file (e.g., `my_config.json`):

```json
{
  "_description": "Example configuration for MLFastOpt optimization",
  "_hyperparameter_space": "Custom hyperparameter space for your use case",
  
  "DATA_PATH": "data/your_dataset.csv",
  "HYPERPARAMETER_PATH": "config/hyperparameters/my_space.py",
  "LABEL_COLUMN": "target",
  "FEATURES": ["feature1", "feature2", "feature3", "feature4", "feature5"],
  
  "CLASS_WEIGHT": {"0": 1, "1": 3},
  "UNDER_SAMPLE_MAJORITY_RATIO": 2,
  
  "N_ENSEMBLE_GROUP_NUMBER": 15,
  "AE_NUM_TRIALS": 30,
  "NUM_SOBOL_TRIALS": 10,
  "RANDOM_SEED": 42,
  "PARALLEL_TRAINING": true,
  "N_JOBS": -1,
  
  "OPTIMIZATION_METRICS": "soft_recall",
  "BEST_TRIAL_FILE_SUFFIX": "my_experiment",
  "SOFT_PREDICTION_THRESHOLD": 0.7,
  "F1_THRESHOLD": 0.7,
  "MIN_RECALL_THRESHOLD": 0.80,
  
  "ENABLE_DATA_IMPUTATION": false,
  "IMPUTE_TARGET_NULLS": true,
  
  "SAVE_THRESHOLD_ENABLED": false,
  "SAVE_THRESHOLD_METRIC": "soft_recall",
  "SAVE_THRESHOLD_VALUE": 0.85,
  "FALLBACK_TOP_K": 5,
  "FALLBACK_METRIC": "soft_recall"
}
```

### Configuration Parameters Explained

#### **Required Parameters**
- **`DATA_PATH`**: Path to your dataset (CSV, Parquet, etc.)
- **`HYPERPARAMETER_PATH`**: Path to your hyperparameter space Python file
- **`LABEL_COLUMN`**: Name of the label column in your dataset
- **`FEATURES`**: List of feature column names to use for training
- **`CLASS_WEIGHT`**: Dictionary mapping class labels to weights for imbalanced data
- **`UNDER_SAMPLE_MAJORITY_RATIO`**: Ratio for undersampling majority class (1 = no undersampling)
- **`N_ENSEMBLE_GROUP_NUMBER`**: Number of models in each ensemble (affects training time)
- **`AE_NUM_TRIALS`**: Total number of optimization trials to run
- **`NUM_SOBOL_TRIALS`**: Number of initial random exploration trials
- **`RANDOM_SEED`**: Random seed for reproducibility
- **`PARALLEL_TRAINING`**: Enable parallel model training
- **`N_JOBS`**: Number of CPU cores to use (-1 = all available)
- **`SOFT_PREDICTION_THRESHOLD`**: Threshold for converting probabilities to binary predictions
- **`MIN_RECALL_THRESHOLD`**: Minimum recall threshold for trial validation

#### **Optional Parameters**
- **`OPTIMIZATION_METRICS`**: Metric to optimize (default: `"soft_recall"`)
- **`F1_THRESHOLD`**: Target F1-score threshold (default: `0.7`)
- **`BEST_TRIAL_FILE_SUFFIX`**: Custom suffix for best trial filenames (default: auto-extract from dataset name)
- **`ENABLE_DATA_IMPUTATION`**: Enable feature imputation (default: `false`)
- **`IMPUTE_TARGET_NULLS`**: Handle null values in target column (default: `true`)

#### **Advanced Trial Selection (Optional)**
- **`SAVE_THRESHOLD_ENABLED`**: Enable threshold-based trial selection (default: `false`)
- **`SAVE_THRESHOLD_METRIC`**: Metric to use for threshold selection (default: `"soft_recall"`)
- **`SAVE_THRESHOLD_VALUE`**: Minimum value to save trials (default: `0.85`)
- **`FALLBACK_TOP_K`**: Number of top trials if none meet threshold (default: `5`)
- **`FALLBACK_METRIC`**: Metric for fallback ranking (default: `"soft_recall"`)

### 4. Run Optimization

```bash
# Set threading environment variable (important!)
export OMP_NUM_THREADS=1

# Run optimization
OMP_NUM_THREADS=1 python -m mlfastopt.cli --config my_config.json

# Validate configuration first
python -m mlfastopt.cli --validate --config my_config.json
```

## Architecture

MLFastOpt is organized into several key modules, all optimized specifically for LightGBM:

- **`mlfastopt.core`**: Core optimization engine and configuration management for LightGBM ensembles
- **`mlfastopt.cli`**: Command-line interface for LightGBM hyperparameter optimization
- **`mlfastopt.web`**: Web-based visualization and analysis tools for LightGBM optimization results

## Configuration System

MLFastOpt is a framework that requires user-provided configurations:

1. **Configuration files**: JSON files defining optimization parameters and data paths
2. **Hyperparameter spaces**: Python modules defining LightGBM parameter search spaces
3. **Data files**: Your datasets in CSV, Parquet, or other pandas-compatible formats

All output directories are created automatically by the framework.

## Hyperparameter Tuning

MLFastOpt requires you to define custom LightGBM hyperparameter spaces for your specific use case:

### Creating Parameter Spaces

You must create your own hyperparameter space files. Here's the syntax:

### Parameter Types

- **Choice**: `{"name": "param", "type": "choice", "values": ["a", "b"], "value_type": "str"}`
- **Range (Int)**: `{"name": "param", "type": "range", "bounds": [1, 100], "value_type": "int"}`
- **Range (Float)**: `{"name": "param", "type": "range", "bounds": [0.1, 1.0], "value_type": "float"}`
- **Log Scale**: Add `"log_scale": True` for logarithmic parameter exploration
- **Boolean**: `{"name": "param", "type": "choice", "values": [True, False], "value_type": "bool"}`

### Example Parameter Space

```python
# config/hyperparameters/my_space.py
PARAMETERS = [
    # Boosting algorithm
    {"name": "boosting_type", "type": "choice", "values": ["gbdt", "dart"], "value_type": "str"},
    
    # Tree structure
    {"name": "num_leaves", "type": "range", "bounds": [20, 200], "value_type": "int"},
    {"name": "max_depth", "type": "range", "bounds": [-1, 30], "value_type": "int"},
    
    # Learning parameters
    {"name": "learning_rate", "type": "range", "bounds": [0.01, 0.3], "value_type": "float", "log_scale": True},
    {"name": "n_estimators", "type": "range", "bounds": [100, 500], "value_type": "int"},
    
    # Regularization
    {"name": "reg_alpha", "type": "range", "bounds": [1e-8, 1.0], "value_type": "float", "log_scale": True},
    {"name": "reg_lambda", "type": "range", "bounds": [1e-8, 1.0], "value_type": "float", "log_scale": True},
    
    # Sampling
    {"name": "subsample", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    {"name": "colsample_bytree", "type": "range", "bounds": [0.3, 1.0], "value_type": "float"},
    
    # Class balance
    {"name": "is_unbalance", "type": "choice", "values": [True, False], "value_type": "bool"},
]

def get_parameter_space():
    """Required function that returns the parameter list"""
    return PARAMETERS
```

### Configuration

Reference your parameter space in the config file:

```json
{
  "HYPERPARAMETER_PATH": "config/hyperparameters/my_space.py",
  "DATA_PATH": "data/your_dataset.csv",
  "LABEL_COLUMN": "target",
  "AE_NUM_TRIALS": 50
}
```

## Optimization Metrics

MLFastOpt allows you to choose which metric to optimize during hyperparameter tuning. By default, it optimizes `soft_recall`, but you can configure it to optimize any of the available metrics.

### Configurable Optimization Metric

Set the `OPTIMIZATION_METRICS` parameter in your configuration file:

```json
{
  "OPTIMIZATION_METRICS": "soft_f1_score",
  "..."
}
```

### Available Metrics

- **`soft_recall`** (default): Recall from soft voting ensemble predictions
- **`hard_recall`**: Recall from hard voting ensemble predictions  
- **`soft_f1_score`**: F1-score from soft voting ensemble predictions
- **`hard_f1_score`**: F1-score from hard voting ensemble predictions
- **`soft_precision`**: Precision from soft voting ensemble predictions
- **`hard_precision`**: Precision from hard voting ensemble predictions

### Soft vs Hard Voting

- **Soft Voting**: Averages predicted probabilities from all ensemble models, then applies threshold
- **Hard Voting**: Averages binary predictions from all ensemble models

Soft voting typically provides better calibrated predictions and is recommended for most use cases.

### Example Configurations

**High Recall for Fraud Detection:**
```json
{
  "OPTIMIZATION_METRICS": "soft_recall",
  "SOFT_PREDICTION_THRESHOLD": 0.2,
  "MIN_RECALL_THRESHOLD": 0.95
}
```

**Balanced Performance:**
```json
{
  "OPTIMIZATION_METRICS": "soft_f1_score", 
  "SOFT_PREDICTION_THRESHOLD": 0.5,
  "MIN_RECALL_THRESHOLD": 0.75
}
```

**High Precision for Medical Diagnosis:**
```json
{
  "OPTIMIZATION_METRICS": "soft_precision",
  "SOFT_PREDICTION_THRESHOLD": 0.8,
  "MIN_RECALL_THRESHOLD": 0.70
}
```

## Data Preprocessing Requirements

MLFastOpt expects **preprocessed, numerical data only**. You must handle all data preprocessing before running optimization.

### Required Preprocessing Steps

1. **Categorical Features**: Must be encoded before optimization
   - ✅ One-hot encoding: `pd.get_dummies()`
   - ✅ Label encoding: `LabelEncoder()`
   - ✅ Target encoding, ordinal encoding, etc.
   - ❌ Raw categorical strings/text

2. **Feature Engineering**: Complete all feature engineering beforehand
   - Feature scaling, normalization (optional - LightGBM handles this)
   - Feature selection and dimensionality reduction
   - Creating interaction features, polynomial features

3. **Missing Values**: Handle according to your domain requirements
   - Set `ENABLE_DATA_IMPUTATION: false` to let LightGBM handle nulls
   - Set `ENABLE_DATA_IMPUTATION: true` for median/mode imputation

### Example Preprocessing Pipeline

```python
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Load raw data
df = pd.read_csv('raw_data.csv')

# 1. Handle categorical features
categorical_cols = ['category_A', 'category_B']
df = pd.get_dummies(df, columns=categorical_cols, dtype=int)

# 2. Handle missing values (optional)
# df = df.fillna(df.median())  # or let LightGBM handle nulls

# 3. Save preprocessed data
df.to_parquet('preprocessed_data.parquet', index=False)

# 4. Update your config
config = {
    "DATA_PATH": "preprocessed_data.parquet",
    "FEATURES": df.columns.tolist(),  # All preprocessed features
    "LABEL_COLUMN": "target"
}
```

### Why No Built-in Categorical Processing?

- **Performance**: Preprocessing once vs. every optimization run
- **Flexibility**: Full control over encoding strategies
- **Consistency**: Same preprocessing for training and production
- **Domain Knowledge**: Categorical encoding often requires domain expertise

## Requirements

- Python 3.8+
- LightGBM 3.3.0+
- Pandas, NumPy, Scikit-learn
- Flask (for web interface)
- Plotly, Matplotlib (for visualization)

## Performance Considerations

- Always set `OMP_NUM_THREADS=1` for LightGBM to avoid thread conflicts
- Parallel training is controlled via configuration parameters
- Optimization algorithms benefit from multiple CPU cores

## Examples

### Development Run (Fast)
```bash
# 15 trials, 10 models (~15-20 minutes)
OMP_NUM_THREADS=1 python -m mlfastopt.cli --environment development
```

### Production Run
```bash
# Full optimization with more trials
OMP_NUM_THREADS=1 python -m mlfastopt.cli --environment production
```

### Validation
```bash
# Validate configuration without running optimization
python -m mlfastopt.cli --config config/environments/development.json --validate
```

## Data Requirements

- Input data should be in Parquet, CSV, or other pandas-compatible formats
- Target column must be binary (0/1) for classification
- Features are automatically handled by LightGBM (nulls, categorical encoding)
- Categorical features should be specified in configuration

## Output Structure

All outputs are organized under `outputs/`:
- `outputs/runs/`: Individual optimization run results
- `outputs/best_trials/`: Best performing configurations  
- `outputs/logs/`: Execution logs
- `outputs/visualizations/`: Generated plots and analysis

### Best Trial File Naming

Best trial files are automatically named to distinguish different experiments:

#### **With Custom BEST_TRIAL_FILE_SUFFIX**
```json
{
  "BEST_TRIAL_FILE_SUFFIX": "fraud_experiment_v2",
  "DATA_PATH": "data/fraud_data.csv"
}
```
**Output files:**
- `2025-08-04_fraud_experiment_v2.json`
- `2025-08-04_fraud_experiment_v2_threshold_soft_recall_0.85.json`

#### **Auto-extracted from Dataset Name**
```json
{
  "BEST_TRIAL_FILE_SUFFIX": "",
  "DATA_PATH": "data/customer_churn/processed_data.csv"
}
```
**Output files:**
- `2025-08-04_processed_data.json`
- `2025-08-04_processed_data_top_5_soft_recall.json`

This naming prevents different experiments from overwriting each other and makes results easily identifiable.

## CLI Commands

The package provides several command-line entry points:

- `mlfastopt-optimize`: Main optimization CLI
- `mlfastopt-web`: Web interface launcher  
- `mlfastopt-analyze`: Analysis tools

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use MLFastOpt in your research, please cite:

```bibtex
@software{mlfastopt,
  title={MLFastOpt: Fast Ensemble Optimization with Advanced Bayesian Methods},
  author={MLFastOpt Development Team},
  url={https://github.com/your-repo/mlfastopt},
  version={0.0.9a2},
  year={2025}
}
```