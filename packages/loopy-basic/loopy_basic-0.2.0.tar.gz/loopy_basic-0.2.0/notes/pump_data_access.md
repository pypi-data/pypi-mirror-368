# Pump Data Access Guide

This document provides guidance on accessing pump data from the MongoDB database used in the Loopy Basic project. It explains the database structure, the collections that contain pump data, and how to query and access this data.

## Database Structure

The MongoDB database contains several collections that store pump-related data:

1. **`treatments`** - Contains insulin dosing records (bolus, basal) and carb entries
2. **`profile`** - Contains pump settings like basal profiles, carb ratios, and insulin sensitivity factors
3. **`devicestatus`** - Contains real-time pump status information
4. **`settings`** - Currently empty, but may contain pump settings in the future

## Pump Data in Collections

### 1. Treatments Collection

The `treatments` collection contains records of insulin doses and carb entries:

- **Bolus Records**:
  - `eventType`: "Correction Bolus"
  - `insulin`: Amount of insulin delivered (units)
  - `timestamp`: When the bolus was delivered

- **Temporary Basal Records**:
  - `eventType`: "Temp Basal"
  - `rate`: Basal rate (units/hour)
  - `duration`: How long the temp basal runs (minutes)
  - `timestamp`: When the temp basal started

- **Carb Correction Records**:
  - `eventType`: "Carb Correction"
  - `carbs`: Amount of carbohydrates (grams)
  - `insulin`: Amount of insulin delivered (units)
  - `timestamp`: When the carb correction was delivered

- **Site Change Records**:
  - `eventType`: "Site Change"
  - `timestamp`: When the site change occurred
  - `notes`: Optional notes about the site change

- **Suspend Pump Records**:
  - `eventType`: "Suspend Pump"
  - `timestamp`: When the pump was suspended
  - `duration`: How long the pump was suspended (minutes)
  - `notes`: Optional notes about the suspension

- **Temporary Override Records**:
  - `eventType`: "Temporary Override"
  - `timestamp`: When the override started
  - `duration`: How long the override lasts (minutes)
  - `reason`: Reason for the override
  - `notes`: Optional notes about the override

### 2. Profile Collection

The `profile` collection contains pump settings organized by profile name:

- **Basal Rate Profile**:
  - Located in `store.[profile_name].basal`
  - Array of time-based settings with `time` and `value` (units/hour)

- **Carb Ratio Profile**:
  - Located in `store.[profile_name].carbratio`
  - Array of time-based settings with `time` and `value` (grams/unit)

- **Insulin Sensitivity Profile**:
  - Located in `store.[profile_name].sens`
  - Array of time-based settings with `time` and `value` (mg/dL per unit)

- **Target Range**:
  - Located in `store.[profile_name].target_low` and `store.[profile_name].target_high`
  - Array of time-based settings with `time` and `value` (mg/dL)

### 3. Devicestatus Collection

The `devicestatus` collection contains real-time pump status information:

- **Pump Information**:
  - Located in the `pump` object
  - Contains `manufacturer`, `model`, `pumpID`, `suspended` status

- **Loop Status**:
  - Located in the `loop` object
  - Contains `iob` (Insulin on Board), `cob` (Carbs on Board)
  - Contains `enacted` with current basal rate information
  - Contains `automaticDoseRecommendation` with bolus recommendations

## Querying Pump Data

### Basic Queries

Here are some basic MongoDB queries to access pump data:

```python
# Get recent bolus treatments
db.treatments.find({"eventType": "Correction Bolus"}).sort("timestamp", -1).limit(10)

# Get recent temp basal treatments
db.treatments.find({"eventType": "Temp Basal"}).sort("timestamp", -1).limit(10)

# Get recent carb correction treatments
db.treatments.find({"eventType": "Carb Correction"}).sort("timestamp", -1).limit(10)

# Get site change records (looking back further since these are less frequent)
db.treatments.find({"eventType": "Site Change"}).sort("timestamp", -1).limit(20)

# Get pump suspension records
db.treatments.find({"eventType": "Suspend Pump"}).sort("timestamp", -1).limit(10)

# Get temporary override records
db.treatments.find({"eventType": "Temporary Override"}).sort("timestamp", -1).limit(10)

# Get current profile settings
db.profile.find().sort("startDate", -1).limit(1)

# Get current pump status
db.devicestatus.find({"pump": {"$exists": true}}).sort("created_at", -1).limit(1)

# Get current IOB and COB
db.devicestatus.find({"loop": {"$exists": true}}).sort("created_at", -1).limit(1)
```

### Time-Based Queries

To query data for a specific time period:

```python
# Get treatments for a specific date range
start_date = "2023-07-01T00:00:00Z"
end_date = "2023-07-02T00:00:00Z"

db.treatments.find({
    "timestamp": {
        "$gte": start_date,
        "$lte": end_date
    }
}).sort("timestamp", 1)
```

## Using the PumpDataAccess Class

The `PumpDataAccess` class in `dev/exploratory/pump_data_access.py` provides a convenient way to access pump data. Here's how to use it:

```python
from dev.exploratory.pump_data_access import PumpDataAccess

# Initialize and connect
pump_data = PumpDataAccess()
pump_data.connect()

try:
    # Get bolus data for the last 7 days
    bolus_data = pump_data.get_bolus_data(days=7)

    # Get basal data for the last day
    basal_data = pump_data.get_basal_data(days=1)

    # Get carb correction data
    carb_data = pump_data.get_carb_data(days=7)

    # Get site change data (looking back 30 days since these are less frequent)
    site_change_data = pump_data.get_site_change_data(days=30)

    # Get pump suspension data
    suspend_data = pump_data.get_suspend_pump_data(days=7)

    # Get temporary override data
    override_data = pump_data.get_temporary_override_data(days=7)

    # Get pump settings
    basal_profile = pump_data.get_basal_profile()
    carb_ratio_profile = pump_data.get_carb_ratio_profile()
    sensitivity_profile = pump_data.get_insulin_sensitivity_profile()

    # Get current pump status
    iob = pump_data.get_insulin_on_board()
    cob = pump_data.get_carbs_on_board()
    current_basal = pump_data.get_current_basal_rate()

finally:
    # Always disconnect when done
    pump_data.disconnect()
```

## Converting to Pandas DataFrames

To convert pump data to pandas DataFrames for analysis:

```python
import pandas as pd

# Convert treatment data to DataFrames
bolus_df = pd.DataFrame(bolus_data)
basal_df = pd.DataFrame(basal_data)
carb_df = pd.DataFrame(carb_data)
site_change_df = pd.DataFrame(site_change_data)
suspend_df = pd.DataFrame(suspend_data)
override_df = pd.DataFrame(override_data)

# Convert profile data to DataFrames
basal_profile_df = pd.DataFrame(basal_profile)
carb_ratio_df = pd.DataFrame(carb_ratio_profile)
sensitivity_df = pd.DataFrame(sensitivity_profile)

# Example: Analyze site changes
if not site_change_df.empty and 'timestamp' in site_change_df.columns:
    site_change_df['datetime'] = pd.to_datetime(site_change_df['timestamp'])
    site_change_df['date'] = site_change_df['datetime'].dt.date
    # Calculate days between site changes
    site_change_df = site_change_df.sort_values('datetime')
    site_change_df['days_since_last'] = (site_change_df['datetime'] - 
                                         site_change_df['datetime'].shift(1)).dt.days
    print(f"Average days between site changes: {site_change_df['days_since_last'].mean():.1f}")
```

## Next Steps for Development

To integrate pump data access into the main Loopy Basic package:

1. Create a new module `src/loopy/data/pump.py` based on the exploratory code
2. Implement a `PumpDataAccess` class with proper error handling and documentation
3. Add methods to convert pump data to pandas DataFrames
4. Add analysis methods for insulin dosing patterns
5. Integrate with the existing CGM data analysis for correlation studies

## Conclusion

The MongoDB database contains rich pump data that can be accessed and analyzed. The main collections to focus on are `treatments` for insulin dosing history, `profile` for pump settings, and `devicestatus` for real-time pump status. The exploratory scripts in the `dev/exploratory` directory provide examples of how to access and work with this data.
