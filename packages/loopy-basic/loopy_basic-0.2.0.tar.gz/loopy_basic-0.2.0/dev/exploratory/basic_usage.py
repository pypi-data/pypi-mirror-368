import marimo

__generated_with = "0.14.11"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    from datetime import datetime, timedelta
    from loopy.data.cgm import CGMDataAccess
    return CGMDataAccess, datetime, mo, timedelta


@app.cell
def title(mo):
    mo.md(r"""# Loopy Basic - CGM Data Analysis Usage Example""")
    return


@app.cell
def init(CGMDataAccess):
    # Initialize CGM data access
    cgm = CGMDataAccess()
    return (cgm,)


@app.cell
def connect(cgm):
    # Connect to the database
    cgm.connect()
    return


@app.cell
def time_period_select(datetime, timedelta):
    # Define a time period
    end_time = datetime.now()
    start_time = end_time - timedelta(days=90)  # ~3 months

    print(f"   Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    return end_time, start_time


@app.cell
def get_data(cgm, end_time, start_time):
    # Pull CGM data from database
    df = cgm.get_dataframe_for_period(
        period_type='custom',
        start_date=start_time,
        end_date=end_time,
        clean_data=True
    )
    return (df,)


@app.cell
def _(df):
    # Display DataFrame information
    print("DataFrame Information:")
    print("   " + "=" * 40)
    print(f"   📊 Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"   📅 Time span: {(df['datetime'].max() - df['datetime'].min()).days} days")
    print(f"   🩸 Glucose range: {df['sgv'].min():.0f} - {df['sgv'].max():.0f} mg/dL")
    print(f"   📈 Average glucose: {df['sgv'].mean():.1f} mg/dL")
    return


@app.cell
def _(df):
    # Show column information
    print("Available columns:")
    print("   " + "=" * 40)
    for i, col in enumerate(df.columns):
        print(f"   {i+1:2d}. {col:<20} ({df[col].dtype})")
    return


@app.cell
def _(df):
    # Show sample of the data
    print("Sample data (first 10 rows):")
    print("   " + "=" * 40)
    sample_cols = ['datetime', 'sgv', 'direction', 'hour', 'day_of_week', 'glucose_category']
    print(df[sample_cols].head(10).to_string(index=False))

    return


@app.cell
def _(df):
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

    return


@app.cell
def _(df):
    df
    return


@app.cell
def _(datetime, df, timedelta):
    import plotly.express as px

    # Filter the dataframe for the last 24 hours
    now = datetime.now()
    past_24_hours = now - timedelta(hours=24)
    df_filtered = df[df['datetime'] > past_24_hours]

    # # Create the time series plot
    # fig = px.line(
    #     df_filtered, 
    #     x='datetime', 
    #     y='sgv', 
    #     title='Continuous Glucose Monitor (CGM) Readings: Past 24 Hours',
    #     labels={'datetime': 'Time', 'sgv': 'SGV (mg/dL)'},
    #     markers=True
    # )

    # # Set plot attributes for better readability
    # fig.update_layout(
    #     xaxis_title='Time',
    #     yaxis_title='SGV (mg/dL)',
    #     hovermode='x unified',
    #     template='plotly_white'
    # )

    # fig

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
