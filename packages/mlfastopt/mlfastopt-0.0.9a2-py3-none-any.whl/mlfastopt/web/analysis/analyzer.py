#!/usr/bin/env python3
"""
AE Output Visualizer

A comprehensive visualization framework for analyzing and comparing 
AE optimization results from the src/outputs directory.
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse
from dataclasses import dataclass
import numpy as np

# Set non-interactive backend for headless execution
matplotlib.use('Agg')

@dataclass
class RunData:
    """Data structure for a single optimization run"""
    run_id: str
    timestamp: datetime
    config: Dict
    parameters: Dict
    metrics: Dict
    timing_stats: Dict
    trial_results: Dict
    readme_path: str
    plots_available: List[str]

class OutputVisualizer:
    """Main visualization framework for AE optimization results"""
    
    def __init__(self, src_outputs_path: str = "outputs", output_dir: str = "visualizations"):
        self.src_outputs_path = Path(src_outputs_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.runs_data: List[RunData] = []
        
    def scan_outputs_directory(self) -> None:
        """Scan the src/outputs directory and extract all run data"""
        print(f"Scanning {self.src_outputs_path} for optimization runs...")
        
        if not self.src_outputs_path.exists():
            print(f"ERROR: Directory {self.src_outputs_path} does not exist!")
            return
            
        run_dirs = [d for d in self.src_outputs_path.iterdir() 
                   if d.is_dir() and d.name.startswith('run_')]
        
        print(f"Found {len(run_dirs)} optimization runs")
        
        for run_dir in sorted(run_dirs):
            try:
                run_data = self._extract_run_data(run_dir)
                if run_data:
                    self.runs_data.append(run_data)
                    print(f"✓ Loaded: {run_data.run_id}")
                else:
                    print(f"✗ Failed to load: {run_dir.name}")
            except Exception as e:
                print(f"✗ Error loading {run_dir.name}: {e}")
                
    def _extract_run_data(self, run_dir: Path) -> Optional[RunData]:
        """Extract data from a single run directory"""
        
        # Required files
        best_params_file = run_dir / "best_parameters.json"
        config_file = run_dir / "config.json"
        readme_file = run_dir / "README.md"
        
        if not all([best_params_file.exists(), config_file.exists(), readme_file.exists()]):
            return None
            
        # Load JSON data
        with open(best_params_file, 'r') as f:
            best_params_data = json.load(f)
            
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            
        # Parse timestamp from directory name
        timestamp_str = run_dir.name.replace('run_', '')
        timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        
        # Check for available plots
        plots_available = []
        for plot_file in ['optimization_progress.png', 'feature_importance.png']:
            if (run_dir / plot_file).exists():
                plots_available.append(plot_file)
                
        return RunData(
            run_id=run_dir.name,
            timestamp=timestamp,
            config=config_data,
            parameters=best_params_data.get('parameters', {}),
            metrics=best_params_data.get('metrics', {}),
            timing_stats=best_params_data.get('timing_stats', {}),
            trial_results=best_params_data.get('trial_results_summary', {}),
            readme_path=str(readme_file),
            plots_available=plots_available
        )
        
    def create_summary_dashboard(self) -> None:
        """Create a comprehensive summary dashboard"""
        if not self.runs_data:
            print("No run data available. Please scan outputs directory first.")
            return
            
        print("Creating summary dashboard...")
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('AE Optimization Runs Summary Dashboard', fontsize=16, fontweight='bold')
        
        # Prepare data for visualization
        df = self._create_summary_dataframe()
        
        # 1. Performance over time
        ax1 = axes[0, 0]
        ax1.plot(df['timestamp'], df['soft_recall'], 'o-', label='Soft Recall', linewidth=2)
        ax1.plot(df['timestamp'], df['soft_f1'], 's-', label='Soft F1', linewidth=2)
        ax1.plot(df['timestamp'], df['soft_precision'], '^-', label='Soft Precision', linewidth=2)
        ax1.set_title('Performance Metrics Over Time')
        ax1.set_ylabel('Score')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Timing performance
        ax2 = axes[0, 1]
        bars = ax2.bar(range(len(df)), df['avg_trial_time'], alpha=0.7)
        ax2.set_title('Average Trial Time by Run')
        ax2.set_ylabel('Time (seconds)')
        ax2.set_xticks(range(len(df)))
        ax2.set_xticklabels([f"Run {i+1}" for i in range(len(df))], rotation=45)
        
        # Color bars by training mode
        for i, (bar, mode) in enumerate(zip(bars, df['training_mode'])):
            if mode == 'Parallel':
                bar.set_color('orange')
            else:
                bar.set_color('skyblue')
        ax2.grid(True, alpha=0.3)
        
        # 3. Configuration distribution
        ax3 = axes[0, 2]
        trial_counts = df['num_trials'].value_counts().sort_index()
        ax3.pie(trial_counts.values, labels=[f"{x} trials" for x in trial_counts.index], 
                autopct='%1.1f%%', startangle=90)
        ax3.set_title('Trial Count Distribution')
        
        # 4. Performance vs ensemble size
        ax4 = axes[1, 0]
        scatter = ax4.scatter(df['ensemble_size'], df['soft_f1'], 
                            c=df['avg_trial_time'], cmap='viridis', 
                            s=100, alpha=0.7)
        ax4.set_xlabel('Ensemble Size')
        ax4.set_ylabel('Soft F1 Score')
        ax4.set_title('F1 Score vs Ensemble Size')
        plt.colorbar(scatter, ax=ax4, label='Avg Trial Time (s)')
        ax4.grid(True, alpha=0.3)
        
        # 5. Training mode comparison
        ax5 = axes[1, 1]
        mode_performance = df.groupby('training_mode')[['soft_recall', 'soft_f1', 'soft_precision']].mean()
        mode_performance.plot(kind='bar', ax=ax5)
        ax5.set_title('Performance by Training Mode')
        ax5.set_ylabel('Average Score')
        ax5.legend()
        ax5.tick_params(axis='x', rotation=0)
        ax5.grid(True, alpha=0.3)
        
        # 6. Run statistics table
        ax6 = axes[1, 2]
        ax6.axis('tight')
        ax6.axis('off')
        
        stats_data = [
            ['Total Runs', len(df)],
            ['Best Soft F1', f"{df['soft_f1'].max():.4f}"],
            ['Best Soft Recall', f"{df['soft_recall'].max():.4f}"],
            ['Best Soft Precision', f"{df['soft_precision'].max():.4f}"],
            ['Avg Trial Time', f"{df['avg_trial_time'].mean():.1f}s"],
            ['Date Range', f"{df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}"]
        ]
        
        table = ax6.table(cellText=stats_data, 
                         colLabels=['Metric', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax6.set_title('Summary Statistics')
        
        plt.tight_layout()
        
        # Save dashboard
        dashboard_path = self.output_dir / 'summary_dashboard.png'
        plt.savefig(dashboard_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Summary dashboard saved: {dashboard_path}")
        
    def _create_summary_dataframe(self) -> pd.DataFrame:
        """Create a pandas DataFrame with summary data from all runs"""
        data = []
        
        for run in self.runs_data:
            # Extract metric values (handle potential None values)
            soft_recall = run.metrics.get('soft_recall', [None])[0] or 0
            soft_f1 = run.metrics.get('soft_f1_score', [None])[0] or 0
            soft_precision = run.metrics.get('soft_precision', [None])[0] or 0
            
            data.append({
                'run_id': run.run_id,
                'timestamp': run.timestamp,
                'soft_recall': soft_recall,
                'soft_f1': soft_f1,
                'soft_precision': soft_precision,
                'num_trials': run.config.get('AE_NUM_TRIALS', 0),
                'ensemble_size': run.config.get('N_ENSEMBLE_GROUP_NUMBER', 0),
                'training_mode': 'Parallel' if run.config.get('PARALLEL_TRAINING', False) else 'Sequential',
                'avg_trial_time': run.timing_stats.get('average_trial_time_seconds', 0),
                'total_time': run.timing_stats.get('total_trial_time_seconds', 0)
            })
            
        return pd.DataFrame(data)
        
    def create_detailed_comparison(self) -> None:
        """Create detailed parameter and performance comparison"""
        if not self.runs_data:
            return
            
        print("Creating detailed comparison analysis...")
        
        # Create parameter comparison heatmap
        self._create_parameter_heatmap()
        
        # Create performance trends
        self._create_performance_trends()
        
        # Create timing analysis
        self._create_timing_analysis()
        
    def _create_parameter_heatmap(self) -> None:
        """Create heatmap of key parameters across runs"""
        
        # Extract key parameters that vary across runs
        param_data = []
        param_names = ['learning_rate', 'num_leaves', 'max_depth', 'n_estimators', 
                      'subsample', 'colsample_bytree', 'reg_alpha', 'reg_lambda']
        
        for run in self.runs_data:
            param_values = []
            for param in param_names:
                value = run.parameters.get(param, 0)
                param_values.append(value)
            param_data.append(param_values)
            
        if not param_data:
            return
            
        # Normalize data for better visualization
        param_df = pd.DataFrame(param_data, 
                               columns=param_names,
                               index=[f"Run {i+1}" for i in range(len(param_data))])
        
        # Create normalized version for heatmap
        param_df_norm = param_df.copy()
        for col in param_df_norm.columns:
            if param_df_norm[col].std() > 0:  # Avoid division by zero
                param_df_norm[col] = (param_df_norm[col] - param_df_norm[col].min()) / (param_df_norm[col].max() - param_df_norm[col].min())
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(param_df_norm.T, annot=False, cmap='viridis', ax=ax)
        ax.set_title('Parameter Values Across Runs (Normalized)')
        ax.set_xlabel('Optimization Runs')
        ax.set_ylabel('Parameters')
        
        plt.tight_layout()
        heatmap_path = self.output_dir / 'parameter_heatmap.png'
        plt.savefig(heatmap_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Parameter heatmap saved: {heatmap_path}")
        
    def _create_performance_trends(self) -> None:
        """Create detailed performance trend analysis"""
        
        df = self._create_summary_dataframe()
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Performance Trends Analysis', fontsize=16, fontweight='bold')
        
        # Performance metrics over time
        ax1 = axes[0, 0]
        ax1.plot(range(len(df)), df['soft_recall'], 'o-', label='Soft Recall', linewidth=2, markersize=6)
        ax1.plot(range(len(df)), df['soft_f1'], 's-', label='Soft F1', linewidth=2, markersize=6)
        ax1.plot(range(len(df)), df['soft_precision'], '^-', label='Soft Precision', linewidth=2, markersize=6)
        ax1.set_title('Performance Metrics Progression')
        ax1.set_xlabel('Run Number')
        ax1.set_ylabel('Score')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot of performance by training mode
        ax2 = axes[0, 1]
        perf_data = []
        labels = []
        for mode in ['Sequential', 'Parallel']:
            mode_data = df[df['training_mode'] == mode]
            if not mode_data.empty:
                perf_data.extend([mode_data['soft_recall'].values, 
                                mode_data['soft_f1'].values, 
                                mode_data['soft_precision'].values])
                labels.extend([f'{mode}\nRecall', f'{mode}\nF1', f'{mode}\nPrecision'])
        
        if perf_data:
            ax2.boxplot(perf_data, labels=labels)
            ax2.set_title('Performance Distribution by Training Mode')
            ax2.set_ylabel('Score')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, alpha=0.3)
        
        # Performance vs configuration
        ax3 = axes[1, 0]
        scatter = ax3.scatter(df['num_trials'], df['soft_f1'], 
                            c=df['ensemble_size'], cmap='plasma',
                            s=100, alpha=0.7)
        ax3.set_xlabel('Number of Trials')
        ax3.set_ylabel('Soft F1 Score')
        ax3.set_title('F1 Score vs Trial Count')
        plt.colorbar(scatter, ax=ax3, label='Ensemble Size')
        ax3.grid(True, alpha=0.3)
        
        # Best run identification
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')
        
        best_f1_idx = df['soft_f1'].idxmax()
        best_recall_idx = df['soft_recall'].idxmax()
        best_precision_idx = df['soft_precision'].idxmax()
        
        best_runs_data = [
            ['Best F1 Score', f"{df.loc[best_f1_idx, 'run_id']}", f"{df.loc[best_f1_idx, 'soft_f1']:.4f}"],
            ['Best Recall', f"{df.loc[best_recall_idx, 'run_id']}", f"{df.loc[best_recall_idx, 'soft_recall']:.4f}"],
            ['Best Precision', f"{df.loc[best_precision_idx, 'run_id']}", f"{df.loc[best_precision_idx, 'soft_precision']:.4f}"],
            ['', '', ''],
            ['Avg Performance', '', ''],
            ['Recall', '', f"{df['soft_recall'].mean():.4f} ± {df['soft_recall'].std():.4f}"],
            ['F1 Score', '', f"{df['soft_f1'].mean():.4f} ± {df['soft_f1'].std():.4f}"],
            ['Precision', '', f"{df['soft_precision'].mean():.4f} ± {df['soft_precision'].std():.4f}"]
        ]
        
        table = ax4.table(cellText=best_runs_data,
                         colLabels=['Metric', 'Run ID', 'Value'],
                         cellLoc='center',
                         loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        ax4.set_title('Best Runs Summary')
        
        plt.tight_layout()
        trends_path = self.output_dir / 'performance_trends.png'
        plt.savefig(trends_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Performance trends saved: {trends_path}")
        
    def _create_timing_analysis(self) -> None:
        """Create detailed timing analysis"""
        
        df = self._create_summary_dataframe()
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle('Timing Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # Average trial time comparison
        ax1 = axes[0, 0]
        mode_timing = df.groupby('training_mode')['avg_trial_time'].agg(['mean', 'std']).reset_index()
        
        bars = ax1.bar(mode_timing['training_mode'], mode_timing['mean'], 
                      yerr=mode_timing['std'], capsize=5, alpha=0.7)
        ax1.set_title('Average Trial Time by Training Mode')
        ax1.set_ylabel('Time (seconds)')
        ax1.grid(True, alpha=0.3)
        
        # Color bars differently
        bars[0].set_color('skyblue')
        if len(bars) > 1:
            bars[1].set_color('orange')
        
        # Timing vs ensemble size
        ax2 = axes[0, 1]
        for mode in df['training_mode'].unique():
            mode_data = df[df['training_mode'] == mode]
            ax2.scatter(mode_data['ensemble_size'], mode_data['avg_trial_time'], 
                       label=mode, alpha=0.7, s=80)
        ax2.set_xlabel('Ensemble Size')
        ax2.set_ylabel('Average Trial Time (s)')
        ax2.set_title('Trial Time vs Ensemble Size')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Total time vs number of trials
        ax3 = axes[1, 0]
        for mode in df['training_mode'].unique():
            mode_data = df[df['training_mode'] == mode]
            ax3.scatter(mode_data['num_trials'], mode_data['total_time'], 
                       label=mode, alpha=0.7, s=80)
        ax3.set_xlabel('Number of Trials')
        ax3.set_ylabel('Total Time (s)')
        ax3.set_title('Total Time vs Trial Count')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Efficiency metrics table
        ax4 = axes[1, 1]
        ax4.axis('tight')
        ax4.axis('off')
        
        efficiency_data = []
        for mode in df['training_mode'].unique():
            mode_data = df[df['training_mode'] == mode]
            if not mode_data.empty:
                efficiency_data.extend([
                    [f'{mode} Mode', '', ''],
                    ['Avg Trial Time', f"{mode_data['avg_trial_time'].mean():.1f}s", f"±{mode_data['avg_trial_time'].std():.1f}s"],
                    ['Time per Model', f"{(mode_data['avg_trial_time'] / mode_data['ensemble_size']).mean():.2f}s", ''],
                    ['Runs Count', f"{len(mode_data)}", ''],
                    ['', '', '']
                ])
        
        if efficiency_data:
            table = ax4.table(cellText=efficiency_data[:-1],  # Remove last empty row
                             colLabels=['Metric', 'Mean', 'Std'],
                             cellLoc='center',
                             loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(9)
            table.scale(1.2, 1.5)
        ax4.set_title('Efficiency Summary')
        
        plt.tight_layout()
        timing_path = self.output_dir / 'timing_analysis.png'
        plt.savefig(timing_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Timing analysis saved: {timing_path}")
        
    def generate_html_report(self) -> None:
        """Generate an interactive HTML report"""
        
        if not self.runs_data:
            return
            
        print("Generating HTML report...")
        
        df = self._create_summary_dataframe()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AE Optimization Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; 
                   background-color: #e8f4fd; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .plot {{ text-align: center; margin: 20px 0; }}
        .best {{ background-color: #d4edda; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AE Optimization Results Dashboard</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Runs Analyzed: {len(self.runs_data)}</p>
    </div>
    
    <div class="section">
        <h2>Summary Metrics</h2>
        <div class="metric">
            <strong>Best Soft F1:</strong> {df['soft_f1'].max():.4f}
        </div>
        <div class="metric">
            <strong>Best Soft Recall:</strong> {df['soft_recall'].max():.4f}
        </div>
        <div class="metric">
            <strong>Best Soft Precision:</strong> {df['soft_precision'].max():.4f}
        </div>
        <div class="metric">
            <strong>Avg Trial Time:</strong> {df['avg_trial_time'].mean():.1f}s
        </div>
    </div>
    
    <div class="section plot">
        <h2>Visualizations</h2>
        <img src="summary_dashboard.png" alt="Summary Dashboard" style="max-width: 100%;">
        <br><br>
        <img src="performance_trends.png" alt="Performance Trends" style="max-width: 100%;">
        <br><br>
        <img src="timing_analysis.png" alt="Timing Analysis" style="max-width: 100%;">
        <br><br>
        <img src="parameter_heatmap.png" alt="Parameter Heatmap" style="max-width: 100%;">
    </div>
    
    <div class="section">
        <h2>Detailed Results</h2>
        <table>
            <tr>
                <th>Run ID</th>
                <th>Timestamp</th>
                <th>Soft F1</th>
                <th>Soft Recall</th>
                <th>Soft Precision</th>
                <th>Trials</th>
                <th>Ensemble Size</th>
                <th>Training Mode</th>
                <th>Avg Trial Time</th>
            </tr>
"""
        
        for _, row in df.iterrows():
            best_class = ""
            if row['soft_f1'] == df['soft_f1'].max():
                best_class = ' class="best"'
                
            html_content += f"""
            <tr{best_class}>
                <td>{row['run_id']}</td>
                <td>{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{row['soft_f1']:.4f}</td>
                <td>{row['soft_recall']:.4f}</td>
                <td>{row['soft_precision']:.4f}</td>
                <td>{row['num_trials']}</td>
                <td>{row['ensemble_size']}</td>
                <td>{row['training_mode']}</td>
                <td>{row['avg_trial_time']:.1f}s</td>
            </tr>
            """
            
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2>Available Plots by Run</h2>
        <ul>
"""
        
        for run in self.runs_data:
            html_content += f"<li><strong>{run.run_id}:</strong> {', '.join(run.plots_available)}</li>"
            
        html_content += """
        </ul>
    </div>
    
</body>
</html>
"""
        
        html_path = self.output_dir / 'results_report.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
            
        print(f"✓ HTML report saved: {html_path}")
        
    def print_summary_stats(self) -> None:
        """Print summary statistics to console"""
        
        if not self.runs_data:
            print("No run data available.")
            return
            
        df = self._create_summary_dataframe()
        
        print("\n" + "="*60)
        print("AE OPTIMIZATION RESULTS SUMMARY")
        print("="*60)
        
        print(f"\nTotal Runs: {len(self.runs_data)}")
        print(f"Date Range: {df['timestamp'].min().strftime('%Y-%m-%d')} to {df['timestamp'].max().strftime('%Y-%m-%d')}")
        
        print(f"\nBest Performance:")
        best_f1_idx = df['soft_f1'].idxmax()
        print(f"  Soft F1:      {df['soft_f1'].max():.4f} ({df.loc[best_f1_idx, 'run_id']})")
        
        best_recall_idx = df['soft_recall'].idxmax()
        print(f"  Soft Recall:  {df['soft_recall'].max():.4f} ({df.loc[best_recall_idx, 'run_id']})")
        
        best_precision_idx = df['soft_precision'].idxmax()
        print(f"  Soft Precision: {df['soft_precision'].max():.4f} ({df.loc[best_precision_idx, 'run_id']})")
        
        print(f"\nAverage Performance:")
        print(f"  Soft F1:      {df['soft_f1'].mean():.4f} ± {df['soft_f1'].std():.4f}")
        print(f"  Soft Recall:  {df['soft_recall'].mean():.4f} ± {df['soft_recall'].std():.4f}")
        print(f"  Soft Precision: {df['soft_precision'].mean():.4f} ± {df['soft_precision'].std():.4f}")
        
        print(f"\nTiming Statistics:")
        print(f"  Avg Trial Time: {df['avg_trial_time'].mean():.1f}s ± {df['avg_trial_time'].std():.1f}s")
        print(f"  Fastest Trial:  {df['avg_trial_time'].min():.1f}s")
        print(f"  Slowest Trial:  {df['avg_trial_time'].max():.1f}s")
        
        mode_counts = df['training_mode'].value_counts()
        print(f"\nTraining Modes:")
        for mode, count in mode_counts.items():
            mode_data = df[df['training_mode'] == mode]
            print(f"  {mode}: {count} runs (avg {mode_data['avg_trial_time'].mean():.1f}s per trial)")
            
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description='AE Output Visualizer')
    parser.add_argument('--src-outputs', default='outputs', 
                       help='Path to outputs directory')
    parser.add_argument('--output-dir', default='visualizations',
                       help='Output directory for visualizations')
    parser.add_argument('--no-plots', action='store_true',
                       help='Skip plot generation')
    parser.add_argument('--no-html', action='store_true',
                       help='Skip HTML report generation')
    
    args = parser.parse_args()
    
    # Create visualizer
    visualizer = OutputVisualizer(args.src_outputs, args.output_dir)
    
    # Scan and load data
    visualizer.scan_outputs_directory()
    
    if not visualizer.runs_data:
        print("No optimization runs found. Please check the path to src/outputs directory.")
        return
        
    # Print summary statistics
    visualizer.print_summary_stats()
    
    # Generate visualizations
    if not args.no_plots:
        visualizer.create_summary_dashboard()
        visualizer.create_detailed_comparison()
        
    # Generate HTML report
    if not args.no_html:
        visualizer.generate_html_report()
        
    print(f"\n✓ Visualization complete! Check the '{args.output_dir}' directory for results.")
    
if __name__ == "__main__":
    main()