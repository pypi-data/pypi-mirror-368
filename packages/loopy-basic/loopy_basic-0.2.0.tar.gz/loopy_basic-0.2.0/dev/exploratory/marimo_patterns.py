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
    mo.md(r"""# Loopy Basic - CGM Data Analysis (Marimo Patterns)""")
    return


@app.cell
def context_manager_pattern(CGMDataAccess, datetime, timedelta):
    """Use context manager for automatic connection handling."""

    # Define time period
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)  # Last month

    # Use context manager - automatically connects and disconnects
    with CGMDataAccess() as cgm:
        df = cgm.get_dataframe_for_period(
            period_type='custom',
            start_date=start_time,
            end_date=end_time,
            clean_data=True
        )

    # Connection is automatically closed here
    print(f"✅ Data loaded: {len(df)} readings")
    print(f"📅 Time range: {df['datetime'].min()} to {df['datetime'].max()}")

    return


@app.cell
def single_cell_pattern(CGMDataAccess, datetime, timedelta):
    """Handle connection in a single cell to avoid reactive issues."""

    cgm = CGMDataAccess()

    try:
        # Connect
        cgm.connect()

        # Get data
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)  # Last week

        df_week = cgm.get_dataframe_for_period(
            period_type='custom',
            start_date=start_time,
            end_date=end_time,
            clean_data=True
        )

        # Basic analysis
        analysis = cgm.analyze_dataframe(df_week)

    finally:
        # Always disconnect
        cgm.disconnect()

    print(f"📊 Weekly data: {len(df_week)} readings")
    print(f"📈 Average glucose: {analysis['basic_stats']['avg_glucose']:.1f} mg/dL")
    print(f"🎯 Time in range: {analysis['time_in_range']['normal_percent']:.1f}%")

    return


@app.cell
def connection_state(CGMDataAccess):
    """Track connection state to avoid multiple connections."""

    # Use a simple state object
    class ConnectionState:
        def __init__(self):
            self.cgm = None
            self.connected = False

        def get_connection(self):
            if not self.connected:
                self.cgm = CGMDataAccess()
                self.cgm.connect()
                self.connected = True
            return self.cgm

        def close(self):
            if self.connected and self.cgm:
                self.cgm.disconnect()
                self.connected = False

    # Create singleton-like state
    if 'conn_state' not in globals():
        conn_state = ConnectionState()

    return (conn_state,)


@app.cell
def use_connection_state(conn_state):
    """Use the managed connection state."""

    cgm = conn_state.get_connection()

    # Get recent data
    df_recent = cgm.get_last_24_hours()

    print(f"🕐 Last 24h data: {len(df_recent)} readings")
    if df_recent:
        recent_avg = sum(r['sgv'] for r in df_recent) / len(df_recent)
        print(f"📈 Average glucose (24h): {recent_avg:.1f} mg/dL")

    return


@app.cell
def safe_data_fetcher(CGMDataAccess):
    """Create a function that safely fetches data."""

    def fetch_cgm_data(period_type='last_week', **kwargs):
        """Safely fetch CGM data with automatic connection handling."""
        cgm = CGMDataAccess()
        try:
            cgm.connect()
            if period_type == 'custom':
                df = cgm.get_dataframe_for_period(period_type, **kwargs)
            else:
                df = cgm.get_dataframe_for_period(period_type)
            return df
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
        finally:
            cgm.disconnect()

    return (fetch_cgm_data,)


@app.cell
def use_safe_fetcher(datetime, fetch_cgm_data, timedelta):
    """Use the safe data fetcher."""

    # Fetch different time periods
    df_day = fetch_cgm_data('last_24h')
    df_week = fetch_cgm_data('last_week')

    # Custom period
    end_time = datetime.now()
    start_time = end_time - timedelta(days=3)
    df_custom = fetch_cgm_data('custom', start_date=start_time, end_date=end_time)

    print("📊 Data Summary:")
    print(f"   Last 24h: {len(df_day) if df_day is not None else 0} readings")
    print(f"   Last week: {len(df_week) if df_week is not None else 0} readings") 
    print(f"   Last 3 days: {len(df_custom) if df_custom is not None else 0} readings")

    return


@app.cell
def recommendations(mo):
    mo.md(
        r"""
    ## Recommended Patterns for Marimo:

    **🥇 Best: Context Manager** - Use `with CGMDataAccess() as cgm:` for automatic cleanup

    **🥈 Good: Single Cell** - Handle connection + data + disconnect in one cell

    **🥉 Okay: Safe Function** - Wrapper function with try/finally

    **❌ Avoid: Separate connect/disconnect cells** - Reactive execution makes this unreliable
    """
    )
    return


if __name__ == "__main__":
    app.run()
