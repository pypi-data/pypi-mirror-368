"""
Pump Data Access Example

This script demonstrates how to access pump data from the MongoDB database.
It shows how to query for basal rates, bolus amounts, carb ratios, and other
pump-related data from the relevant collections.

Run with: uv run python dev/exploratory/pump_data_access.py
"""

from loopy.connection.mongodb import MongoDBConnection
from datetime import datetime, timedelta
import pandas as pd
from pprint import pprint
import json

class PumpDataAccess:
    """Class for accessing pump data from MongoDB."""

    def __init__(self):
        """Initialize the PumpDataAccess class."""
        self.conn = None
        self.database = None

    def connect(self):
        """Connect to the MongoDB database."""
        self.conn = MongoDBConnection()
        if not self.conn.connect():
            print("Failed to connect to MongoDB")
            return False

        self.database = self.conn.database
        return True

    def disconnect(self):
        """Disconnect from the MongoDB database."""
        if self.conn:
            self.conn.disconnect()

    def get_treatments(self, limit=10, event_type=None, start_date=None, end_date=None):
        """
        Get treatment data from the treatments collection.

        Args:
            limit (int): Maximum number of documents to return
            event_type (str): Filter by event type (e.g., 'Bolus', 'Temp Basal')
            start_date (datetime): Start date for filtering
            end_date (datetime): End date for filtering

        Returns:
            list: List of treatment documents
        """
        if self.database is None:
            print("Not connected to database")
            return []

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

    def get_bolus_data(self, days=7):
        """
        Get bolus data for the specified number of days.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of bolus documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Correction Bolus',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_basal_data(self, days=7):
        """
        Get basal data for the specified number of days.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of basal documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Temp Basal',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_carb_data(self, days=7):
        """
        Get carb data for the specified number of days.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of carb documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Carb Correction',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_current_profile(self):
        """
        Get the current profile settings.

        Returns:
            dict: The current profile document
        """
        if self.database is None:
            print("Not connected to database")
            return None

        # Get the most recent profile
        profile = list(self.database.profile.find().sort('startDate', -1).limit(1))

        if not profile:
            return None

        return profile[0]

    def get_basal_profile(self):
        """
        Get the basal profile settings.

        Returns:
            list: The basal profile settings
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

    def get_carb_ratio_profile(self):
        """
        Get the carb ratio profile settings.

        Returns:
            list: The carb ratio profile settings
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

    def get_insulin_sensitivity_profile(self):
        """
        Get the insulin sensitivity profile settings.

        Returns:
            list: The insulin sensitivity profile settings
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

    def get_recent_pump_status(self, limit=1):
        """
        Get the most recent pump status.

        Args:
            limit (int): Number of status documents to return

        Returns:
            list: Recent pump status documents
        """
        if self.database is None:
            print("Not connected to database")
            return []

        # Get the most recent devicestatus documents
        status = list(self.database.devicestatus.find(
            {'pump': {'$exists': True}}
        ).sort('created_at', -1).limit(limit))

        return status

    def get_recent_loop_status(self, limit=1):
        """
        Get the most recent loop status.

        Args:
            limit (int): Number of status documents to return

        Returns:
            list: Recent loop status documents
        """
        if self.database is None:
            print("Not connected to database")
            return []

        # Get the most recent devicestatus documents with loop data
        status = list(self.database.devicestatus.find(
            {'loop': {'$exists': True}}
        ).sort('created_at', -1).limit(limit))

        return status

    def get_insulin_on_board(self):
        """
        Get the current insulin on board (IOB).

        Returns:
            float: Current IOB or None if not available
        """
        status = self.get_recent_loop_status(1)

        if not status or 'loop' not in status[0] or 'iob' not in status[0]['loop']:
            return None

        return status[0]['loop']['iob'].get('iob')

    def get_carbs_on_board(self):
        """
        Get the current carbs on board (COB).

        Returns:
            float: Current COB or None if not available
        """
        status = self.get_recent_loop_status(1)

        if not status or 'loop' not in status[0] or 'cob' not in status[0]['loop']:
            return None

        return status[0]['loop']['cob'].get('cob')

    def get_current_basal_rate(self):
        """
        Get the current basal rate.

        Returns:
            float: Current basal rate or None if not available
        """
        status = self.get_recent_loop_status(1)

        if not status or 'loop' not in status[0] or 'enacted' not in status[0]['loop']:
            return None

        return status[0]['loop']['enacted'].get('rate')

    def get_site_change_data(self, days=30):
        """
        Get site change data for the specified number of days.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of site change documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Site Change',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_suspend_pump_data(self, days=7):
        """
        Get pump suspension data for the specified number of days.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of pump suspension documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Suspend Pump',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )

    def get_temporary_override_data(self, days=7):
        """
        Get temporary override data for the specified number of days.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of temporary override documents
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        return self.get_treatments(
            event_type='Temporary Override',
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )


def main():
    """Main function to demonstrate pump data access."""
    print("=" * 80)
    print("PUMP DATA ACCESS EXAMPLE")
    print("=" * 80)

    # Initialize and connect
    pump_data = PumpDataAccess()
    if not pump_data.connect():
        return

    try:
        # 1. Get recent bolus data
        print("\n" + "=" * 80)
        print("RECENT BOLUS DATA")
        print("=" * 80)
        bolus_data = pump_data.get_bolus_data(days=3)
        print(f"Found {len(bolus_data)} bolus records in the last 3 days")

        if bolus_data:
            print("\nSample bolus data:")
            for i, bolus in enumerate(bolus_data[:5]):
                print(f"\nBolus {i+1}:")
                print(f"  Time: {bolus.get('timestamp')}")
                print(f"  Amount: {bolus.get('insulin')} units")
                print(f"  Type: {bolus.get('eventType')}")
                if 'carbs' in bolus:
                    print(f"  Carbs: {bolus.get('carbs')}g")

        # 2. Get recent basal data
        print("\n" + "=" * 80)
        print("RECENT BASAL DATA")
        print("=" * 80)
        basal_data = pump_data.get_basal_data(days=1)
        print(f"Found {len(basal_data)} temp basal records in the last day")

        if basal_data:
            print("\nSample basal data:")
            for i, basal in enumerate(basal_data[:5]):
                print(f"\nTemp Basal {i+1}:")
                print(f"  Time: {basal.get('timestamp')}")
                print(f"  Rate: {basal.get('rate')} U/hr")
                print(f"  Duration: {basal.get('duration')} minutes")

        # 2.5 Get recent carb data
        print("\n" + "=" * 80)
        print("RECENT CARB DATA")
        print("=" * 80)
        carb_data = pump_data.get_carb_data(days=3)
        print(f"Found {len(carb_data)} carb correction records in the last 3 days")

        if carb_data:
            print("\nSample carb data:")
            for i, carb in enumerate(carb_data[:5]):
                print(f"\nCarb Correction {i+1}:")
                print(f"  Time: {carb.get('timestamp')}")
                if 'carbs' in carb:
                    print(f"  Carbs: {carb.get('carbs')}g")
                if 'insulin' in carb:
                    print(f"  Insulin: {carb.get('insulin')} units")
                print(f"  Type: {carb.get('eventType')}")

        # 3. Get basal profile
        print("\n" + "=" * 80)
        print("BASAL PROFILE")
        print("=" * 80)
        basal_profile = pump_data.get_basal_profile()
        print(f"Found {len(basal_profile)} basal profile entries")

        if basal_profile:
            print("\nBasal profile:")
            for entry in basal_profile:
                print(f"  {entry.get('time')}: {entry.get('value')} U/hr")

        # 4. Get carb ratio profile
        print("\n" + "=" * 80)
        print("CARB RATIO PROFILE")
        print("=" * 80)
        carb_ratio_profile = pump_data.get_carb_ratio_profile()
        print(f"Found {len(carb_ratio_profile)} carb ratio profile entries")

        if carb_ratio_profile:
            print("\nCarb ratio profile:")
            for entry in carb_ratio_profile:
                print(f"  {entry.get('time')}: {entry.get('value')} g/U")

        # 5. Get insulin sensitivity profile
        print("\n" + "=" * 80)
        print("INSULIN SENSITIVITY PROFILE")
        print("=" * 80)
        sensitivity_profile = pump_data.get_insulin_sensitivity_profile()
        print(f"Found {len(sensitivity_profile)} insulin sensitivity profile entries")

        if sensitivity_profile:
            print("\nInsulin sensitivity profile:")
            for entry in sensitivity_profile:
                print(f"  {entry.get('time')}: {entry.get('value')} mg/dL per unit")

        # 6. Get site change data
        print("\n" + "=" * 80)
        print("SITE CHANGE DATA")
        print("=" * 80)
        site_change_data = pump_data.get_site_change_data(days=30)
        print(f"Found {len(site_change_data)} site change records in the last 30 days")

        if site_change_data:
            print("\nSample site change data:")
            for i, site_change in enumerate(site_change_data[:5]):
                print(f"\nSite Change {i+1}:")
                print(f"  Time: {site_change.get('timestamp')}")
                print(f"  Type: {site_change.get('eventType')}")
                if 'notes' in site_change:
                    print(f"  Notes: {site_change.get('notes')}")

        # 7. Get suspend pump data
        print("\n" + "=" * 80)
        print("SUSPEND PUMP DATA")
        print("=" * 80)
        suspend_data = pump_data.get_suspend_pump_data(days=7)
        print(f"Found {len(suspend_data)} pump suspension records in the last 7 days")

        if suspend_data:
            print("\nSample suspend pump data:")
            for i, suspend in enumerate(suspend_data[:5]):
                print(f"\nSuspend Pump {i+1}:")
                print(f"  Time: {suspend.get('timestamp')}")
                print(f"  Type: {suspend.get('eventType')}")
                if 'duration' in suspend:
                    print(f"  Duration: {suspend.get('duration')} minutes")
                if 'notes' in suspend:
                    print(f"  Notes: {suspend.get('notes')}")

        # 8. Get temporary override data
        print("\n" + "=" * 80)
        print("TEMPORARY OVERRIDE DATA")
        print("=" * 80)
        override_data = pump_data.get_temporary_override_data(days=7)
        print(f"Found {len(override_data)} temporary override records in the last 7 days")

        if override_data:
            print("\nSample temporary override data:")
            for i, override in enumerate(override_data[:5]):
                print(f"\nTemporary Override {i+1}:")
                print(f"  Time: {override.get('timestamp')}")
                print(f"  Type: {override.get('eventType')}")
                if 'duration' in override:
                    print(f"  Duration: {override.get('duration')} minutes")
                if 'reason' in override:
                    print(f"  Reason: {override.get('reason')}")
                if 'notes' in override:
                    print(f"  Notes: {override.get('notes')}")

        # 9. Get current pump status
        print("\n" + "=" * 80)
        print("CURRENT PUMP STATUS")
        print("=" * 80)

        # Get IOB and COB
        iob = pump_data.get_insulin_on_board()
        cob = pump_data.get_carbs_on_board()
        current_basal = pump_data.get_current_basal_rate()

        print(f"Insulin On Board (IOB): {iob} units")
        print(f"Carbs On Board (COB): {cob} grams")
        print(f"Current Basal Rate: {current_basal} U/hr")

        # Get recent pump status
        pump_status = pump_data.get_recent_pump_status(1)
        if pump_status:
            print("\nPump details:")
            pump = pump_status[0].get('pump', {})
            print(f"  Manufacturer: {pump.get('manufacturer')}")
            print(f"  Model: {pump.get('model')}")
            print(f"  ID: {pump.get('pumpID')}")
            print(f"  Suspended: {pump.get('suspended')}")
            print(f"  Last updated: {pump.get('clock')}")

        print("\n" + "=" * 80)
        print("EXPLORATION COMPLETE")
        print("=" * 80)

    finally:
        # Disconnect
        pump_data.disconnect()


if __name__ == "__main__":
    main()
