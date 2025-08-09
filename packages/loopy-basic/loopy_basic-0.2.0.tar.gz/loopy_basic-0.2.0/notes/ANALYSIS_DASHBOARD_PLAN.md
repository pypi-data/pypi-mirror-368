# Loopy Analysis Dashboard - Implementation Plan

## Overview

Create a separate repository focused on **pump-CGM correlation analysis** to optimize diabetes treatment settings. This dashboard will use `loopy-basic` as a dependency for data access while implementing sophisticated analysis of how blood glucose responds to pump settings, bolus amounts, and basal rates.

## Repository Structure

```
loopy-analysis/
├── README.md
├── pyproject.toml              # Uses loopy-basic as dependency
├── .env.example
├── .gitignore
├── src/
│   └── loopy_analysis/
│       ├── __init__.py
│       ├── patterns/           # Pattern analysis modules
│       │   ├── __init__.py
│       │   ├── temporal.py     # Time-based patterns
│       │   ├── glycemic.py     # Glucose-specific patterns
│       │   ├── treatment.py    # Treatment correlation patterns
│       │   └── variability.py  # Variability analysis
│       ├── metrics/            # Custom metrics
│       │   ├── __init__.py
│       │   ├── time_in_range.py
│       │   ├── variability.py
│       │   └── risk_scores.py
│       └── visualizations/     # Plotting utilities
│           ├── __init__.py
│           ├── daily_patterns.py
│           ├── heatmaps.py
│           └── trends.py
├── notebooks/                  # Marimo notebooks
│   ├── 01_daily_patterns.py
│   ├── 02_weekly_analysis.py
│   ├── 03_meal_response.py
│   ├── 04_overnight_analysis.py
│   ├── 05_treatment_correlation.py
│   └── 06_custom_exploration.py
├── dashboards/                 # If using Streamlit/Dash
│   ├── streamlit_app.py
│   └── pages/
│       ├── daily_view.py
│       ├── patterns.py
│       └── reports.py
├── reports/                    # Generated analysis reports
│   └── templates/
└── tests/

```

## Primary Analysis Goals

1. **Bolus Response Analysis**
   - How BG responds to different bolus amounts
   - Optimal insulin-to-carb ratios by time of day
   - Pre-bolus timing effectiveness
   - Duration of insulin action patterns

2. **Basal Rate Optimization**
   - Identify periods where basal rates need adjustment
   - Overnight basal testing results
   - Basal rate effectiveness by time blocks
   - Detection of recurring highs/lows at specific times

3. **Insulin Sensitivity Patterns**
   - ISF (Insulin Sensitivity Factor) variations throughout day
   - Impact of exercise, stress, illness on insulin needs
   - Weekend vs weekday insulin requirements
   - Seasonal variations in insulin sensitivity

4. **Treatment Effectiveness Metrics**
   - Success rate of corrections at different BG levels
   - Time to return to range after corrections
   - Frequency of overcorrections leading to lows
   - Comparison of different treatment strategies

## Phase 1: Pump Data Integration & Foundation (Week 1)

### 1.1 Repository Setup
- Create new repository `loopy-analysis`
- Set up dependency on `loopy-basic` via local path or git
- Configure development environment with uv
- Set up pre-commit hooks for code quality

### 1.2 Core Pump-CGM Correlation Module
```python
# src/loopy_analysis/pump_response/bolus.py
class BolusResponseAnalyzer:
    """Analyze BG response to bolus insulin."""
    
    def analyze_bolus_response(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame, 
                              bolus_id: str) -> Dict:
        """Track BG response curve after a specific bolus."""
        return {
            'pre_bolus_bg': 145,
            'peak_action_time': 75,  # minutes
            'total_bg_drop': 65,
            'time_to_target': 120,  # minutes
            'post_meal_spike': 180,
            'effectiveness_score': 0.85
        }
    
    def calculate_optimal_icr(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame,
                             time_block: str) -> Dict:
        """Calculate optimal insulin-to-carb ratio for time period."""
        
    def analyze_prebolus_timing(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Determine optimal pre-bolus timing by meal type."""
```

```python
# src/loopy_analysis/pump_response/basal.py
class BasalAnalyzer:
    """Analyze basal rate effectiveness."""
    
    def identify_basal_issues(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Find time blocks where basal rates need adjustment."""
        return {
            'problem_periods': [
                {'time': '3:00-6:00', 'issue': 'dawn phenomenon', 'suggested_increase': 0.1},
                {'time': '14:00-17:00', 'issue': 'afternoon highs', 'suggested_increase': 0.05}
            ],
            'overnight_stability_score': 0.72,
            'basal_effectiveness_by_hour': {...}
        }
    
    def overnight_basal_test_analysis(self, cgm_df: pd.DataFrame, test_night: date) -> Dict:
        """Analyze overnight basal test results."""
```

### 1.3 Initial Pump Analysis Notebook
Create `notebooks/01_bolus_response_analysis.py` with:
- Synchronized pump and CGM data loading
- Bolus event identification
- BG response curve visualization
- ICR effectiveness calculation
- Interactive bolus comparison tool

## Phase 2: Advanced Pump-CGM Analysis (Week 2-3)

### 2.1 Insulin Sensitivity Analysis
```python
# src/loopy_analysis/pump_response/sensitivity.py
class InsulinSensitivityAnalyzer:
    """Analyze insulin sensitivity factors and patterns."""
    
    def calculate_isf_by_time(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Calculate ISF variations throughout the day."""
        return {
            'morning_isf': 45,  # 1 unit drops BG by 45 mg/dL
            'afternoon_isf': 50,
            'evening_isf': 40,
            'overnight_isf': 55,
            'confidence_scores': {...}
        }
    
    def analyze_correction_effectiveness(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Analyze how well corrections work at different BG levels."""
        
    def identify_resistance_patterns(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Identify times when insulin resistance is higher."""
```

### 2.2 Meal Response Patterns
```python
# src/loopy_analysis/pump_response/meals.py
class MealResponseAnalyzer:
    """Analyze BG response to meals and meal boluses."""
    
    def analyze_meal_response(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame, 
                             meal_time: datetime) -> Dict:
        """Detailed analysis of a specific meal."""
        return {
            'carb_estimate': 45,
            'bolus_amount': 4.5,
            'icr_used': 10,
            'pre_meal_bg': 110,
            'peak_bg': 185,
            'peak_time_minutes': 65,
            'time_above_180': 45,  # minutes
            'return_to_range_time': 180,  # minutes
            'meal_impact_score': 0.75
        }
    
    def compare_meal_strategies(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Compare different bolus strategies (standard, extended, dual wave)."""
        
    def identify_problematic_meals(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> List[Dict]:
        """Find meals that consistently cause BG issues."""
```

### 2.3 Treatment Optimization Recommendations
```python
# src/loopy_analysis/optimization/recommendations.py
class TreatmentOptimizer:
    """Generate specific pump setting recommendations."""
    
    def recommend_basal_adjustments(self, analysis_results: Dict) -> List[Dict]:
        """Suggest specific basal rate changes."""
        return [
            {
                'time_range': '03:00-06:00',
                'current_rate': 0.85,
                'suggested_rate': 0.95,
                'reason': 'Consistent dawn phenomenon, avg BG rise of 40 mg/dL',
                'confidence': 0.89
            }
        ]
    
    def recommend_icr_adjustments(self, analysis_results: Dict) -> List[Dict]:
        """Suggest ICR changes by meal time."""
        
    def recommend_isf_adjustments(self, analysis_results: Dict) -> List[Dict]:
        """Suggest ISF changes based on correction analysis."""
```

## Phase 3: Visualization Suite (Week 3-4)

### 3.1 Pump-Specific Visualizations
```python
# src/loopy_analysis/visualizations/pump_response.py
def plot_bolus_response_curve(cgm_df: pd.DataFrame, pump_df: pd.DataFrame, 
                             bolus_time: datetime) -> go.Figure:
    """Plot BG response curve after a bolus with key metrics annotated."""

def plot_basal_effectiveness_heatmap(cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> go.Figure:
    """Heatmap showing basal rate effectiveness by hour and day."""

def plot_icr_effectiveness_by_meal(analysis_results: List[Dict]) -> go.Figure:
    """Compare ICR effectiveness across different meals/times."""

# src/loopy_analysis/visualizations/treatment_comparison.py
def plot_correction_success_rate(cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> go.Figure:
    """Show success rate of corrections at different starting BG levels."""

def plot_meal_response_comparison(meal_analyses: List[Dict]) -> go.Figure:
    """Compare BG responses to similar meals with different bolus strategies."""

def plot_insulin_on_board_impact(cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> go.Figure:
    """Visualize how IOB affects BG trends and correction effectiveness."""
```

### 3.2 Interactive Dashboards
- Implement Streamlit dashboard with multiple pages
- Real-time data refresh capability
- Export functionality for reports
- Customizable time ranges and filters

## Phase 4: Advanced Pattern Recognition (Week 5-6)

### 4.1 Machine Learning for Pattern Detection
```python
# src/loopy_analysis/ml/pattern_detection.py
class PumpPatternDetector:
    """Use ML to detect complex pump-CGM patterns."""
    
    def detect_recurring_patterns(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> List[Dict]:
        """Find recurring situations where current settings fail."""
        return [
            {
                'pattern': 'Post-breakfast spike after high-protein meals',
                'frequency': '3-4 times/week',
                'avg_spike': 75,
                'suggested_action': 'Extended bolus 60/40 over 2 hours',
                'confidence': 0.82
            }
        ]
    
    def predict_bg_trajectory(self, current_bg: float, iob: float, cob: float) -> Dict:
        """Predict future BG based on current state and active insulin/carbs."""
        
    def cluster_similar_meals(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame) -> Dict:
        """Group meals by similar BG response patterns."""
```

### 4.2 Exercise and Activity Impact
```python
# src/loopy_analysis/factors/activity.py
class ActivityImpactAnalyzer:
    """Analyze how exercise affects insulin needs."""
    
    def analyze_exercise_impact(self, cgm_df: pd.DataFrame, pump_df: pd.DataFrame,
                               activity_data: pd.DataFrame) -> Dict:
        """Quantify exercise impact on insulin sensitivity."""
        
    def recommend_temp_basal_settings(self, exercise_type: str, duration: int) -> Dict:
        """Suggest temp basal settings for different activities."""
```

## Phase 5: Reporting & Insights (Week 7-8)

### 5.1 Automated Report Generation
```python
# src/loopy_analysis/reports/generator.py
class ReportGenerator:
    """Generate comprehensive analysis reports."""
    
    def generate_weekly_report(self, start_date: datetime) -> str:
        """Generate weekly analysis report with insights."""
        
    def generate_pattern_report(self, df: pd.DataFrame) -> str:
        """Generate report focused on identified patterns."""
        
    def export_to_pdf(self, report_data: Dict, output_path: str):
        """Export analysis report as PDF."""
```

### 5.2 Actionable Insights Engine
- Pattern change detection
- Trend identification
- Risk alerts
- Optimization suggestions

## Key Design Principles

1. **Modular Architecture**: Each analysis type in its own module
2. **Reusable Components**: Shared utilities for common operations
3. **Performance First**: Use vectorized operations, caching
4. **Interactive Exploration**: Marimo notebooks for discovery
5. **Production Ready**: Streamlit/Dash for shareable dashboards
6. **Statistical Rigor**: Include confidence intervals, significance tests

## Technology Stack

### Core Dependencies
```toml
[dependencies]
loopy-basic = { path = "../loopy-basic" }  # or git URL
pandas = "^2.2.0"
numpy = "^1.26.0"
scipy = "^1.12.0"          # Statistical analysis
plotly = "^5.18.0"         # Interactive visualizations
marimo = "^0.14.0"         # Interactive notebooks
streamlit = "^1.35.0"      # Web dashboard (optional)
statsmodels = "^0.14.0"    # Advanced statistics
scikit-learn = "^1.5.0"    # ML for pattern detection
```

### Development Dependencies
```toml
[tool.uv.dev-dependencies]
pytest = "^8.0.0"
ruff = "^0.8.0"
mypy = "^1.13.0"
pre-commit = "^4.0.0"
```

## Implementation Tips

1. **Start Simple**: Begin with one pattern analysis type and expand
2. **Test with Real Data**: Use your actual CGM data from the start
3. **Iterate Based on Insights**: Let discoveries guide next features
4. **Document Patterns**: Keep notes on interesting findings
5. **Version Control Analysis**: Track analysis code evolution
6. **Cache Expensive Operations**: Store processed data for quick iteration

## Example Pump Analysis Notebook

```python
# notebooks/01_bolus_response_analysis.py
import marimo as mo
from loopy.data.cgm import CGMDataAccess
from loopy.data.pump import PumpDataAccess
from loopy_analysis.pump_response.bolus import BolusResponseAnalyzer
from loopy_analysis.visualizations.pump_response import plot_bolus_response_curve

# Cell 1: Load synchronized data
with CGMDataAccess() as cgm, PumpDataAccess() as pump:
    cgm_df = cgm.get_dataframe_for_period('last_week')
    pump_df = pump.get_bolus_data_for_period('last_week')

# Cell 2: Analyze recent boluses
analyzer = BolusResponseAnalyzer()
recent_boluses = pump_df[pump_df['type'] == 'normal'].tail(20)

# Cell 3: Interactive bolus selector
selected_bolus = mo.ui.dropdown(
    options={f"{b['timestamp']} - {b['amount']}U": b['id'] 
             for b in recent_boluses.to_dict('records')},
    label="Select a bolus to analyze:"
)

# Cell 4: Analyze selected bolus
if selected_bolus.value:
    response = analyzer.analyze_bolus_response(cgm_df, pump_df, selected_bolus.value)
    fig = plot_bolus_response_curve(cgm_df, pump_df, selected_bolus.value)
    mo.ui.plotly(fig)
    
    mo.md(f"""
    ## Bolus Response Analysis
    - Pre-bolus BG: {response['pre_bolus_bg']} mg/dL
    - Peak action time: {response['peak_action_time']} minutes
    - Total BG drop: {response['total_bg_drop']} mg/dL
    - Effectiveness score: {response['effectiveness_score']:.2f}
    """)

# Cell 5: Generate recommendations
optimizer = TreatmentOptimizer()
recommendations = optimizer.recommend_icr_adjustments(analyzer.get_weekly_summary())
mo.md("## Recommended ICR Adjustments\n" + 
      "\n".join([f"- {r['meal_time']}: {r['current']} → {r['suggested']}" 
                 for r in recommendations]))
```

## Key Analysis Outputs

1. **Bolus Effectiveness Report**
   - ICR performance by time of day
   - Success rate of meal boluses
   - Optimal pre-bolus timing recommendations
   - Problem meals requiring different strategies

2. **Basal Rate Optimization Report**
   - Hour-by-hour basal effectiveness
   - Identified problem time periods
   - Specific rate change recommendations
   - Overnight stability assessment

3. **Insulin Sensitivity Report**
   - ISF variations throughout day
   - Correction bolus effectiveness
   - Factors affecting sensitivity (exercise, stress, etc.)
   - Resistance pattern identification

4. **Treatment Strategy Comparison**
   - Standard vs extended bolus outcomes
   - Temp basal effectiveness for activities
   - IOB impact on corrections
   - Success rates of different approaches

## Success Metrics

1. **Improved Time in Range**: Target 5-10% improvement
2. **Reduced Variability**: Lower standard deviation and CV
3. **Fewer Corrections Needed**: Reduce correction frequency by 20%
4. **Better Meal Outcomes**: 80%+ meals staying under 180 mg/dL
5. **Actionable Insights**: Generate 3-5 specific setting changes per week

## Next Steps

1. Create the new repository
2. Set up development environment
3. Implement first pattern analyzer
4. Create initial marimo notebook
5. Test with your CGM data
6. Iterate based on findings

This modular approach allows you to start simple and expand based on what you discover in your data. The separation from `loopy-basic` keeps both projects focused and maintainable.