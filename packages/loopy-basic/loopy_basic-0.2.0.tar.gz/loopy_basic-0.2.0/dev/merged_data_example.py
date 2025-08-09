#!/usr/bin/env python
"""
Example: Merging CGM Data with Active Pump Settings

This script demonstrates how to use the MergedDataAccess module to get CGM readings
enriched with the pump settings that were active at each reading time.

This enables analysis of:
- How different basal rates affect glucose levels
- The effectiveness of carb ratios at different times of day
- Insulin sensitivity patterns throughout the day
- Correlations between settings and glucose outcomes

Run with: uv run python dev/merged_data_example.py
"""

from loopy.data.merged import MergedDataAccess
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def main():
    """Demonstrate merged CGM and pump settings analysis."""
    
    print("=" * 80)
    print("CGM DATA WITH ACTIVE PUMP SETTINGS")
    print("=" * 80)
    
    with MergedDataAccess() as merged:
        # Get last 7 days of CGM data with active settings
        print("\nFetching CGM data with active pump settings...")
        df = merged.get_merged_cgm_and_settings(days=7)
        
        if df.empty:
            print("No data available")
            return
        
        print(f"✓ Retrieved {len(df):,} CGM readings")
        print(f"✓ Date range: {df['dateTime'].min()} to {df['dateTime'].max()}")
        
        # Display sample of the merged data
        print("\n" + "=" * 80)
        print("SAMPLE OF MERGED DATA")
        print("=" * 80)
        print("\nEach CGM reading now includes the pump settings active at that time:")
        print("-" * 80)
        
        # Check which glucose column is available
        glucose_col = 'glucose' if 'glucose' in df.columns else 'sgv'
        display_cols = ['dateTime', glucose_col, 'active_basal', 'active_carb_ratio', 'active_isf']
        print(df[display_cols].head(10).to_string())
        
        # Show unique settings values
        print("\n" + "=" * 80)
        print("UNIQUE PUMP SETTINGS IN USE")
        print("=" * 80)
        
        if 'active_basal' in df.columns:
            unique_basal = df['active_basal'].dropna().unique()
            print(f"\nBasal Rates (units/hour): {sorted(unique_basal)}")
        
        if 'active_carb_ratio' in df.columns:
            unique_cr = df['active_carb_ratio'].dropna().unique()
            print(f"Carb Ratios (g/unit): {sorted(unique_cr)}")
        
        if 'active_isf' in df.columns:
            unique_isf = df['active_isf'].dropna().unique()
            print(f"Insulin Sensitivity Factors (mg/dL per unit): {sorted(unique_isf)}")
        
        # Analyze glucose by different settings
        print("\n" + "=" * 80)
        print("GLUCOSE OUTCOMES BY PUMP SETTINGS")
        print("=" * 80)
        
        # Group by basal rate
        if 'active_basal' in df.columns and df['active_basal'].notna().any():
            print("\nAverage Glucose by Basal Rate:")
            print("-" * 40)
            basal_analysis = df.groupby('active_basal')[glucose_col].agg([
                ('Avg Glucose', 'mean'),
                ('Std Dev', 'std'),
                ('Readings', 'count'),
                ('% Time', lambda x: len(x) / len(df) * 100)
            ]).round(1)
            print(basal_analysis.to_string())
        
        # Time patterns with settings
        print("\n" + "=" * 80)
        print("HOURLY PATTERNS WITH SETTINGS")
        print("=" * 80)
        
        hourly = df.groupby('hour_of_day').agg({
            glucose_col: ['mean', 'std', 'count'],
            'active_basal': lambda x: x.mode()[0] if not x.empty else None,
            'active_carb_ratio': lambda x: x.mode()[0] if not x.empty else None,
        }).round(1)
        
        print("\nGlucose patterns by hour with most common settings:")
        print("-" * 60)
        for hour in range(0, 24, 3):  # Show every 3 hours
            if hour in hourly.index:
                row = hourly.loc[hour]
                print(f"{hour:02d}:00 - Glucose: {row[(glucose_col, 'mean')]:.0f} ± {row[(glucose_col, 'std')]:.0f} mg/dL, "
                      f"Basal: {row[('active_basal', '<lambda>')]:.2f} u/h, "
                      f"CR: {row[('active_carb_ratio', '<lambda>')]:.1f} g/u")
        
        # Get data with recent treatments for context
        print("\n" + "=" * 80)
        print("CGM DATA WITH RECENT TREATMENTS")
        print("=" * 80)
        
        df_with_treatments = merged.get_merged_with_recent_treatments(days=1, lookback_hours=3)
        
        if not df_with_treatments.empty:
            print(f"\n✓ Added recent treatment data (3-hour lookback)")
            
            # Show readings where recent insulin was given
            insulin_mask = df_with_treatments['insulin_last_3h'] > 0
            if insulin_mask.any():
                print(f"\nReadings with insulin in prior 3 hours: {insulin_mask.sum()} ({insulin_mask.sum()/len(df_with_treatments)*100:.1f}%)")
                
                # Compare glucose with and without recent insulin
                glucose_col_treat = 'glucose' if 'glucose' in df_with_treatments.columns else 'sgv'
                with_insulin = df_with_treatments[insulin_mask][glucose_col_treat].mean()
                without_insulin = df_with_treatments[~insulin_mask][glucose_col_treat].mean()
                print(f"  Avg glucose WITH recent insulin: {with_insulin:.1f} mg/dL")
                print(f"  Avg glucose WITHOUT recent insulin: {without_insulin:.1f} mg/dL")
        
        # Correlation analysis
        print("\n" + "=" * 80)
        print("CORRELATION ANALYSIS")
        print("=" * 80)
        
        analysis = merged.analyze_settings_correlation(df)
        
        if 'correlations' in analysis:
            print("\nCorrelations with glucose levels:")
            print("-" * 40)
            for setting, correlation in analysis['correlations'].items():
                direction = "positive" if correlation > 0 else "negative"
                strength = "strong" if abs(correlation) > 0.5 else "moderate" if abs(correlation) > 0.3 else "weak"
                print(f"  {setting}: {correlation:+.3f} ({strength} {direction})")
        
        # Summary statistics
        stats = analysis['data_summary']['glucose_stats']
        print(f"\nGlucose Statistics:")
        print(f"  Mean: {stats['mean']:.1f} mg/dL")
        print(f"  Std Dev: {stats['std']:.1f} mg/dL")
        print(f"  Range: {stats['min']:.0f} - {stats['max']:.0f} mg/dL")
        print(f"  Time in Range (70-180): {stats['in_range_70_180']:.1f}%")
        
        # Visualization example
        print("\n" + "=" * 80)
        print("CREATING VISUALIZATION")
        print("=" * 80)
        
        # Create a figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.suptitle('CGM Data with Active Pump Settings Analysis', fontsize=14, fontweight='bold')
        
        # Plot 1: Glucose over time colored by basal rate
        if 'active_basal' in df.columns:
            ax1 = axes[0, 0]
            scatter = ax1.scatter(df['dateTime'], df[glucose_col], 
                                c=df['active_basal'], cmap='viridis', 
                                alpha=0.6, s=10)
            ax1.set_xlabel('Time')
            ax1.set_ylabel('Glucose (mg/dL)')
            ax1.set_title('Glucose Colored by Basal Rate')
            ax1.axhline(y=70, color='red', linestyle='--', alpha=0.3)
            ax1.axhline(y=180, color='red', linestyle='--', alpha=0.3)
            plt.colorbar(scatter, ax=ax1, label='Basal (u/h)')
        
        # Plot 2: Average glucose by hour of day
        ax2 = axes[0, 1]
        hourly_avg = df.groupby('hour_of_day')[glucose_col].mean()
        ax2.plot(hourly_avg.index, hourly_avg.values, marker='o')
        ax2.set_xlabel('Hour of Day')
        ax2.set_ylabel('Average Glucose (mg/dL)')
        ax2.set_title('Daily Glucose Pattern')
        ax2.set_xticks(range(0, 24, 3))
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=70, color='red', linestyle='--', alpha=0.3)
        ax2.axhline(y=180, color='red', linestyle='--', alpha=0.3)
        
        # Plot 3: Glucose distribution by basal rate
        if 'active_basal' in df.columns:
            ax3 = axes[1, 0]
            basal_rates = df['active_basal'].dropna().unique()
            data_by_basal = [df[df['active_basal'] == rate][glucose_col].values 
                            for rate in sorted(basal_rates)]
            ax3.boxplot(data_by_basal, labels=[f"{rate:.2f}" for rate in sorted(basal_rates)])
            ax3.set_xlabel('Basal Rate (u/h)')
            ax3.set_ylabel('Glucose (mg/dL)')
            ax3.set_title('Glucose Distribution by Basal Rate')
            ax3.axhline(y=70, color='red', linestyle='--', alpha=0.3)
            ax3.axhline(y=180, color='red', linestyle='--', alpha=0.3)
        
        # Plot 4: Settings schedule
        ax4 = axes[1, 1]
        hours = range(24)
        basal_by_hour = [merged.get_active_basal_at_time(
            datetime.now().replace(hour=h, minute=0, second=0)) for h in hours]
        ax4.step(hours, basal_by_hour, where='post', label='Basal Rate')
        ax4.set_xlabel('Hour of Day')
        ax4.set_ylabel('Basal Rate (u/h)')
        ax4.set_title('Daily Basal Rate Schedule')
        ax4.set_xticks(range(0, 24, 3))
        ax4.grid(True, alpha=0.3)
        ax4.legend()
        
        plt.tight_layout()
        
        # Save the figure
        output_file = 'cgm_settings_analysis.png'
        plt.savefig(output_file, dpi=100, bbox_inches='tight')
        print(f"\n✓ Visualization saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nKey Insights:")
        print("- Each CGM reading is now paired with its active pump settings")
        print("- You can analyze how different settings affect glucose outcomes")
        print("- Time patterns show which settings are active at different times")
        print("- Correlation analysis reveals relationships between settings and glucose")
        print("\nThis merged data is ready for advanced time series analysis,")
        print("machine learning models, and treatment optimization studies.")


if __name__ == "__main__":
    main()