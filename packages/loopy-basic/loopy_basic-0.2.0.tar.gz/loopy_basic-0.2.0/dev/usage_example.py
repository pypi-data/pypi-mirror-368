"""
Usage Example: Loopy Basic CGM Data Analysis

This script demonstrates how to use the loopy-basic package to:
1. Connect to MongoDB database
2. Pull CGM data for the past 3 months
3. Convert to pandas DataFrame for analysis

Run with: uv run python dev/usage_example.py
"""

from datetime import datetime, timedelta
from loopy.data.cgm import CGMDataAccess


def main():
    """Demonstrate basic usage of the loopy-basic package."""
    
    print("=" * 60)
    print("Loopy Basic - CGM Data Analysis Usage Example")
    print("=" * 60)
    
    # Initialize CGM data access
    print("\n1. Initializing CGM data access...")
    cgm = CGMDataAccess()
    
    # Connect to database
    print("\n2. Connecting to MongoDB database...")
    if not cgm.connect():
        print("❌ Failed to connect to database")
        print("   Make sure your .env file is configured correctly")
        return
    
    # Define time period (last 3 months)
    print("\n3. Defining time period (last 3 months)...")
    end_time = datetime.now()
    start_time = end_time - timedelta(days=90)  # ~3 months
    
    print(f"   Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Pull CGM data for the specified period
    print("\n4. Pulling CGM data from database...")
    try:
        df = cgm.get_dataframe_for_period(
            period_type='custom',
            start_date=start_time,
            end_date=end_time,
            clean_data=True
        )
        
        if df.empty:
            print("❌ No data retrieved for the specified period")
            cgm.disconnect()
            return
            
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        cgm.disconnect()
        return
    
    # Display DataFrame information
    print("\n5. DataFrame Information:")
    print("   " + "=" * 40)
    print(f"   📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"   📅 Time span: {(df['datetime'].max() - df['datetime'].min()).days} days")
    print(f"   🩸 Glucose range: {df['sgv'].min():.0f} - {df['sgv'].max():.0f} mg/dL")
    print(f"   📈 Average glucose: {df['sgv'].mean():.1f} mg/dL")
    
    # Show column information
    print("\n6. Available columns:")
    print("   " + "=" * 40)
    for i, col in enumerate(df.columns):
        print(f"   {i+1:2d}. {col:<20} ({df[col].dtype})")
    
    # Show sample of the data
    print("\n7. Sample data (first 10 rows):")
    print("   " + "=" * 40)
    sample_cols = ['datetime', 'sgv', 'direction', 'hour', 'day_of_week', 'glucose_category']
    print(df[sample_cols].head(10).to_string(index=False))
    
    # Basic time range analysis
    print("\n8. Basic time in range analysis:")
    print("   " + "=" * 40)
    
    # Calculate time in range percentages
    total_readings = len(df)
    low_count = (df['glucose_category'] == 'Low').sum()
    normal_count = (df['glucose_category'] == 'Normal').sum()
    high_count = (df['glucose_category'] == 'High').sum()
    very_high_count = (df['glucose_category'] == 'Very High').sum()
    
    print(f"   📉 Low (<70 mg/dL):        {low_count:4d} readings ({low_count/total_readings*100:.1f}%)")
    print(f"   ✅ Normal (70-180 mg/dL):  {normal_count:4d} readings ({normal_count/total_readings*100:.1f}%)")
    print(f"   📈 High (180-250 mg/dL):   {high_count:4d} readings ({high_count/total_readings*100:.1f}%)")
    print(f"   🚨 Very High (>250 mg/dL): {very_high_count:4d} readings ({very_high_count/total_readings*100:.1f}%)")
    
    # Data quality check
    print("\n9. Data quality assessment:")
    print("   " + "=" * 40)
    
    time_span_days = (df['datetime'].max() - df['datetime'].min()).days
    expected_readings = time_span_days * 288  # CGM reads every 5 minutes = 288/day
    actual_readings = len(df)
    data_coverage = (actual_readings / expected_readings) * 100 if expected_readings > 0 else 0
    
    print(f"   📊 Expected readings (~5min intervals): {expected_readings:,}")
    print(f"   📊 Actual readings: {actual_readings:,}")
    print(f"   📊 Data coverage: {data_coverage:.1f}%")
    print(f"   📊 Average readings per day: {actual_readings/time_span_days:.0f}")
    
    # Save DataFrame info for potential future use
    print("\n10. DataFrame ready for analysis!")
    print("    " + "=" * 40)
    print(f"    Variable 'df' contains your cleaned CGM data")
    print(f"    Shape: {df.shape}")
    print(f"    Ready for time-series analysis, pattern discovery, and visualization")
    
    # Disconnect from database
    print("\n11. Disconnecting from database...")
    cgm.disconnect()
    
    print("\n✅ Usage example completed successfully!")
    print("   Your CGM data is now loaded and ready for analysis.")
    
    # Return the DataFrame for potential interactive use
    return df


if __name__ == "__main__":
    # Run the example
    dataframe = main()
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("  1. Use marimo notebooks for interactive exploration")
    print("  2. Analyze temporal patterns (hourly, daily)")
    print("  3. Create visualizations of glucose trends")
    print("  4. Identify optimization opportunities")
    print("=" * 60)