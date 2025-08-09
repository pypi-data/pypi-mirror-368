"""
Pump Data Visualization with Marimo

This notebook demonstrates how to access and visualize pump data from MongoDB.
It uses the PumpDataAccess class to retrieve data and creates visualizations
to help understand insulin dosing patterns.

Run with: uv run marimo edit dev/exploratory/pump_data_visualization.py
"""

import marimo

__generated_with = "0.14.11"
app = marimo.App(width="medium")


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from datetime import datetime, timedelta
    from dev.exploratory.pump_data_access import PumpDataAccess
    return PumpDataAccess, datetime, go, mo, np, pd, px, timedelta


@app.cell
def title(mo):
    mo.md(r"""# Pump Data Visualization
    
    This notebook demonstrates how to access and visualize pump data from MongoDB.
    It uses the `PumpDataAccess` class to retrieve data and creates visualizations
    to help understand insulin dosing patterns.
    """)
    return


@app.cell
def connection_manager():
    """Create a connection manager for database access."""
    
    class ConnectionManager:
        def __init__(self):
            self.pump_data = None
            self.connected = False
            
        def connect(self):
            if not self.connected:
                self.pump_data = PumpDataAccess()
                if self.pump_data.connect():
                    self.connected = True
                    return True
                return False
            return True
            
        def disconnect(self):
            if self.connected and self.pump_data is not None:
                self.pump_data.disconnect()
                self.connected = False
                
        def get_pump_data(self):
            if not self.connected:
                self.connect()
            return self.pump_data
    
    # Create a singleton instance
    conn_manager = ConnectionManager()
    
    return conn_manager,


@app.cell
def connect_button(conn_manager, mo):
    """Create a connect/disconnect button."""
    
    connect_status = mo.ui.text("Not connected")
    
    def toggle_connection():
        if conn_manager.connected:
            conn_manager.disconnect()
            connect_status.update("Disconnected")
            return "Connect to MongoDB"
        else:
            if conn_manager.connect():
                connect_status.update("Connected")
                return "Disconnect from MongoDB"
            else:
                connect_status.update("Connection failed")
                return "Retry connection"
    
    button_label = "Connect to MongoDB" if not conn_manager.connected else "Disconnect from MongoDB"
    connect_button = mo.ui.button(button_label, on_click=toggle_connection)
    
    mo.md(f"### Database Connection")
    mo.hstack([connect_button, connect_status])
    
    return connect_button, connect_status


@app.cell
def date_range_selector(datetime, mo, timedelta):
    """Create date range selector for data retrieval."""
    
    # Default to last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    # Create date range selector
    date_range = mo.ui.date_range(
        value=(start_date.date(), end_date.date()),
        label="Date Range"
    )
    
    # Create days selector as an alternative
    days_options = [
        ("Last 24 hours", 1),
        ("Last 3 days", 3),
        ("Last week", 7),
        ("Last 2 weeks", 14),
        ("Last month", 30)
    ]
    days_selector = mo.ui.dropdown(
        options=days_options,
        value=7,
        label="Quick Select"
    )
    
    # Function to update date range based on days selector
    def update_date_range(days):
        new_end = datetime.now()
        new_start = new_end - timedelta(days=days)
        date_range.update((new_start.date(), new_end.date()))
    
    # Button to apply quick select
    apply_button = mo.ui.button(
        "Apply Quick Select",
        on_click=lambda: update_date_range(days_selector.value)
    )
    
    mo.md(f"### Select Time Period")
    mo.hstack([days_selector, apply_button])
    date_range
    
    return date_range, days_selector


@app.cell
def get_basal_data(conn_manager, date_range, datetime):
    """Retrieve basal data for the selected date range."""
    
    def fetch_basal_data():
        pump_data = conn_manager.get_pump_data()
        if pump_data is None:
            return pd.DataFrame()
        
        # Convert date range to datetime
        start_date = datetime.combine(date_range.value[0], datetime.min.time())
        end_date = datetime.combine(date_range.value[1], datetime.max.time())
        
        # Get basal data
        basal_data = pump_data.get_treatments(
            event_type="Temp Basal",
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Convert to DataFrame
        if not basal_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(basal_data)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['datetime'].dt.date
            df['time'] = df['datetime'].dt.time
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.day_name()
        
        return df
    
    # Create a button to fetch data
    fetch_button = mo.ui.button("Fetch Basal Data")
    
    # Only fetch data when button is clicked
    if fetch_button.value:
        basal_df = fetch_basal_data()
    else:
        basal_df = pd.DataFrame()
    
    # Display data info
    if not basal_df.empty:
        info = f"Retrieved {len(basal_df)} basal records from {date_range.value[0]} to {date_range.value[1]}"
    else:
        info = "No data fetched yet. Click the button to retrieve data."
    
    mo.md(f"### Basal Data")
    mo.hstack([fetch_button, mo.ui.text(info)])
    
    return basal_df, fetch_button


@app.cell
def get_bolus_data(conn_manager, date_range, datetime):
    """Retrieve bolus data for the selected date range."""
    
    def fetch_bolus_data():
        pump_data = conn_manager.get_pump_data()
        if pump_data is None:
            return pd.DataFrame()
        
        # Convert date range to datetime
        start_date = datetime.combine(date_range.value[0], datetime.min.time())
        end_date = datetime.combine(date_range.value[1], datetime.max.time())
        
        # Get bolus data
        bolus_data = pump_data.get_treatments(
            event_type="Bolus",
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
        
        # Convert to DataFrame
        if not bolus_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(bolus_data)
        
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['datetime'].dt.date
            df['time'] = df['datetime'].dt.time
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.day_name()
        
        return df
    
    # Create a button to fetch data
    fetch_button = mo.ui.button("Fetch Bolus Data")
    
    # Only fetch data when button is clicked
    if fetch_button.value:
        bolus_df = fetch_bolus_data()
    else:
        bolus_df = pd.DataFrame()
    
    # Display data info
    if not bolus_df.empty:
        info = f"Retrieved {len(bolus_df)} bolus records from {date_range.value[0]} to {date_range.value[1]}"
    else:
        info = "No data fetched yet. Click the button to retrieve data."
    
    mo.md(f"### Bolus Data")
    mo.hstack([fetch_button, mo.ui.text(info)])
    
    return bolus_df, fetch_button


@app.cell
def get_profiles(conn_manager, mo):
    """Retrieve pump profiles (basal, carb ratio, sensitivity)."""
    
    def fetch_profiles():
        pump_data = conn_manager.get_pump_data()
        if pump_data is None:
            return None, None, None
        
        # Get profiles
        basal_profile = pump_data.get_basal_profile()
        carb_ratio_profile = pump_data.get_carb_ratio_profile()
        sensitivity_profile = pump_data.get_insulin_sensitivity_profile()
        
        # Convert to DataFrames
        basal_df = pd.DataFrame(basal_profile) if basal_profile else pd.DataFrame()
        carb_ratio_df = pd.DataFrame(carb_ratio_profile) if carb_ratio_profile else pd.DataFrame()
        sensitivity_df = pd.DataFrame(sensitivity_profile) if sensitivity_profile else pd.DataFrame()
        
        return basal_df, carb_ratio_df, sensitivity_df
    
    # Create a button to fetch profiles
    fetch_button = mo.ui.button("Fetch Pump Profiles")
    
    # Only fetch profiles when button is clicked
    if fetch_button.value:
        basal_profile_df, carb_ratio_df, sensitivity_df = fetch_profiles()
    else:
        basal_profile_df, carb_ratio_df, sensitivity_df = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    # Display profile info
    if not basal_profile_df.empty:
        info = f"Retrieved pump profiles: {len(basal_profile_df)} basal entries, {len(carb_ratio_df)} carb ratio entries, {len(sensitivity_df)} sensitivity entries"
    else:
        info = "No profiles fetched yet. Click the button to retrieve profiles."
    
    mo.md(f"### Pump Profiles")
    mo.hstack([fetch_button, mo.ui.text(info)])
    
    return basal_profile_df, carb_ratio_df, fetch_button, sensitivity_df


@app.cell
def visualize_basal_data(basal_df, mo, px):
    """Visualize basal data."""
    
    mo.md("## Basal Rate Visualization")
    
    if basal_df.empty:
        return mo.md("No basal data available. Please fetch data first.")
    
    # Create basal rate timeline
    fig1 = px.scatter(
        basal_df,
        x='datetime',
        y='rate',
        color='duration',
        size='duration',
        hover_data=['duration', 'timestamp'],
        title='Temporary Basal Rates Over Time',
        labels={'rate': 'Basal Rate (U/hr)', 'datetime': 'Date/Time', 'duration': 'Duration (min)'}
    )
    
    fig1.update_layout(height=500)
    
    # Create hourly basal rate distribution
    if 'hour' in basal_df.columns and 'rate' in basal_df.columns:
        hourly_basal = basal_df.groupby('hour')['rate'].mean().reset_index()
        
        fig2 = px.bar(
            hourly_basal,
            x='hour',
            y='rate',
            title='Average Basal Rate by Hour of Day',
            labels={'rate': 'Average Basal Rate (U/hr)', 'hour': 'Hour of Day'}
        )
        
        fig2.update_layout(height=400)
    else:
        fig2 = None
    
    # Display visualizations
    mo.vstack([
        mo.md("### Temporary Basal Rates Over Time"),
        fig1,
        mo.md("### Average Basal Rate by Hour of Day"),
        fig2 if fig2 is not None else mo.md("Hourly data not available")
    ])
    
    return fig1, fig2


@app.cell
def visualize_bolus_data(bolus_df, mo, px):
    """Visualize bolus data."""
    
    mo.md("## Bolus Visualization")
    
    if bolus_df.empty:
        return mo.md("No bolus data available. Please fetch data first.")
    
    # Create bolus timeline
    fig1 = px.scatter(
        bolus_df,
        x='datetime',
        y='insulin',
        hover_data=['timestamp'],
        title='Bolus Amounts Over Time',
        labels={'insulin': 'Bolus Amount (U)', 'datetime': 'Date/Time'}
    )
    
    fig1.update_layout(height=500)
    
    # Create hourly bolus distribution
    if 'hour' in bolus_df.columns and 'insulin' in bolus_df.columns:
        hourly_bolus = bolus_df.groupby('hour')['insulin'].mean().reset_index()
        
        fig2 = px.bar(
            hourly_bolus,
            x='hour',
            y='insulin',
            title='Average Bolus Amount by Hour of Day',
            labels={'insulin': 'Average Bolus Amount (U)', 'hour': 'Hour of Day'}
        )
        
        fig2.update_layout(height=400)
    else:
        fig2 = None
    
    # Display visualizations
    mo.vstack([
        mo.md("### Bolus Amounts Over Time"),
        fig1,
        mo.md("### Average Bolus Amount by Hour of Day"),
        fig2 if fig2 is not None else mo.md("Hourly data not available")
    ])
    
    return fig1, fig2


@app.cell
def visualize_profiles(basal_profile_df, carb_ratio_df, go, mo, sensitivity_df):
    """Visualize pump profiles."""
    
    mo.md("## Pump Profiles Visualization")
    
    if basal_profile_df.empty and carb_ratio_df.empty and sensitivity_df.empty:
        return mo.md("No profile data available. Please fetch profiles first.")
    
    # Create a time-based x-axis for 24 hours
    hours = list(range(24))
    hour_labels = [f"{h:02d}:00" for h in hours]
    
    # Function to map profile times to hour values
    def time_to_hour(time_str):
        h, m = map(int, time_str.split(':'))
        return h + m/60
    
    # Create basal profile visualization
    if not basal_profile_df.empty and 'time' in basal_profile_df.columns and 'value' in basal_profile_df.columns:
        # Convert time strings to hour values
        basal_profile_df['hour'] = basal_profile_df['time'].apply(time_to_hour)
        
        # Sort by hour
        basal_profile_df = basal_profile_df.sort_values('hour')
        
        # Create the figure
        fig_basal = go.Figure()
        
        # Add the basal profile line
        fig_basal.add_trace(go.Scatter(
            x=basal_profile_df['hour'],
            y=basal_profile_df['value'],
            mode='lines+markers',
            name='Basal Rate',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        
        # Set the layout
        fig_basal.update_layout(
            title='Basal Rate Profile',
            xaxis_title='Time of Day',
            yaxis_title='Basal Rate (U/hr)',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(0, 24, 2)),
                ticktext=[f"{h:02d}:00" for h in range(0, 24, 2)]
            ),
            height=400
        )
    else:
        fig_basal = None
    
    # Create carb ratio profile visualization
    if not carb_ratio_df.empty and 'time' in carb_ratio_df.columns and 'value' in carb_ratio_df.columns:
        # Convert time strings to hour values
        carb_ratio_df['hour'] = carb_ratio_df['time'].apply(time_to_hour)
        
        # Sort by hour
        carb_ratio_df = carb_ratio_df.sort_values('hour')
        
        # Create the figure
        fig_carb = go.Figure()
        
        # Add the carb ratio profile line
        fig_carb.add_trace(go.Scatter(
            x=carb_ratio_df['hour'],
            y=carb_ratio_df['value'],
            mode='lines+markers',
            name='Carb Ratio',
            line=dict(color='green', width=2),
            marker=dict(size=8)
        ))
        
        # Set the layout
        fig_carb.update_layout(
            title='Carb Ratio Profile',
            xaxis_title='Time of Day',
            yaxis_title='Carb Ratio (g/U)',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(0, 24, 2)),
                ticktext=[f"{h:02d}:00" for h in range(0, 24, 2)]
            ),
            height=400
        )
    else:
        fig_carb = None
    
    # Create insulin sensitivity profile visualization
    if not sensitivity_df.empty and 'time' in sensitivity_df.columns and 'value' in sensitivity_df.columns:
        # Convert time strings to hour values
        sensitivity_df['hour'] = sensitivity_df['time'].apply(time_to_hour)
        
        # Sort by hour
        sensitivity_df = sensitivity_df.sort_values('hour')
        
        # Create the figure
        fig_sens = go.Figure()
        
        # Add the sensitivity profile line
        fig_sens.add_trace(go.Scatter(
            x=sensitivity_df['hour'],
            y=sensitivity_df['value'],
            mode='lines+markers',
            name='Insulin Sensitivity',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        # Set the layout
        fig_sens.update_layout(
            title='Insulin Sensitivity Profile',
            xaxis_title='Time of Day',
            yaxis_title='Sensitivity (mg/dL per U)',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(0, 24, 2)),
                ticktext=[f"{h:02d}:00" for h in range(0, 24, 2)]
            ),
            height=400
        )
    else:
        fig_sens = None
    
    # Display visualizations
    mo.vstack([
        mo.md("### Basal Rate Profile"),
        fig_basal if fig_basal is not None else mo.md("Basal profile data not available"),
        mo.md("### Carb Ratio Profile"),
        fig_carb if fig_carb is not None else mo.md("Carb ratio profile data not available"),
        mo.md("### Insulin Sensitivity Profile"),
        fig_sens if fig_sens is not None else mo.md("Sensitivity profile data not available")
    ])
    
    return fig_basal, fig_carb, fig_sens


@app.cell
def cleanup(conn_manager):
    """Ensure database connection is closed when the notebook is closed."""
    
    import atexit
    
    def cleanup_connection():
        if conn_manager.connected:
            conn_manager.disconnect()
            print("Database connection closed")
    
    # Register the cleanup function to be called when the notebook is closed
    atexit.register(cleanup_connection)
    
    return


@app.cell
def conclusion(mo):
    mo.md("""
    ## Conclusion
    
    This notebook demonstrates how to access and visualize pump data from the MongoDB database.
    You can use this as a starting point for more advanced analysis of insulin dosing patterns.
    
    ### Next Steps
    
    1. Integrate pump data with CGM data for correlation analysis
    2. Analyze meal responses by combining bolus and carb data with CGM trends
    3. Identify patterns in basal rate adjustments and their effects on glucose levels
    4. Implement the `PumpDataAccess` class in the main Loopy Basic package
    """)
    return


if __name__ == "__main__":
    app.run()