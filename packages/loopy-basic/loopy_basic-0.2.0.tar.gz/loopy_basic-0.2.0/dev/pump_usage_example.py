#!/usr/bin/env python3
"""
Simple Pump Data Usage Example

A simplified example showing how to access pump data for analysis.
This script demonstrates the most common pump data queries you'll likely need.

Run with: uv run python dev/pump_usage_example.py
"""

from loopy.connection.mongodb import MongoDBConnection
from datetime import datetime, timedelta
import pandas as pd

def main():
    """Simple pump data analysis example."""
    print("Pump Data Usage Example")
    print("=" * 40)
    
    # Connect to database
    conn = MongoDBConnection()
    if not conn.connect():
        print("❌ Failed to connect to database")
        return
    
    try:
        db = conn.database
        
        # 1. Recent bolus analysis (last 7 days)
        print("\n📊 Recent Bolus Analysis")
        print("-" * 25)
        
        # Query for bolus data from last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
        bolus_data = list(db.treatments.find({
            'eventType': 'Correction Bolus',
            'timestamp': {'$gte': week_ago}
        }).sort('timestamp', -1))
        
        if bolus_data:
            # Convert to DataFrame for easy analysis
            bolus_df = pd.DataFrame(bolus_data)
            
            print(f"Total bolus doses: {len(bolus_df)}")
            print(f"Total insulin: {bolus_df['insulin'].sum():.1f} units")
            print(f"Average bolus: {bolus_df['insulin'].mean():.2f} units")
            print(f"Min bolus: {bolus_df['insulin'].min():.2f} units")
            print(f"Max bolus: {bolus_df['insulin'].max():.2f} units")
            
            # Most recent boluses
            print("\nLast 3 boluses:")
            for i, row in bolus_df.head(3).iterrows():
                timestamp = pd.to_datetime(row['timestamp'])
                print(f"  {timestamp.strftime('%m/%d %H:%M')}: {row['insulin']:.2f} units")
        else:
            print("No bolus data found")
        
        # 2. Carb intake analysis
        print("\n🍎 Carb Intake Analysis")
        print("-" * 22)
        
        carb_data = list(db.treatments.find({
            'eventType': 'Carb Correction',
            'timestamp': {'$gte': week_ago}
        }).sort('timestamp', -1))
        
        if carb_data:
            carb_df = pd.DataFrame(carb_data)
            
            print(f"Total carb entries: {len(carb_df)}")
            print(f"Total carbs: {carb_df['carbs'].sum():.0f}g")
            print(f"Average per meal: {carb_df['carbs'].mean():.1f}g")
            
            # Recent carb entries
            print("\nLast 3 carb entries:")
            for i, row in carb_df.head(3).iterrows():
                timestamp = pd.to_datetime(row['timestamp'])
                print(f"  {timestamp.strftime('%m/%d %H:%M')}: {row['carbs']:.0f}g")
        else:
            print("No carb data found")
        
        # 3. Current pump profile
        print("\n⚙️ Current Pump Settings")
        print("-" * 23)
        
        # Get latest profile
        profile = list(db.profile.find().sort('startDate', -1).limit(1))
        if profile:
            profile = profile[0]
            default_profile_name = profile.get('defaultProfile', '')
            
            if default_profile_name and default_profile_name in profile.get('store', {}):
                settings = profile['store'][default_profile_name]
                
                # Basal rates
                print("Basal rates:")
                for basal in settings.get('basal', []):
                    print(f"  {basal['time']}: {basal['value']} U/hr")
                
                # Carb ratios
                print("\nCarb ratios:")
                for ratio in settings.get('carbratio', []):
                    print(f"  {ratio['time']}: {ratio['value']}g/U")
        
        # 4. Recent pump status
        print("\n📱 Current Status")
        print("-" * 16)
        
        # Get latest device status with loop data
        loop_status = list(db.devicestatus.find({
            'loop': {'$exists': True}
        }).sort('created_at', -1).limit(1))
        
        if loop_status:
            loop = loop_status[0]['loop']
            
            # Current values
            iob = loop.get('iob', {}).get('iob', 0)
            cob = loop.get('cob', {}).get('cob', 0)
            
            print(f"Insulin On Board (IOB): {iob:.2f} units")
            print(f"Carbs On Board (COB): {cob:.1f}g")
            
            # Enacted rate (current temp basal or profile basal)
            enacted = loop.get('enacted')
            if enacted:
                rate = enacted.get('rate', 'Unknown')
                duration = enacted.get('duration', 0)
                print(f"Current basal rate: {rate} U/hr")
                if duration > 0:
                    print(f"Temp basal duration: {duration} min remaining")
        
        # 5. Site changes (last 30 days)
        print("\n🔄 Recent Site Changes")
        print("-" * 21)
        
        month_ago = (datetime.now() - timedelta(days=30)).isoformat() + 'Z'
        site_changes = list(db.treatments.find({
            'eventType': 'Site Change',
            'timestamp': {'$gte': month_ago}
        }).sort('timestamp', -1))
        
        print(f"Site changes in last 30 days: {len(site_changes)}")
        
        if site_changes:
            print("Most recent site changes:")
            for change in site_changes[:3]:
                timestamp = pd.to_datetime(change['timestamp'])
                days_ago = (pd.Timestamp.now(tz=timestamp.tz) - timestamp).days
                print(f"  {timestamp.strftime('%m/%d')}: {days_ago} days ago")
        
        print("\n✅ Analysis complete!")
        
    finally:
        conn.disconnect()

if __name__ == "__main__":
    main()