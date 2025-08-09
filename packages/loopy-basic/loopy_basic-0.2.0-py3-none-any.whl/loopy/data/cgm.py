from __future__ import annotations

from ..connection.mongodb import MongoDBConnection
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union

# Configure pandas to use PyArrow backend for better performance
try:
    pd.options.mode.dtype_backend = "pyarrow"
except:
    # Fallback if PyArrow backend isn't available in this pandas version
    print("PyArrow backend not available, using default pandas backend")


class CGMDataAccess:
    """Access and query CGM/blood glucose data from the entries collection.
    
    This class provides methods to connect to a MongoDB database containing
    diabetes CGM (Continuous Glucose Monitor) data and retrieve data for analysis.
    Supports context manager protocol for automatic connection management.
    
    Attributes:
        db_conn: MongoDB connection instance
        collection: MongoDB collection reference for CGM entries
        
    Example:
        Basic usage:
            cgm = CGMDataAccess()
            cgm.connect()
            df = cgm.get_dataframe_for_period('last_week')
            cgm.disconnect()
            
        Context manager (recommended):
            with CGMDataAccess() as cgm:
                df = cgm.get_dataframe_for_period('last_week')
    """

    def __init__(self) -> None:
        """Initialize CGM data access with MongoDB connection."""
        self.db_conn = MongoDBConnection()
        self.collection = None
    
    def __enter__(self) -> CGMDataAccess:
        """Context manager entry - connect to database.
        
        Returns:
            Self instance with established database connection
        """
        self.connect()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - disconnect from database.
        
        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred  
            exc_tb: Exception traceback if an exception occurred
        """
        self.disconnect()

    def connect(self) -> bool:
        """Connect to the database and entries collection.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.db_conn.connect():
            self.collection = self.db_conn.database['entries']
            print("✓ Connected to CGM entries collection")
            return True
        return False

    def disconnect(self) -> None:
        """Disconnect from the database."""
        self.db_conn.disconnect()

    def explore_schema(self, limit=5):
        """Explore the structure of documents in the entries collection."""
        if self.collection is None:
            print("✗ Not connected to collection")
            return []

        print(f"=== Exploring entries collection schema ===")

        # Get total document count
        total_docs = self.collection.count_documents({})
        print(f"Total documents in collection: {total_docs}")

        # Get sample documents
        sample_docs = list(self.collection.find().limit(limit))

        print(f"\nSample documents (first {limit}):")
        for i, doc in enumerate(sample_docs, 1):
            print(f"\n--- Document {i} ---")
            print(json.dumps(doc, indent=2, default=str))

        # Analyze field structure
        if sample_docs:
            print(f"\n=== Field Analysis ===")
            all_fields = set()
            for doc in sample_docs:
                all_fields.update(doc.keys())

            print(f"All fields found: {sorted(all_fields)}")

            # Check for common CGM fields
            common_fields = ['sgv', 'glucose', 'bg', 'dateString', 'date', 'type']
            found_fields = [field for field in common_fields if field in all_fields]
            print(f"Common CGM fields found: {found_fields}")

        return sample_docs

    def get_recent_readings(self, limit=10):
        """Get the most recent CGM readings."""
        if self.collection is None:
            print("✗ Not connected to collection")
            return []

        try:
            # Try to sort by date field (common in CGM data)
            readings = list(self.collection.find().sort("date", -1).limit(limit))
            print(f"✓ Retrieved {len(readings)} recent readings")
            return readings
        except Exception as e:
            print(f"✗ Error retrieving readings: {e}")
            return []

    def get_collection_info(self):
        """Get basic information about the entries collection."""
        if self.collection is None:
            print("✗ Not connected to collection")
            return

        print("=== Collection Information ===")

        # Document count
        count = self.collection.count_documents({})
        print(f"Total documents: {count}")

        # Index information
        indexes = list(self.collection.list_indexes())
        print(f"Indexes: {[idx['name'] for idx in indexes]}")

        # Find date range if possible
        try:
            # Try to find oldest and newest documents
            oldest = self.collection.find().sort("date", 1).limit(1)
            newest = self.collection.find().sort("date", -1).limit(1)

            oldest_doc = list(oldest)
            newest_doc = list(newest)

            if oldest_doc and newest_doc:
                print(f"Date range: {oldest_doc[0].get('date')} to {newest_doc[0].get('date')}")
        except Exception as e:
            print(f"Could not determine date range: {e}")

    def get_readings_by_time_range(self, start_time: Union[datetime, int], end_time: Union[datetime, int], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get CGM readings within a specific time range.

        Args:
            start_time: datetime object or Unix timestamp (milliseconds)
            end_time: datetime object or Unix timestamp (milliseconds)
            limit: Optional limit on number of results
        """
        if self.collection is None:
            print("✗ Not connected to collection")
            return []

        # Convert datetime objects to Unix timestamps if needed
        if isinstance(start_time, datetime):
            start_timestamp = int(start_time.timestamp() * 1000)
        else:
            start_timestamp = int(start_time)

        if isinstance(end_time, datetime):
            end_timestamp = int(end_time.timestamp() * 1000)
        else:
            end_timestamp = int(end_time)

        # Query with date range filter
        query = {
            "date": {
                "$gte": start_timestamp,
                "$lte": end_timestamp
            },
            "type": "sgv"  # Only sensor glucose values
        }

        try:
            cursor = self.collection.find(query).sort("date", 1)  # Sort ascending by date
            if limit:
                cursor = cursor.limit(limit)

            readings = list(cursor)
            print(f"✓ Retrieved {len(readings)} readings from {datetime.fromtimestamp(start_timestamp/1000)} to {datetime.fromtimestamp(end_timestamp/1000)}")
            return readings
        except Exception as e:
            print(f"✗ Error querying time range: {e}")
            return []

    def get_last_24_hours(self):
        """Get CGM readings from the last 24 hours."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        return self.get_readings_by_time_range(start_time, end_time)

    def get_last_week(self):
        """Get CGM readings from the last 7 days."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        return self.get_readings_by_time_range(start_time, end_time)

    def get_last_month(self):
        """Get CGM readings from the last 30 days."""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        return self.get_readings_by_time_range(start_time, end_time)

    def get_readings_for_date(self, target_date):
        """Get all CGM readings for a specific date.

        Args:
            target_date: datetime.date object or datetime object
        """
        if hasattr(target_date, 'date'):
            target_date = target_date.date()

        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())

        return self.get_readings_by_time_range(start_time, end_time)

    def get_readings_summary(self, readings):
        """Get summary statistics for a list of readings."""
        if not readings:
            return {"error": "No readings provided"}

        glucose_values = [reading.get('sgv') for reading in readings if reading.get('sgv')]

        if not glucose_values:
            return {"error": "No glucose values found"}

        return {
            "count": len(glucose_values),
            "min": min(glucose_values),
            "max": max(glucose_values),
            "average": round(sum(glucose_values) / len(glucose_values), 1),
            "time_range": {
                "start": readings[0].get('dateString'),
                "end": readings[-1].get('dateString')
            }
        }
    
    def to_dataframe(self, readings: List[Dict[str, Any]], clean_data: bool = True) -> pd.DataFrame:
        """Convert MongoDB readings to pandas DataFrame with PyArrow backend.
        
        Args:
            readings: List of MongoDB documents from CGM collection
            clean_data: Whether to apply data cleaning and validation
            
        Returns:
            pandas.DataFrame: Cleaned and processed CGM data
        """
        if not readings:
            print("✗ No readings provided")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(readings)
        
        if clean_data:
            df = self._clean_dataframe(df)
        
        print(f"✓ Created DataFrame with {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def _clean_dataframe(self, df):
        """Clean and validate CGM DataFrame.
        
        Args:
            df: Raw DataFrame from MongoDB documents
            
        Returns:
            pandas.DataFrame: Cleaned DataFrame
        """
        print("🧹 Cleaning DataFrame...")
        
        # Filter to only sensor glucose values
        df = df[df['type'] == 'sgv'].copy()
        
        # Convert date column to datetime with timezone handling
        df['datetime'] = pd.to_datetime(df['date'], unit='ms', utc=True)
        
        # Convert dateString to datetime for validation
        df['dateString_parsed'] = pd.to_datetime(df['dateString'])
        
        # Remove rows with missing or invalid glucose values
        df = df.dropna(subset=['sgv'])
        df = df[df['sgv'] > 0]  # Remove zero or negative values
        
        # Remove extreme outliers (likely sensor errors)
        glucose_mean = df['sgv'].mean()
        glucose_std = df['sgv'].std()
        lower_bound = max(20, glucose_mean - 4 * glucose_std)  # At least 20 mg/dL
        upper_bound = min(600, glucose_mean + 4 * glucose_std)  # At most 600 mg/dL
        
        outliers_removed = len(df) - len(df[(df['sgv'] >= lower_bound) & (df['sgv'] <= upper_bound)])
        df = df[(df['sgv'] >= lower_bound) & (df['sgv'] <= upper_bound)]
        
        if outliers_removed > 0:
            print(f"  📊 Removed {outliers_removed} outlier readings")
        
        # Sort by timestamp
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Add time-based features for analysis
        df['hour'] = df['datetime'].dt.hour
        df['day_of_week'] = df['datetime'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['date_only'] = df['datetime'].dt.date
        
        # Add glucose level categories for analysis
        df['glucose_category'] = pd.cut(
            df['sgv'], 
            bins=[0, 70, 180, 250, float('inf')], 
            labels=['Low', 'Normal', 'High', 'Very High'],
            right=False
        )
        
        print(f"  ✓ Cleaned data: {len(df)} valid readings")
        print(f"  📈 Glucose range: {df['sgv'].min()}-{df['sgv'].max()} mg/dL")
        print(f"  📅 Time range: {df['datetime'].min()} to {df['datetime'].max()}")
        
        return df
    
    def get_dataframe_for_period(self, period_type: str = 'last_week', start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, clean_data: bool = True) -> pd.DataFrame:
        """Get cleaned DataFrame for a specific time period.
        
        Args:
            period_type: 'last_24h', 'last_week', 'last_month', or 'custom'
            start_date: For custom period (datetime object)
            end_date: For custom period (datetime object)
            clean_data: Whether to apply data cleaning
            
        Returns:
            pandas.DataFrame: Cleaned CGM data for the specified period
        """
        if period_type == 'last_24h':
            readings = self.get_last_24_hours()
        elif period_type == 'last_week':
            readings = self.get_last_week()
        elif period_type == 'last_month':
            readings = self.get_last_month()
        elif period_type == 'custom' and start_date and end_date:
            readings = self.get_readings_by_time_range(start_date, end_date)
        else:
            print("✗ Invalid period_type or missing dates for custom period")
            return pd.DataFrame()
        
        return self.to_dataframe(readings, clean_data=clean_data)
    
    def analyze_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform basic analysis on CGM DataFrame.
        
        Args:
            df: Cleaned CGM DataFrame
            
        Returns:
            dict: Analysis summary
        """
        if df.empty:
            return {"error": "Empty DataFrame"}
        
        analysis = {
            "basic_stats": {
                "total_readings": len(df),
                "avg_glucose": df['sgv'].mean(),
                "median_glucose": df['sgv'].median(),
                "std_glucose": df['sgv'].std(),
                "min_glucose": df['sgv'].min(),
                "max_glucose": df['sgv'].max(),
            },
            "time_in_range": {
                "low_percent": (df['glucose_category'] == 'Low').sum() / len(df) * 100,
                "normal_percent": (df['glucose_category'] == 'Normal').sum() / len(df) * 100,
                "high_percent": (df['glucose_category'] == 'High').sum() / len(df) * 100,
                "very_high_percent": (df['glucose_category'] == 'Very High').sum() / len(df) * 100,
            },
            "temporal_patterns": {
                "avg_by_hour": df.groupby('hour')['sgv'].mean().to_dict(),
                "avg_by_day_of_week": df.groupby('day_of_week')['sgv'].mean().to_dict(),
            },
            "data_quality": {
                "time_span_hours": (df['datetime'].max() - df['datetime'].min()).total_seconds() / 3600,
                "readings_per_day": len(df) / ((df['datetime'].max() - df['datetime'].min()).days + 1),
            }
        }
        
        return analysis


def test_time_range_queries():
    """Test time-range query functionality."""
    print("=== Testing Time-Range Queries ===")

    cgm = CGMDataAccess()

    if cgm.connect():
        # Test last 24 hours
        print("\n--- Last 24 Hours ---")
        last_24h = cgm.get_last_24_hours()
        if last_24h:
            summary = cgm.get_readings_summary(last_24h)
            print(f"Summary: {summary}")

        # Test last week
        print("\n--- Last Week ---")
        last_week = cgm.get_last_week()
        if last_week:
            summary = cgm.get_readings_summary(last_week)
            print(f"Summary: {summary}")

        # Test specific date (yesterday)
        print("\n--- Yesterday's Readings ---")
        yesterday = datetime.now().date() - timedelta(days=1)
        yesterday_readings = cgm.get_readings_for_date(yesterday)
        if yesterday_readings:
            summary = cgm.get_readings_summary(yesterday_readings)
            print(f"Summary: {summary}")

        # Test custom time range (last 6 hours)
        print("\n--- Last 6 Hours (Custom Range) ---")
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=6)
        custom_readings = cgm.get_readings_by_time_range(start_time, end_time)
        if custom_readings:
            summary = cgm.get_readings_summary(custom_readings)
            print(f"Summary: {summary}")

            # Show first and last few readings
            print(f"\nFirst 3 readings:")
            for i, reading in enumerate(custom_readings[:3], 1):
                print(f"  {i}. {reading['sgv']} mg/dL at {reading['dateString']} ({reading['direction']})")

            if len(custom_readings) > 3:
                print(f"\nLast 3 readings:")
                for i, reading in enumerate(custom_readings[-3:], 1):
                    print(f"  {i}. {reading['sgv']} mg/dL at {reading['dateString']} ({reading['direction']})")

        cgm.disconnect()
    else:
        print("Failed to connect to CGM data")


def test_cgm_access():
    """Test CGM data access functionality."""
    print("=== Testing CGM Data Access ===")

    cgm = CGMDataAccess()

    if cgm.connect():
        # Get collection info
        cgm.get_collection_info()

        # Explore schema
        cgm.explore_schema(limit=3)

        # Get recent readings
        recent = cgm.get_recent_readings(limit=5)
        if recent:
            print(f"\n=== Recent Readings Sample ===")
            for i, reading in enumerate(recent, 1):
                print(f"Reading {i}: {reading}")

        cgm.disconnect()
    else:
        print("Failed to connect to CGM data")


def test_dataframe_functionality():
    """Test DataFrame conversion and analysis functionality."""
    print("=== Testing DataFrame Functionality ===")
    
    cgm = CGMDataAccess()
    
    if cgm.connect():
        # Test DataFrame creation for last week
        print("\n--- Creating DataFrame for Last Week ---")
        df = cgm.get_dataframe_for_period('last_week')
        
        if not df.empty:
            print(f"\n📊 DataFrame Info:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Data types:\n{df.dtypes}")
            
            # Show sample data
            print(f"\n📈 Sample Data:")
            print(df[['datetime', 'sgv', 'direction', 'hour', 'glucose_category']].head())
            
            # Perform analysis
            print(f"\n📊 Analysis Results:")
            analysis = cgm.analyze_dataframe(df)
            
            # Display basic stats
            basic_stats = analysis['basic_stats']
            print(f"  Basic Stats:")
            print(f"    Total readings: {basic_stats['total_readings']}")
            print(f"    Average glucose: {basic_stats['avg_glucose']:.1f} mg/dL")
            print(f"    Glucose range: {basic_stats['min_glucose']:.0f}-{basic_stats['max_glucose']:.0f} mg/dL")
            
            # Display time in range
            tir = analysis['time_in_range']
            print(f"  Time in Range:")
            print(f"    Low (<70): {tir['low_percent']:.1f}%")
            print(f"    Normal (70-180): {tir['normal_percent']:.1f}%")
            print(f"    High (180-250): {tir['high_percent']:.1f}%")
            print(f"    Very High (>250): {tir['very_high_percent']:.1f}%")
            
            # Test custom time range (last 3 days)
            print(f"\n--- Testing Custom Time Range (Last 3 Days) ---")
            end_time = datetime.now()
            start_time = end_time - timedelta(days=3)
            df_custom = cgm.get_dataframe_for_period('custom', start_time, end_time)
            
            if not df_custom.empty:
                print(f"Custom DataFrame shape: {df_custom.shape}")
                custom_analysis = cgm.analyze_dataframe(df_custom)
                print(f"Average glucose (3 days): {custom_analysis['basic_stats']['avg_glucose']:.1f} mg/dL")
        
        cgm.disconnect()
    else:
        print("Failed to connect to CGM data")


if __name__ == "__main__":
    # Test DataFrame functionality
    test_dataframe_functionality()
