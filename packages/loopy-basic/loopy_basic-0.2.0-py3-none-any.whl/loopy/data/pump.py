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


class PumpDataAccess:
    """Access and query pump treatment data from MongoDB collections.
    
    This class provides methods to connect to a MongoDB database containing
    diabetes pump data (insulin doses, basal rates, treatments) and retrieve 
    data for analysis. Supports context manager protocol for automatic 
    connection management.
    
    Attributes:
        db_conn: MongoDB connection instance
        database: MongoDB database reference
        
    Example:
        Basic usage:
            pump = PumpDataAccess()
            pump.connect()
            treatments = pump.get_bolus_data(days=7)
            pump.disconnect()
            
        Context manager (recommended):
            with PumpDataAccess() as pump:
                treatments = pump.get_bolus_data(days=7)
    """

    def __init__(self) -> None:
        """Initialize pump data access with MongoDB connection."""
        self.db_conn = MongoDBConnection()
        self.database = None
    
    def __enter__(self) -> PumpDataAccess:
        """Context manager entry - connect to database.
        
        Returns:
            Self instance with established database connection
        """
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
        if not self.db_conn.connect():
            return False
        
        self.database = self.db_conn.database
        return True

    def disconnect(self) -> None:
        """Disconnect from the MongoDB database."""
        if self.db_conn:
            self.db_conn.disconnect()
            self.database = None

    def get_treatments(self, limit: int = 10, event_type: Optional[str] = None, 
                      start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get treatment data from the treatments collection.

        Args:
            limit: Maximum number of documents to return
            event_type: Filter by event type (e.g., 'Bolus', 'Temp Basal')
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of treatment documents
        """
        if self.database is None:
            raise ConnectionError("Not connected to database. Call connect() first.")

        # Build query
        query = {}

        if event_type:
            query['eventType'] = event_type

        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query['$gte'] = start_date.isoformat() + 'Z'
            if end_date:
                date_query['$lte'] = end_date.isoformat() + 'Z'
            if date_query:
                query['timestamp'] = date_query

        # Execute query
        treatments = list(self.database.treatments.find(query).sort('timestamp', -1).limit(limit))

        return treatments

    def get_bolus_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get bolus data for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of bolus documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Correction Bolus',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_basal_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get basal data for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of basal documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Temp Basal',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_carb_data(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get carb data for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of carb documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Carb Correction',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_dataframe_for_period(self, period: str, 
                                event_types: Optional[List[str]] = None) -> pd.DataFrame:
        """Get treatment data as a pandas DataFrame for a specified period.
        
        Args:
            period: Time period - 'last_24h', 'last_week', 'last_month', 'last_3_months'
            event_types: List of event types to include (default: all treatments)
            
        Returns:
            pandas.DataFrame: Treatment data with timestamp conversion
        """
        # Define time periods
        periods = {
            'last_24h': 1,
            'last_week': 7, 
            'last_month': 30,
            'last_3_months': 90
        }
        
        if period not in periods:
            raise ValueError(f"Unsupported period '{period}'. Use: {list(periods.keys())}")
        
        days = periods[period]
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Build query
        query = {
            'timestamp': {
                '$gte': start_date.isoformat() + 'Z',
                '$lte': end_date.isoformat() + 'Z'
            }
        }
        
        if event_types:
            query['eventType'] = {'$in': event_types}
        
        if self.database is None:
            raise ConnectionError("Not connected to database. Call connect() first.")
        
        # Get data
        treatments = list(self.database.treatments.find(query).sort('timestamp', -1))
        
        if not treatments:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(treatments)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['dateTime'] = pd.to_datetime(df['timestamp'])
        
        return df

    def get_current_profile(self) -> Optional[Dict[str, Any]]:
        """Get the current profile settings.

        Returns:
            The current profile document or None if not found
        """
        if self.database is None:
            raise ConnectionError("Not connected to database. Call connect() first.")

        # Get the most recent profile
        profile = list(self.database.profile.find().sort('startDate', -1).limit(1))

        if not profile:
            return None

        return profile[0]

    def get_basal_profile(self) -> List[Dict[str, Any]]:
        """Get the basal profile settings.

        Returns:
            The basal profile settings
        """
        profile = self.get_current_profile()

        if not profile or 'store' not in profile:
            return []

        # Get the default profile name
        default_profile = profile.get('defaultProfile')

        if not default_profile or default_profile not in profile['store']:
            # If no default profile, use the first one
            if profile['store']:
                default_profile = next(iter(profile['store']))
            else:
                return []

        # Get the basal profile
        return profile['store'][default_profile].get('basal', [])

    def get_carb_ratio_profile(self) -> List[Dict[str, Any]]:
        """Get the carb ratio profile settings.

        Returns:
            The carb ratio profile settings
        """
        profile = self.get_current_profile()

        if not profile or 'store' not in profile:
            return []

        # Get the default profile name
        default_profile = profile.get('defaultProfile')

        if not default_profile or default_profile not in profile['store']:
            # If no default profile, use the first one
            if profile['store']:
                default_profile = next(iter(profile['store']))
            else:
                return []

        # Get the carb ratio profile
        return profile['store'][default_profile].get('carbratio', [])

    def get_insulin_sensitivity_profile(self) -> List[Dict[str, Any]]:
        """Get the insulin sensitivity profile settings.

        Returns:
            The insulin sensitivity profile settings
        """
        profile = self.get_current_profile()

        if not profile or 'store' not in profile:
            return []

        # Get the default profile name
        default_profile = profile.get('defaultProfile')

        if not default_profile or default_profile not in profile['store']:
            # If no default profile, use the first one
            if profile['store']:
                default_profile = next(iter(profile['store']))
            else:
                return []

        # Get the insulin sensitivity profile
        return profile['store'][default_profile].get('sens', [])

    def get_recent_pump_status(self, limit: int = 1) -> List[Dict[str, Any]]:
        """Get the most recent pump status.

        Args:
            limit: Number of status documents to return

        Returns:
            Recent pump status documents
        """
        if self.database is None:
            raise ConnectionError("Not connected to database. Call connect() first.")

        # Get the most recent devicestatus documents
        status = list(self.database.devicestatus.find(
            {'pump': {'$exists': True}}
        ).sort('created_at', -1).limit(limit))

        return status

    def get_recent_loop_status(self, limit: int = 1) -> List[Dict[str, Any]]:
        """Get the most recent loop status.

        Args:
            limit: Number of status documents to return

        Returns:
            Recent loop status documents
        """
        if self.database is None:
            raise ConnectionError("Not connected to database. Call connect() first.")

        # Get the most recent devicestatus documents with loop data
        status = list(self.database.devicestatus.find(
            {'loop': {'$exists': True}}
        ).sort('created_at', -1).limit(limit))

        return status

    def get_insulin_on_board(self) -> Optional[float]:
        """Get the current insulin on board (IOB).

        Returns:
            Current IOB or None if not available
        """
        status = self.get_recent_loop_status(1)

        if not status or 'loop' not in status[0] or 'iob' not in status[0]['loop']:
            return None

        return status[0]['loop']['iob'].get('iob')

    def get_carbs_on_board(self) -> Optional[float]:
        """Get the current carbs on board (COB).

        Returns:
            Current COB or None if not available
        """
        status = self.get_recent_loop_status(1)

        if not status or 'loop' not in status[0] or 'cob' not in status[0]['loop']:
            return None

        return status[0]['loop']['cob'].get('cob')

    def get_current_basal_rate(self) -> Optional[float]:
        """Get the current basal rate.

        Returns:
            Current basal rate or None if not available
        """
        status = self.get_recent_loop_status(1)

        if not status or 'loop' not in status[0] or 'enacted' not in status[0]['loop']:
            return None

        return status[0]['loop']['enacted'].get('rate')

    def get_site_change_data(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get site change data for the specified number of days.

        Args:
            days: Number of days to look back

        Returns:
            List of site change documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Site Change',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def analyze_treatments(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze treatment DataFrame and return summary statistics.
        
        Args:
            df: DataFrame containing treatment data
            
        Returns:
            Dictionary with analysis results including insulin totals, 
            carb totals, and treatment counts by type
        """
        if df.empty:
            return {
                'total_treatments': 0,
                'treatment_types': {},
                'insulin_summary': {},
                'carb_summary': {},
                'date_range': {}
            }
        
        analysis = {
            'total_treatments': len(df),
            'treatment_types': df['eventType'].value_counts().to_dict() if 'eventType' in df.columns else {},
            'date_range': {}
        }
        
        # Date range analysis
        if 'dateTime' in df.columns:
            analysis['date_range'] = {
                'start_date': df['dateTime'].min().isoformat(),
                'end_date': df['dateTime'].max().isoformat(),
                'days_span': (df['dateTime'].max() - df['dateTime'].min()).days
            }
        
        # Insulin analysis
        if 'insulin' in df.columns:
            insulin_data = df[df['insulin'].notna() & (df['insulin'] > 0)]
            if not insulin_data.empty:
                analysis['insulin_summary'] = {
                    'total_insulin': float(insulin_data['insulin'].sum()),
                    'avg_dose': float(insulin_data['insulin'].mean()),
                    'min_dose': float(insulin_data['insulin'].min()),
                    'max_dose': float(insulin_data['insulin'].max()),
                    'num_doses': len(insulin_data)
                }
        
        # Carb analysis  
        if 'carbs' in df.columns:
            carb_data = df[df['carbs'].notna() & (df['carbs'] > 0)]
            if not carb_data.empty:
                analysis['carb_summary'] = {
                    'total_carbs': float(carb_data['carbs'].sum()),
                    'avg_carbs': float(carb_data['carbs'].mean()),
                    'min_carbs': float(carb_data['carbs'].min()),
                    'max_carbs': float(carb_data['carbs'].max()),
                    'num_entries': len(carb_data)
                }
        
        return analysis


def main():
    """Main function to test pump data access functionality."""
    print("Testing PumpDataAccess module...")
    print("=" * 50)
    
    try:
        with PumpDataAccess() as pump:
            print("✓ Successfully connected to database")
            
            # Test recent bolus data
            bolus_data = pump.get_bolus_data(days=3)
            print(f"✓ Retrieved {len(bolus_data)} bolus records (last 3 days)")
            
            # Test DataFrame functionality
            df = pump.get_dataframe_for_period('last_week')
            print(f"✓ Retrieved {len(df)} treatment records as DataFrame (last week)")
            
            if not df.empty:
                analysis = pump.analyze_treatments(df)
                print(f"✓ Analysis complete - {analysis['total_treatments']} treatments analyzed")
            
            # Test current status
            iob = pump.get_insulin_on_board()
            cob = pump.get_carbs_on_board()
            print(f"✓ Current IOB: {iob} units, COB: {cob}g")
            
            print("\n✅ All pump data access tests passed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()