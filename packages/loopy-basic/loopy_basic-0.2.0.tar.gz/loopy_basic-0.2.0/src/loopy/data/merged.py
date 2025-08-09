"""
Merged CGM and Pump Settings Data Module

This module provides functionality to merge CGM readings with active pump settings
at each reading time. This enables analysis of the relationship between pump settings
and glucose outcomes.

Key features:
- Merges CGM readings with active basal rates, carb ratios, and insulin sensitivity factors
- Handles time-based pump settings (different settings for different times of day)
- Provides enriched dataframes for correlation analysis and time series analysis
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, time
import pandas as pd
import numpy as np
from ..connection.mongodb import MongoDBConnection
from .cgm import CGMDataAccess
from .pump import PumpDataAccess

# Configure pandas to use PyArrow backend for better performance
try:
    pd.options.mode.dtype_backend = "pyarrow"
except:
    print("PyArrow backend not available, using default pandas backend")


class MergedDataAccess:
    """Merges CGM data with active pump settings at each reading time.
    
    This class provides methods to retrieve CGM readings enriched with the pump
    settings that were active at the time of each reading. This enables analysis
    of how different settings affect glucose outcomes.
    
    The merged data includes:
    - CGM glucose values and trends
    - Active basal rate at the time
    - Active carb ratio at the time
    - Active insulin sensitivity factor at the time
    - Recent insulin and carb events (for context)
    
    Example:
        with MergedDataAccess() as merged:
            # Get CGM data with active settings for each reading
            df = merged.get_merged_cgm_and_settings(days=7)
            
            # Each row has glucose value + all active settings at that time
            print(df[['dateTime', 'glucose', 'active_basal', 'active_carb_ratio', 
                     'active_isf']].head())
    """
    
    def __init__(self) -> None:
        """Initialize merged data access with CGM and pump data connections."""
        self.cgm = CGMDataAccess()
        self.pump = PumpDataAccess()
        self.db_conn = MongoDBConnection()
        self.database = None
        
        # Cache for pump settings to avoid repeated queries
        self._basal_profile_cache = None
        self._carb_ratio_cache = None
        self._isf_cache = None
        self._profile_cache_time = None
    
    def __enter__(self) -> MergedDataAccess:
        """Context manager entry - connect to database."""
        if not self.connect():
            raise ConnectionError("Failed to connect to MongoDB database")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - disconnect from database."""
        self.disconnect()
    
    def connect(self) -> bool:
        """Connect to the MongoDB database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        # Connect all data sources
        if not self.cgm.connect():
            return False
        if not self.pump.connect():
            self.cgm.disconnect()
            return False
        if not self.db_conn.connect():
            self.cgm.disconnect()
            self.pump.disconnect()
            return False
            
        self.database = self.db_conn.database
        return True
    
    def disconnect(self) -> None:
        """Disconnect from the MongoDB database."""
        if self.cgm:
            self.cgm.disconnect()
        if self.pump:
            self.pump.disconnect()
        if self.db_conn:
            self.db_conn.disconnect()
            self.database = None
    
    def _refresh_profile_cache(self) -> None:
        """Refresh the cached pump profile settings.
        
        Settings are cached for 5 minutes to avoid repeated database queries.
        """
        now = datetime.now()
        
        # Check if cache is still valid (5 minute TTL)
        if (self._profile_cache_time is not None and 
            (now - self._profile_cache_time).seconds < 300):
            return
        
        # Refresh cache
        self._basal_profile_cache = self.pump.get_basal_profile()
        self._carb_ratio_cache = self.pump.get_carb_ratio_profile()
        self._isf_cache = self.pump.get_insulin_sensitivity_profile()
        self._profile_cache_time = now
    
    def get_active_basal_at_time(self, dt: datetime) -> Optional[float]:
        """Get the basal rate that was active at a specific time.
        
        Args:
            dt: The datetime to look up
            
        Returns:
            The basal rate in units/hour, or None if not found
        """
        try:
            self._refresh_profile_cache()
            
            if not self._basal_profile_cache:
                return None
        except Exception as e:
            print(f"Warning: Could not refresh profile cache: {e}")
            return None
        
        # Extract time of day from datetime
        time_of_day = dt.time()
        
        # Find the applicable basal rate for this time
        # Basal profiles have 'time' (HH:MM:SS format) and 'value' fields
        active_rate = None
        
        for i, entry in enumerate(self._basal_profile_cache):
            # Parse the time string (format: "HH:MM:SS" or seconds since midnight)
            if 'time' in entry:
                # Handle time string format
                entry_time_str = entry['time']
                if ':' in entry_time_str:
                    time_parts = entry_time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    entry_time = time(hour, minute, second)
                else:
                    # Handle seconds since midnight format
                    seconds = int(entry['time'])
                    hour = seconds // 3600
                    minute = (seconds % 3600) // 60
                    second = seconds % 60
                    entry_time = time(hour, minute, second)
            elif 'timeAsSeconds' in entry:
                # Handle seconds since midnight
                seconds = entry['timeAsSeconds']
                hour = seconds // 3600
                minute = (seconds % 3600) // 60
                second = seconds % 60
                entry_time = time(hour, minute, second)
            else:
                continue
            
            # Check if this entry applies to our time
            if i + 1 < len(self._basal_profile_cache):
                # Not the last entry - check if we're before the next entry
                next_entry = self._basal_profile_cache[i + 1]
                if 'time' in next_entry:
                    next_time_str = next_entry['time']
                    if ':' in next_time_str:
                        time_parts = next_time_str.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                        next_time = time(hour, minute, second)
                    else:
                        seconds = int(next_entry['time'])
                        hour = seconds // 3600
                        minute = (seconds % 3600) // 60
                        second = seconds % 60
                        next_time = time(hour, minute, second)
                elif 'timeAsSeconds' in next_entry:
                    seconds = next_entry['timeAsSeconds']
                    hour = seconds // 3600
                    minute = (seconds % 3600) // 60
                    second = seconds % 60
                    next_time = time(hour, minute, second)
                else:
                    next_time = time(23, 59, 59)
                
                if entry_time <= time_of_day < next_time:
                    active_rate = entry.get('value')
                    break
            else:
                # Last entry - applies from this time until midnight
                if entry_time <= time_of_day:
                    active_rate = entry.get('value')
                    break
        
        # If no rate found and time is before first entry, use last entry (wraps around midnight)
        if active_rate is None and self._basal_profile_cache:
            active_rate = self._basal_profile_cache[-1].get('value')
        
        return active_rate
    
    def get_active_carb_ratio_at_time(self, dt: datetime) -> Optional[float]:
        """Get the carb ratio that was active at a specific time.
        
        Args:
            dt: The datetime to look up
            
        Returns:
            The carb ratio (grams per unit), or None if not found
        """
        self._refresh_profile_cache()
        
        if not self._carb_ratio_cache:
            return None
        
        # Similar logic to basal rates
        time_of_day = dt.time()
        active_ratio = None
        
        for i, entry in enumerate(self._carb_ratio_cache):
            # Parse the time
            if 'time' in entry:
                entry_time_str = entry['time']
                if ':' in entry_time_str:
                    time_parts = entry_time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    entry_time = time(hour, minute, second)
                else:
                    seconds = int(entry['time'])
                    hour = seconds // 3600
                    minute = (seconds % 3600) // 60
                    second = seconds % 60
                    entry_time = time(hour, minute, second)
            elif 'timeAsSeconds' in entry:
                seconds = entry['timeAsSeconds']
                hour = seconds // 3600
                minute = (seconds % 3600) // 60
                second = seconds % 60
                entry_time = time(hour, minute, second)
            else:
                continue
            
            # Check if this entry applies
            if i + 1 < len(self._carb_ratio_cache):
                next_entry = self._carb_ratio_cache[i + 1]
                if 'time' in next_entry:
                    next_time_str = next_entry['time']
                    if ':' in next_time_str:
                        time_parts = next_time_str.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                        next_time = time(hour, minute, second)
                    else:
                        seconds = int(next_entry['time'])
                        hour = seconds // 3600
                        minute = (seconds % 3600) // 60
                        second = seconds % 60
                        next_time = time(hour, minute, second)
                elif 'timeAsSeconds' in next_entry:
                    seconds = next_entry['timeAsSeconds']
                    hour = seconds // 3600
                    minute = (seconds % 3600) // 60
                    second = seconds % 60
                    next_time = time(hour, minute, second)
                else:
                    next_time = time(23, 59, 59)
                
                if entry_time <= time_of_day < next_time:
                    active_ratio = entry.get('value')
                    break
            else:
                if entry_time <= time_of_day:
                    active_ratio = entry.get('value')
                    break
        
        if active_ratio is None and self._carb_ratio_cache:
            active_ratio = self._carb_ratio_cache[-1].get('value')
        
        return active_ratio
    
    def get_active_isf_at_time(self, dt: datetime) -> Optional[float]:
        """Get the insulin sensitivity factor that was active at a specific time.
        
        Args:
            dt: The datetime to look up
            
        Returns:
            The ISF (mg/dL per unit), or None if not found
        """
        self._refresh_profile_cache()
        
        if not self._isf_cache:
            return None
        
        # Similar logic to basal rates
        time_of_day = dt.time()
        active_isf = None
        
        for i, entry in enumerate(self._isf_cache):
            # Parse the time
            if 'time' in entry:
                entry_time_str = entry['time']
                if ':' in entry_time_str:
                    time_parts = entry_time_str.split(':')
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                    second = int(time_parts[2]) if len(time_parts) > 2 else 0
                    entry_time = time(hour, minute, second)
                else:
                    seconds = int(entry['time'])
                    hour = seconds // 3600
                    minute = (seconds % 3600) // 60
                    second = seconds % 60
                    entry_time = time(hour, minute, second)
            elif 'timeAsSeconds' in entry:
                seconds = entry['timeAsSeconds']
                hour = seconds // 3600
                minute = (seconds % 3600) // 60
                second = seconds % 60
                entry_time = time(hour, minute, second)
            else:
                continue
            
            # Check if this entry applies
            if i + 1 < len(self._isf_cache):
                next_entry = self._isf_cache[i + 1]
                if 'time' in next_entry:
                    next_time_str = next_entry['time']
                    if ':' in next_time_str:
                        time_parts = next_time_str.split(':')
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        second = int(time_parts[2]) if len(time_parts) > 2 else 0
                        next_time = time(hour, minute, second)
                    else:
                        seconds = int(next_entry['time'])
                        hour = seconds // 3600
                        minute = (seconds % 3600) // 60
                        second = seconds % 60
                        next_time = time(hour, minute, second)
                elif 'timeAsSeconds' in next_entry:
                    seconds = next_entry['timeAsSeconds']
                    hour = seconds // 3600
                    minute = (seconds % 3600) // 60
                    second = seconds % 60
                    next_time = time(hour, minute, second)
                else:
                    next_time = time(23, 59, 59)
                
                if entry_time <= time_of_day < next_time:
                    active_isf = entry.get('value')
                    break
            else:
                if entry_time <= time_of_day:
                    active_isf = entry.get('value')
                    break
        
        if active_isf is None and self._isf_cache:
            active_isf = self._isf_cache[-1].get('value')
        
        return active_isf
    
    def get_merged_cgm_and_settings(self, days: int = 7) -> pd.DataFrame:
        """Get CGM data merged with active pump settings for each reading.
        
        This is the main method for getting analysis-ready data. Each CGM reading
        is enriched with the pump settings that were active at that time.
        
        Args:
            days: Number of days of data to retrieve
            
        Returns:
            DataFrame with columns:
                - dateTime: Timestamp of CGM reading
                - glucose: Glucose value (mg/dL)
                - trend: Glucose trend indicator
                - active_basal: Basal rate active at this time (units/hour)
                - active_carb_ratio: Carb ratio active at this time (g/unit)
                - active_isf: Insulin sensitivity factor active at this time (mg/dL per unit)
                - hour_of_day: Hour of day (0-23)
                - day_of_week: Day of week (0=Monday, 6=Sunday)
        """
        # Get CGM data using the correct period types
        if days == 1:
            period_type = 'last_24h'
        elif days <= 7:
            period_type = 'last_week'
        elif days <= 30:
            period_type = 'last_month'
        else:
            # For more than 30 days, use custom period
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            cgm_df = self.cgm.get_dataframe_for_period(
                'custom', start_date=start_date, end_date=end_date
            )
            
        if days <= 30:
            cgm_df = self.cgm.get_dataframe_for_period(period_type)
        
        if cgm_df.empty:
            return pd.DataFrame()
        
        # Check what columns are available in the CGM dataframe
        print(f"CGM DataFrame columns: {list(cgm_df.columns)}")
        
        # Use the correct datetime column name - prefer 'datetime' if available
        datetime_col = None
        for col in ['dateTime', 'datetime', 'date_time']:
            if col in cgm_df.columns:
                datetime_col = col
                break
        
        if datetime_col is None:
            # Find the datetime column
            datetime_cols = [col for col in cgm_df.columns if 'date' in col.lower() and 'time' in col.lower()]
            if datetime_cols:
                datetime_col = datetime_cols[0]
            else:
                raise ValueError(f"No datetime column found in CGM data. Available columns: {list(cgm_df.columns)}")
        
        # Ensure the datetime column is properly converted
        if not pd.api.types.is_datetime64_any_dtype(cgm_df[datetime_col]):
            cgm_df[datetime_col] = pd.to_datetime(cgm_df[datetime_col])
        
        # Add active settings for each CGM reading
        cgm_df['active_basal'] = cgm_df[datetime_col].apply(self.get_active_basal_at_time)
        cgm_df['active_carb_ratio'] = cgm_df[datetime_col].apply(self.get_active_carb_ratio_at_time)
        cgm_df['active_isf'] = cgm_df[datetime_col].apply(self.get_active_isf_at_time)
        
        # Add time-based features for analysis
        cgm_df['hour_of_day'] = cgm_df[datetime_col].dt.hour
        cgm_df['day_of_week'] = cgm_df[datetime_col].dt.dayofweek
        cgm_df['time_of_day_category'] = pd.cut(
            cgm_df['hour_of_day'],
            bins=[0, 6, 12, 18, 24],
            labels=['Night', 'Morning', 'Afternoon', 'Evening'],
            include_lowest=True
        )
        
        # Ensure we have a consistent 'dateTime' column for downstream usage
        if datetime_col != 'dateTime':
            cgm_df['dateTime'] = cgm_df[datetime_col]
        
        return cgm_df
    
    def get_merged_with_recent_treatments(self, days: int = 7, 
                                         lookback_hours: int = 4) -> pd.DataFrame:
        """Get CGM data with settings and recent treatment context.
        
        This method adds information about recent insulin and carb events to provide
        context for each CGM reading. This is useful for understanding the impact
        of recent treatments on glucose levels.
        
        Args:
            days: Number of days of data to retrieve
            lookback_hours: How many hours to look back for recent treatments
            
        Returns:
            DataFrame with CGM readings, active settings, and recent treatment info
        """
        # Get base merged data
        df = self.get_merged_cgm_and_settings(days=days)
        
        if df.empty:
            return df
        
        # Get treatments for the same period plus lookback
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 1)  # Extra day for lookback
        
        # Get treatments data using correct period format
        if days + 1 == 1:
            treatments_df = self.pump.get_dataframe_for_period('last_24h')
        elif days + 1 <= 7:
            treatments_df = self.pump.get_dataframe_for_period('last_week')
        elif days + 1 <= 30:
            treatments_df = self.pump.get_dataframe_for_period('last_month')
        else:
            treatments_df = self.pump.get_dataframe_for_period('last_3_months')
        
        if not treatments_df.empty and 'dateTime' in treatments_df.columns:
            # For each CGM reading, calculate recent insulin and carbs
            recent_insulin = []
            recent_carbs = []
            
            for _, cgm_row in df.iterrows():
                cgm_time = cgm_row['dateTime']
                lookback_start = cgm_time - timedelta(hours=lookback_hours)
                
                # Find treatments in lookback window
                mask = (treatments_df['dateTime'] >= lookback_start) & \
                       (treatments_df['dateTime'] <= cgm_time)
                recent_treatments = treatments_df[mask]
                
                # Sum recent insulin
                if 'insulin' in recent_treatments.columns:
                    insulin_sum = recent_treatments['insulin'].sum()
                    recent_insulin.append(insulin_sum if not pd.isna(insulin_sum) else 0)
                else:
                    recent_insulin.append(0)
                
                # Sum recent carbs
                if 'carbs' in recent_treatments.columns:
                    carbs_sum = recent_treatments['carbs'].sum()
                    recent_carbs.append(carbs_sum if not pd.isna(carbs_sum) else 0)
                else:
                    recent_carbs.append(0)
            
            df[f'insulin_last_{lookback_hours}h'] = recent_insulin
            df[f'carbs_last_{lookback_hours}h'] = recent_carbs
        
        return df
    
    def analyze_settings_correlation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze correlation between pump settings and glucose outcomes.
        
        Args:
            df: Merged dataframe from get_merged_cgm_and_settings()
            
        Returns:
            Dictionary with correlation analysis results
        """
        if df.empty:
            return {'error': 'No data available for analysis'}
        
        # Determine glucose column name
        glucose_col = 'glucose' if 'glucose' in df.columns else 'sgv'
        
        analysis = {
            'data_summary': {
                'total_readings': len(df),
                'date_range': {
                    'start': df['dateTime'].min().isoformat(),
                    'end': df['dateTime'].max().isoformat()
                },
                'glucose_stats': {
                    'mean': float(df[glucose_col].mean()),
                    'std': float(df[glucose_col].std()),
                    'min': float(df[glucose_col].min()),
                    'max': float(df[glucose_col].max()),
                    'in_range_70_180': float((df[glucose_col].between(70, 180).sum() / len(df)) * 100)
                }
            }
        }
        
        # Analyze by different basal rates
        if 'active_basal' in df.columns and df['active_basal'].notna().any():
            basal_groups = df.groupby('active_basal')[glucose_col].agg(['mean', 'std', 'count'])
            analysis['basal_rate_analysis'] = basal_groups.to_dict('index')
        
        # Analyze by carb ratio
        if 'active_carb_ratio' in df.columns and df['active_carb_ratio'].notna().any():
            carb_ratio_groups = df.groupby('active_carb_ratio')[glucose_col].agg(['mean', 'std', 'count'])
            analysis['carb_ratio_analysis'] = carb_ratio_groups.to_dict('index')
        
        # Analyze by ISF
        if 'active_isf' in df.columns and df['active_isf'].notna().any():
            isf_groups = df.groupby('active_isf')[glucose_col].agg(['mean', 'std', 'count'])
            analysis['isf_analysis'] = isf_groups.to_dict('index')
        
        # Time of day patterns with settings
        if 'hour_of_day' in df.columns:
            hourly = df.groupby('hour_of_day').agg({
                glucose_col: ['mean', 'std'],
                'active_basal': 'first',
                'active_carb_ratio': 'first',
                'active_isf': 'first'
            })
            analysis['hourly_patterns'] = hourly.to_dict()
        
        # Calculate correlations if numeric columns exist
        numeric_cols = [glucose_col, 'active_basal', 'active_carb_ratio', 'active_isf']
        numeric_df = df[numeric_cols].select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            correlations = numeric_df.corr()[glucose_col].drop(glucose_col).to_dict()
            analysis['correlations'] = correlations
        
        return analysis


def main():
    """Test the merged data access functionality."""
    print("Testing MergedDataAccess module...")
    print("=" * 50)
    
    try:
        with MergedDataAccess() as merged:
            print("✓ Successfully connected to database")
            
            # Get merged data for last 3 days
            df = merged.get_merged_cgm_and_settings(days=3)
            print(f"✓ Retrieved {len(df)} CGM readings with active settings")
            
            if not df.empty:
                # Show sample of merged data
                print("\nSample of merged data:")
                print("-" * 50)
                # Check which glucose column name is used
                glucose_col = 'glucose' if 'glucose' in df.columns else 'sgv'
                sample_cols = ['dateTime', glucose_col, 'active_basal', 
                              'active_carb_ratio', 'active_isf']
                print(df[sample_cols].head())
                
                # Analyze correlations
                analysis = merged.analyze_settings_correlation(df)
                print("\n✓ Correlation analysis complete")
                print(f"  - Mean glucose: {analysis['data_summary']['glucose_stats']['mean']:.1f} mg/dL")
                print(f"  - Time in range (70-180): {analysis['data_summary']['glucose_stats']['in_range_70_180']:.1f}%")
                
                if 'correlations' in analysis:
                    print("\n  Correlations with glucose:")
                    for setting, corr in analysis['correlations'].items():
                        print(f"    - {setting}: {corr:.3f}")
            
            print("\n✅ All merged data access tests passed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()