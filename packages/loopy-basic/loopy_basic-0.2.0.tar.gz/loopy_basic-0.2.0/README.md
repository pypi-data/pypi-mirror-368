# Loopy Basic - Type 1 Diabetes Data Analysis

[![PyPI version](https://badge.fury.io/py/loopy-basic.svg)](https://badge.fury.io/py/loopy-basic)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A Python package for accessing and analyzing Type 1 diabetes data from a DIY Loop system stored in MongoDB Atlas. Focuses on CGM (Continuous Glucose Monitor) pattern analysis for diabetes management optimization.

## Features

- 📊 **CGM Data Analysis** - Access and analyze continuous glucose monitor data
- 💉 **Pump Data Integration** - Query insulin doses, basal rates, and treatment data  
- 📈 **Time-Series Analysis** - Built-in time-in-range calculations and statistics
- 🔍 **Flexible Queries** - Predefined periods or custom date ranges
- 🚀 **High Performance** - PyArrow-backed DataFrames for efficient processing
- 🔐 **Secure** - Environment-based configuration for credentials

## Project Structure

```
src/loopy/
├── connection/    # Database connectivity
│   └── mongodb.py
├── data/          # Data access modules
│   └── cgm.py
└── utils/         # Utilities and debugging
    └── debug.py
docs/              # Analysis documentation
dev/               # Development and analysis scripts
├── exploratory/   # Exploratory analysis notebooks
├── reports/       # Analysis reports  
└── usage_example.py # Complete usage demonstration
tests/             # Test modules
```

## Installation

### Recommended: Install with uv (fast, modern Python package manager)

```bash
# Install uv first if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install loopy-basic
uv add loopy-basic

# Or install directly without adding to project
uv tool install loopy-basic
```

### Alternative: Install with pip

```bash
# Install the latest version from PyPI
pip install loopy-basic
```

### Install from Source (for development)

```bash
# Clone the repository
git clone <repository-url>
cd loopy-basic

# Install dependencies using uv (recommended)
uv sync

# Install package in editable mode for development
uv pip install -e .
```

## Quick Start

### 1. Set Up MongoDB Connection

Create a `.env` file in your project directory with your MongoDB Atlas credentials:

```env
MONGODB_USERNAME=your_actual_username
MONGODB_PW=your_actual_password
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.yourcluster.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
MONGODB_DATABASE=myCGMitc
```

**Important Notes:**
- Keep the `<username>` and `<password>` placeholders in the URI exactly as shown - the code automatically replaces them
- Only change the cluster URL part (after the @ symbol) to match your MongoDB Atlas cluster
- Provide your actual username and password in the separate MONGODB_USERNAME and MONGODB_PW variables
- Ensure the database user has read access to the `myCGMitc` database

### 2. Basic Usage

```python
from loopy.data.cgm import CGMDataAccess
from loopy.data.pump import PumpDataAccess
from datetime import datetime, timedelta

# Initialize CGM data access
cgm = CGMDataAccess()
cgm.connect()

# Get last week's data as a cleaned DataFrame
df = cgm.get_dataframe_for_period('last_week')

# Basic analysis
analysis = cgm.analyze_dataframe(df)
print(f"Average glucose: {analysis['basic_stats']['avg_glucose']:.1f} mg/dL")
print(f"Time in range: {analysis['time_in_range']['normal_percent']:.1f}%")

# Get pump data (insulin treatments)
pump = PumpDataAccess()
pump.connect()
treatments = pump.get_dataframe_for_period('last_24h')

cgm.disconnect()
pump.disconnect()
```

### 3. Test Your Connection

For development installations, you can test the connection:

```bash
# If installed from source with uv
uv run python -m loopy.connection.mongodb

# If installed via pip
python -m loopy.connection.mongodb
```

You should see output like:
```
✓ Connected to MongoDB database: myCGMitc
Available databases: ['myCGMitc', 'test', 'admin', 'local']
Collections in myCGMitc: ['entries', 'treatments', 'food', 'settings', 'devicestatus', 'auth_roles', 'auth_subjects', 'activity', 'profile']
✓ Disconnected from MongoDB
```

## Database Schema

The `myCGMitc` database contains the following collections:

- **`entries`** - CGM/blood glucose readings (primary data for analysis)
- **`treatments`** - Insulin doses and medical treatments
- **`food`** - Food intake and carbohydrate data
- **`settings`** - Loop system configuration
- **`devicestatus`** - Device status and connectivity info
- **`profile`** - User profile and basal rate settings
- **`activity`** - Activity and exercise logs
- **`auth_roles`**, **`auth_subjects`** - Authentication data

### `entries` Collection Schema (CGM Data)

**Collection Stats:**
- Total documents: 243,047 CGM readings
- Date range: March 2023 to July 2025 (~2 years of data)
- Device: Dexcom CGM ("share2")
- Data actively updated (real-time)

**Document Structure:**
```json
{
  "_id": "ObjectId",
  "sgv": 163,                           // Blood glucose value (mg/dL)
  "date": 1678724324000.0,             // Unix timestamp (milliseconds)
  "dateString": "2023-03-13T16:18:44.000Z",  // ISO formatted date
  "trend": 4,                          // Glucose trend indicator (1-7)
  "direction": "Flat",                 // Trend direction text
  "device": "share2",                  // CGM device identifier
  "type": "sgv",                       // Sensor glucose value type
  "utcOffset": 0,                      // UTC offset
  "sysTime": "2023-03-13T16:18:44.000Z"  // System timestamp
}
```

**Key Fields:**
- **`sgv`** - Primary glucose reading in mg/dL
- **`date`** - Unix timestamp for sorting and time-based queries
- **`direction`** - Trend indicators: "Flat", "FortyFiveUp", "FortyFiveDown", "SingleUp", "SingleDown", "DoubleUp", "DoubleDown"
- **`trend`** - Numeric trend value (1-7 scale)

**Database Indexes:**
- Optimized indexes on `date`, `sgv`, `dateString`, `type` for efficient queries

## Development Stages

### ✅ Stage 1: Database Connection
- MongoDB Atlas connection with environment variables
- Basic authentication and connection testing
- Database and collection discovery

### ✅ Stage 2: CGM Data Access
- Connect to `entries` collection for glucose readings
- Explore document structure and schema
- Implement basic data retrieval queries
- Verify data format and field analysis

### ✅ Stage 3: Time-Range Queries
- Implement date/time filtering for CGM data
- Add functions to query specific time periods (24h, week, month, custom ranges)
- Test with various time ranges and validate results
- Summary statistics and data validation

### ✅ Stage 4: Data Processing & DataFrame Integration - COMPLETE
- MongoDB to pandas DataFrames with PyArrow backend
- Efficient data cleaning and validation
- Timestamp conversions and timezone management
- Time-series analysis preparation

### ✅ Stage 5: Pump Data Access - COMPLETE
- Access to insulin treatment data
- Bolus and basal rate queries
- Treatment type filtering
- Insulin and carbohydrate calculations

### 🔄 Current Focus: Pattern Analysis & Insights
- Time-of-day glucose patterns
- Treatment correlation analysis
- Weekly and monthly trends
- Statistical summaries by time period

## Key Files & Commands

**Core Modules:**
- `src/loopy/connection/mongodb.py` - Main MongoDB connection module
- `src/loopy/data/cgm.py` - CGM data access and time-range queries
- `src/loopy/utils/debug.py` - Connection debugging utilities
- `docs/analysis_patterns.md` - Analysis methodology documentation
- `.env.example` - Environment variable template
- `CLAUDE.md` - Development guidance for AI assistants

**Module Testing Commands:**

Recommended with uv:
```bash
# Test database connection
uv run python -m loopy.connection.mongodb

# Test CGM data access and time-range queries  
uv run python -m loopy.data.cgm

# Test pump data access
uv run python -m loopy.data.pump

# Debug connection issues
uv run python -m loopy.utils.debug
```

With pip installations:
```bash
# Test database connection
python -m loopy.connection.mongodb

# Test CGM data access
python -m loopy.data.cgm

# Test pump data access
python -m loopy.data.pump

# Debug connection issues
python -m loopy.utils.debug
```

Development commands (for source installations):
```bash
# Start marimo notebook for exploration
uv run marimo edit dev/exploratory/analysis.py

# Run usage example (3 months of CGM data)
uv run python dev/usage_example.py
```

## Troubleshooting

If you encounter authentication errors:

1. Verify credentials in MongoDB Atlas dashboard
2. Ensure database user has appropriate permissions
3. Check for extra spaces in `.env` file
4. Test connection with MongoDB Compass first
5. Run `uv run python -m loopy.utils.debug` for detailed diagnostics

## Development Standards

This project follows Python best practices for professional coding:

- **Code Quality**: Type hints, comprehensive docstrings, error handling
- **Reproducibility**: Pinned dependencies, environment configuration, deterministic workflows  
- **Documentation**: Detailed docstrings, inline comments, complete setup instructions
- **Testing**: Input validation, data quality checks, comprehensive testing

## Available Data Access Modules

### CGM Data (`loopy.data.cgm.CGMDataAccess`)
- Access continuous glucose monitor readings
- Query by time periods: 'last_24h', 'last_week', 'last_month', 'last_3_months'
- Get pandas DataFrames with PyArrow backend for efficient analysis
- Built-in statistical analysis and time-in-range calculations

### Pump Data (`loopy.data.pump.PumpDataAccess`)
- Access insulin pump treatment data
- Query bolus doses, basal rates, and temporary basals
- Filter by treatment types and time periods
- Calculate insulin on board (IOB) and carbohydrate data

#### Available Event Types
The pump data includes these treatment event types:
- **`Correction Bolus`** - Insulin bolus doses
- **`Carb Correction`** - Carbohydrate entries
- **`Temp Basal`** - Temporary basal rate adjustments
- **`Site Change`** - Pump site/pod changes
- **`Suspend Pump`** - Pump suspension events
- **`Temporary Override`** - Temporary setting overrides

#### Key Pump Methods

```python
from loopy.data.pump import PumpDataAccess

with PumpDataAccess() as pump:
    # Get specific treatment types
    boluses = pump.get_bolus_data(days=7)           # Bolus doses
    basals = pump.get_basal_data(days=7)            # Temp basals
    carbs = pump.get_carb_data(days=7)              # Carb entries
    site_changes = pump.get_site_change_data(days=30)  # Site changes
    
    # Get current pump status
    iob = pump.get_insulin_on_board()               # Current IOB
    cob = pump.get_carbs_on_board()                 # Current COB
    current_basal = pump.get_current_basal_rate()   # Current basal rate
    
    # Get pump profiles/settings
    basal_profile = pump.get_basal_profile()        # Basal rate schedule
    carb_ratios = pump.get_carb_ratio_profile()     # I:C ratios
    sensitivity = pump.get_insulin_sensitivity_profile()  # ISF values
    
    # Get DataFrame with all treatments
    df = pump.get_dataframe_for_period('last_week')
    analysis = pump.analyze_treatments(df)          # Summary statistics
```

## Advanced Usage Examples

### Custom Time Range Queries

```python
from loopy.data.cgm import CGMDataAccess
from datetime import datetime, timedelta

# Initialize and connect
cgm = CGMDataAccess()
cgm.connect()

# Query specific date range
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 1, 31)
january_data = cgm.get_readings_in_range(start_date, end_date)

# Get DataFrame with analysis
df = cgm.to_dataframe(january_data)
analysis = cgm.analyze_dataframe(df)

print(f"January 2024 Statistics:")
print(f"  Average: {analysis['basic_stats']['avg_glucose']:.1f} mg/dL")
print(f"  Std Dev: {analysis['basic_stats']['std_glucose']:.1f}")
print(f"  Time in Range (70-180): {analysis['time_in_range']['normal_percent']:.1f}%")
print(f"  Time High (>180): {analysis['time_in_range']['high_percent']:.1f}%")
print(f"  Time Low (<70): {analysis['time_in_range']['low_percent']:.1f}%")

cgm.disconnect()
```

### Correlating CGM and Pump Data

```python
from loopy.data.cgm import CGMDataAccess
from loopy.data.pump import PumpDataAccess
import pandas as pd

# Initialize both data access objects
cgm = CGMDataAccess()
pump = PumpDataAccess()

cgm.connect()
pump.connect()

# Get data for the same period
period = 'last_week'
cgm_df = cgm.get_dataframe_for_period(period)
pump_df = pump.get_dataframe_for_period(period)

# Filter for bolus doses only
bolus_df = pump_df[pump_df['eventType'] == 'Bolus']

print(f"Week Summary:")
print(f"  CGM Readings: {len(cgm_df)}")
print(f"  Total Boluses: {len(bolus_df)}")
print(f"  Total Insulin: {bolus_df['insulin'].sum():.1f} units")
print(f"  Average Bolus: {bolus_df['insulin'].mean():.2f} units")

cgm.disconnect()
pump.disconnect()
```

### Pattern Analysis by Time of Day

```python
from loopy.data.cgm import CGMDataAccess
import pandas as pd

cgm = CGMDataAccess()
cgm.connect()

# Get a month of data
df = cgm.get_dataframe_for_period('last_month')

# Add hour of day
df['hour'] = df['dateTime'].dt.hour

# Calculate hourly statistics
hourly_stats = df.groupby('hour')['sgv'].agg(['mean', 'std', 'count'])
hourly_stats.columns = ['avg_glucose', 'std_dev', 'num_readings']

print("Hourly Glucose Patterns:")
print(hourly_stats.round(1))

# Find problematic times
high_times = hourly_stats[hourly_stats['avg_glucose'] > 180]
if not high_times.empty:
    print(f"\nHours with average glucose > 180 mg/dL:")
    for hour in high_times.index:
        print(f"  {hour:02d}:00 - Avg: {high_times.loc[hour, 'avg_glucose']:.1f}")

cgm.disconnect()
```

### Pump Data Analysis Examples

#### Daily Insulin and Carb Summary

```python
from loopy.data.pump import PumpDataAccess
import pandas as pd
from datetime import datetime, timedelta

with PumpDataAccess() as pump:
    # Get a week of pump data
    df = pump.get_dataframe_for_period('last_week')
    
    # Analyze treatments
    analysis = pump.analyze_treatments(df)
    
    print("Week Summary:")
    print(f"  Total treatments: {analysis['total_treatments']}")
    print(f"  Date range: {analysis['date_range']['days_span']} days")
    
    if 'insulin_summary' in analysis:
        print(f"\nInsulin Summary:")
        print(f"  Total: {analysis['insulin_summary']['total_insulin']:.1f} units")
        print(f"  Daily average: {analysis['insulin_summary']['total_insulin']/7:.1f} units/day")
        print(f"  Average dose: {analysis['insulin_summary']['avg_dose']:.2f} units")
        print(f"  Range: {analysis['insulin_summary']['min_dose']:.2f} - {analysis['insulin_summary']['max_dose']:.2f} units")
    
    if 'carb_summary' in analysis:
        print(f"\nCarb Summary:")
        print(f"  Total: {analysis['carb_summary']['total_carbs']:.0f}g")
        print(f"  Daily average: {analysis['carb_summary']['total_carbs']/7:.0f}g/day")
        print(f"  Average per entry: {analysis['carb_summary']['avg_carbs']:.1f}g")
```

#### Insulin Patterns by Time of Day

```python
from loopy.data.pump import PumpDataAccess
import pandas as pd

with PumpDataAccess() as pump:
    # Get bolus data for the last month
    boluses = pump.get_bolus_data(days=30)
    
    if boluses:
        # Convert to DataFrame
        bolus_df = pd.DataFrame(boluses)
        bolus_df['dateTime'] = pd.to_datetime(bolus_df['timestamp'])
        bolus_df['hour'] = bolus_df['dateTime'].dt.hour
        
        # Calculate hourly insulin patterns
        hourly_insulin = bolus_df.groupby('hour')['insulin'].agg(['sum', 'mean', 'count'])
        hourly_insulin.columns = ['total_insulin', 'avg_bolus', 'num_boluses']
        
        print("Hourly Insulin Patterns (last 30 days):")
        print(hourly_insulin.round(2))
        
        # Find peak insulin times
        peak_hours = hourly_insulin.nlargest(3, 'total_insulin')
        print(f"\nPeak insulin hours:")
        for hour in peak_hours.index:
            print(f"  {hour:02d}:00 - Total: {peak_hours.loc[hour, 'total_insulin']:.1f}u, "
                  f"Avg: {peak_hours.loc[hour, 'avg_bolus']:.2f}u")
```

#### Pump Settings Review

```python
from loopy.data.pump import PumpDataAccess

with PumpDataAccess() as pump:
    # Get current pump settings
    basal_profile = pump.get_basal_profile()
    carb_ratios = pump.get_carb_ratio_profile()
    isf = pump.get_insulin_sensitivity_profile()
    
    print("Current Pump Settings:")
    
    print("\nBasal Profile:")
    total_basal = 0
    for i, entry in enumerate(basal_profile):
        print(f"  {entry['time']}: {entry['value']} U/hr")
        # Calculate duration until next entry
        if i < len(basal_profile) - 1:
            current_time = pd.to_datetime(f"2024-01-01 {entry['time']}")
            next_time = pd.to_datetime(f"2024-01-01 {basal_profile[i+1]['time']}")
            hours = (next_time - current_time).seconds / 3600
        else:
            # Last entry goes until midnight
            current_time = pd.to_datetime(f"2024-01-01 {entry['time']}")
            hours = (pd.to_datetime("2024-01-02 00:00") - current_time).seconds / 3600
        total_basal += entry['value'] * hours
    
    print(f"  Total daily basal: {total_basal:.1f} units")
    
    print("\nCarb Ratios (I:C):")
    for entry in carb_ratios:
        print(f"  {entry['time']}: 1:{entry['value']}g")
    
    print("\nInsulin Sensitivity Factors (ISF):")
    for entry in isf:
        print(f"  {entry['time']}: {entry['value']} mg/dL per unit")
    
    # Get current status
    iob = pump.get_insulin_on_board()
    cob = pump.get_carbs_on_board()
    print(f"\nCurrent Status:")
    print(f"  IOB: {iob:.2f} units")
    print(f"  COB: {cob:.1f}g")
```

## Package Information

- **PyPI**: [loopy-basic](https://pypi.org/project/loopy-basic/)
- **License**: MIT
- **Python**: 3.12+
- **Dependencies**: pymongo, pandas, pyarrow, python-dotenv, python-dateutil

## Security Notes

- Never commit the `.env` file to version control
- Use read-only database connections when possible
- Store connection credentials securely
- The package does not store or transmit credentials

## Contributing

Contributions are welcome! This is an open-source project aimed at helping the Type 1 diabetes community better understand and manage their condition through data analysis.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](<repository-url>).
