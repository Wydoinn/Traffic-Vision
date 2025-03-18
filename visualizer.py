import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os

# Enable pandas Copy-on-Write mode to prevent SettingWithCopyWarning
pd.options.mode.copy_on_write = True

# Set page configuration
st.set_page_config(
    page_title="Traffic Analytics Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to connect to the SQLite database
@st.cache_resource
def get_connection(db_path):
    return sqlite3.connect(db_path, check_same_thread=False)

# Function to load session data
@st.cache_data
def load_sessions(_conn):
    return pd.read_sql_query("SELECT * FROM sessions ORDER BY start_time DESC", _conn)

# Function to load vehicle counts data for a specific session
@st.cache_data
def load_vehicle_counts(_conn, session_id):
    query = """
    SELECT timestamp, zone_name, car, truck, bus, motorcycle, bicycle, total
    FROM zone_vehicle_counts
    WHERE session_id = ?
    ORDER BY timestamp
    """
    return pd.read_sql_query(query, _conn, params=(session_id,))

# Function to load pedestrian counts data
@st.cache_data
def load_pedestrian_counts(_conn, session_id):
    query = """
    SELECT timestamp, zone_name, count
    FROM zone_pedestrian_counts
    WHERE session_id = ?
    ORDER BY timestamp
    """
    return pd.read_sql_query(query, _conn, params=(session_id,))

# Function to load vehicle speeds data
@st.cache_data
def load_vehicle_speeds(_conn, session_id):
    query = """
    SELECT timestamp, vehicle_type, speed, zone_name
    FROM vehicle_speeds
    WHERE session_id = ?
    ORDER BY timestamp
    """
    return pd.read_sql_query(query, _conn, params=(session_id,))

# Function to load traffic light states
@st.cache_data
def load_traffic_lights(_conn, session_id):
    query = """
    SELECT timestamp, intersection_id, light_id, state, duration, is_adaptive_mode
    FROM traffic_light_states
    WHERE session_id = ?
    ORDER BY timestamp
    """
    return pd.read_sql_query(query, _conn, params=(session_id,))

# Function to load events data
@st.cache_data
def load_events(_conn, session_id):
    query = """
    SELECT timestamp, event_type, details
    FROM events
    WHERE session_id = ?
    ORDER BY timestamp
    """
    return pd.read_sql_query(query, _conn, params=(session_id,))

# Function to load heatmap data
@st.cache_data
def load_heatmap_data(_conn, session_id):
    query = """
    SELECT timestamp, zone_name, average_intensity, max_intensity
    FROM heatmap_data
    WHERE session_id = ?
    ORDER BY timestamp
    """
    return pd.read_sql_query(query, _conn, params=(session_id,))

# Function to get session statistics
@st.cache_data
def get_session_stats(_conn, session_id):
    # Get session duration
    query = "SELECT start_time, end_time FROM sessions WHERE session_id = ?"
    session_data = pd.read_sql_query(query, _conn, params=(session_id,))

    if session_data.empty:
        return {}

    stats = {}
    stats["start_time"] = session_data["start_time"][0]

    if pd.notna(session_data["end_time"][0]):
        stats["end_time"] = session_data["end_time"][0]

        start_time = pd.to_datetime(stats["start_time"]).to_pydatetime()
        end_time = pd.to_datetime(stats["end_time"]).to_pydatetime()

        stats["duration"] = (end_time - start_time).total_seconds() / 60
    else:
        stats["end_time"] = "Still running"
        stats["duration"] = "N/A"

    # Total vehicles
    query = "SELECT SUM(total) as total_vehicles FROM zone_vehicle_counts WHERE session_id = ?"
    result = pd.read_sql_query(query, _conn, params=(session_id,))
    stats["total_vehicles"] = result["total_vehicles"][0] if pd.notna(result["total_vehicles"][0]) else 0

    # Total pedestrians
    query = "SELECT SUM(count) as total_pedestrians FROM zone_pedestrian_counts WHERE session_id = ?"
    result = pd.read_sql_query(query, _conn, params=(session_id,))
    stats["total_pedestrians"] = result["total_pedestrians"][0] if pd.notna(result["total_pedestrians"][0]) else 0

    # Total events
    query = "SELECT COUNT(*) as event_count FROM events WHERE session_id = ?"
    result = pd.read_sql_query(query, _conn, params=(session_id,))
    stats["event_count"] = result["event_count"][0]

    return stats

def main():
    st.title("Traffic Analytics Dashboard 🚦")

    # Sidebar for database connection and session selection
    st.sidebar.header("Database Connection")

    db_path = st.sidebar.text_input(
        "Database Path",
        value="data/traffic_data.db",
        help="Path to the SQLite database file"
    )

    if not os.path.exists(db_path):
        st.sidebar.error(f"Database file not found: {db_path}")
        return

    try:
        conn = get_connection(db_path)
        sessions_df = load_sessions(conn)

        if sessions_df.empty:
            st.warning("No recording sessions found in the database.")
            return

        # Session selection
        st.sidebar.header("Session Selection")

        # Format session options for selection
        session_options = []
        for _, row in sessions_df.iterrows():
            session_id = row["session_id"]
            start_time = row["start_time"]
            notes = row["notes"] if pd.notna(row["notes"]) else "No notes"
            label = f"Session {session_id} - {start_time} - {notes[:20]}..."
            session_options.append((label, session_id))

        selected_session_id = st.sidebar.selectbox(
            "Select Recording Session:",
            options=[sid for _, sid in session_options],
            format_func=lambda x: next((label for label, sid in session_options if sid == x), x)
        )

        # Get session statistics
        stats = get_session_stats(conn, selected_session_id)

        # Display session information
        st.header("Session Information")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Start Time", stats.get("start_time", "N/A")[:16])

        with col2:
            st.metric("End Time", str(stats.get("end_time", "N/A"))[:16])

        with col3:
            st.metric("Total Vehicles", int(stats.get("total_vehicles", 0)))

        with col4:
            st.metric("Total Pedestrians", int(stats.get("total_pedestrians", 0)))

        # Load all necessary data for the selected session
        vehicle_counts_df = load_vehicle_counts(conn, selected_session_id)
        pedestrian_counts_df = load_pedestrian_counts(conn, selected_session_id)
        vehicle_speeds_df = load_vehicle_speeds(conn, selected_session_id)
        traffic_lights_df = load_traffic_lights(conn, selected_session_id)
        events_df = load_events(conn, selected_session_id)
        heatmap_df = load_heatmap_data(conn, selected_session_id)

        # Check if data exists
        if vehicle_counts_df.empty and pedestrian_counts_df.empty and vehicle_speeds_df.empty:
            st.warning("No traffic data available for this session.")
            return

        # Convert timestamp columns to datetime
        for df in [vehicle_counts_df, pedestrian_counts_df, vehicle_speeds_df,
                  traffic_lights_df, events_df, heatmap_df]:
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Traffic Volume", "Vehicle Speeds", "Traffic Light Analysis",
            "Events & Incidents", "Heatmap Analysis"
        ])

        # Tab 1: Traffic Volume
        with tab1:
            st.header("Traffic Volume Analysis")

            if not vehicle_counts_df.empty:
                # Time series of total vehicles by zone
                st.subheader("Vehicle Volume Over Time")

                # Get unique zones
                zones = vehicle_counts_df['zone_name'].unique()
                selected_zones = st.multiselect("Select Zones", options=zones, default=zones)

                if selected_zones:
                    mask = vehicle_counts_df['zone_name'].isin(selected_zones)
                    filtered_df = vehicle_counts_df.loc[mask].copy()

                    # Group by timestamp and zone, sum the total vehicles
                    time_series_df = filtered_df.groupby(['timestamp', 'zone_name'])['total'].sum().reset_index()

                    # Add chart type selector
                    chart_type = st.radio(
                        "Select chart type:",
                        options=["Line Chart", "Bar Chart", "Area Chart"],
                        horizontal=True,
                        key="vehicle_volume_chart_type"
                    )

                    if chart_type == "Line Chart":
                        fig = px.line(
                            time_series_df,
                            x="timestamp",
                            y="total",
                            color="zone_name",
                            title="Total Vehicle Count Over Time by Zone",
                            labels={"timestamp": "Time", "total": "Total Vehicles", "zone_name": "Zone"}
                        )
                    elif chart_type == "Bar Chart":
                        fig = px.bar(
                            time_series_df,
                            x="timestamp",
                            y="total",
                            color="zone_name",
                            title="Total Vehicle Count Over Time by Zone",
                            labels={"timestamp": "Time", "total": "Total Vehicles", "zone_name": "Zone"}
                        )
                    else:  # Area Chart
                        fig = px.area(
                            time_series_df,
                            x="timestamp",
                            y="total",
                            color="zone_name",
                            title="Total Vehicle Count Over Time by Zone",
                            labels={"timestamp": "Time", "total": "Total Vehicles", "zone_name": "Zone"}
                        )
                    st.plotly_chart(fig, use_container_width=True)

                    # Pie chart of vehicle distribution by type
                    st.subheader("Vehicle Type Distribution")

                    vehicle_types = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
                    type_totals = {vtype: filtered_df[vtype].sum() for vtype in vehicle_types}
                    vehicle_dist_df = pd.DataFrame({
                        'Vehicle Type': type_totals.keys(),
                        'Count': type_totals.values()
                    })

                    # Remove vehicle types with zero count
                    vehicle_dist_df = vehicle_dist_df[vehicle_dist_df['Count'] > 0]

                    # Add chart type selector
                    dist_chart_type = st.radio(
                        "Select chart type:",
                        options=["Pie Chart", "Bar Chart", "Donut Chart"],
                        horizontal=True,
                        key="vehicle_dist_chart_type"
                    )

                    if dist_chart_type == "Pie Chart":
                        fig = px.pie(
                            vehicle_dist_df,
                            names='Vehicle Type',
                            values='Count',
                            title="Distribution of Vehicle Types"
                        )

                        # Improve display of small percentages
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            texttemplate='%{percent:.1%}',
                            hoverinfo='label+percent+value',
                            pull=[0.05] * len(vehicle_dist_df)
                        )

                        # Adjust layout for better readability
                        fig.update_layout(
                            uniformtext_minsize=12,
                            uniformtext_mode='hide',
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.2,
                                xanchor="center",
                                x=0.5
                            )
                        )
                    elif dist_chart_type == "Bar Chart":
                        fig = px.bar(
                            vehicle_dist_df,
                            x='Vehicle Type',
                            y='Count',
                            title="Distribution of Vehicle Types",
                            color='Vehicle Type'
                        )
                    else:  # Donut Chart
                        fig = px.pie(
                            vehicle_dist_df,
                            names='Vehicle Type',
                            values='Count',
                            title="Distribution of Vehicle Types",
                            hole=0.4
                        )

                        # Improve display of small percentages
                        fig.update_traces(
                            textposition='inside',
                            textinfo='percent+label',
                            texttemplate='%{percent:.1%}',
                            hoverinfo='label+percent+value'
                        )

                        # Add total count in the center
                        total = vehicle_dist_df['Count'].sum()
                        fig.add_annotation(
                            text=f"Total:<br>{total}",
                            x=0.5, y=0.5,
                            font_size=15,
                            showarrow=False
                        )

                    st.plotly_chart(fig, use_container_width=True)

            if not pedestrian_counts_df.empty:
                st.subheader("Pedestrian Volume Over Time")

                # Get unique zones for pedestrians
                ped_zones = pedestrian_counts_df['zone_name'].unique()
                selected_ped_zones = st.multiselect(
                    "Select Pedestrian Zones",
                    options=ped_zones,
                    default=ped_zones,
                    key="ped_zones"
                )

                if selected_ped_zones:
                    mask = pedestrian_counts_df['zone_name'].isin(selected_ped_zones)
                    filtered_ped_df = pedestrian_counts_df.loc[mask].copy()

                    # Group by timestamp and zone
                    ped_time_series = filtered_ped_df.groupby(['timestamp', 'zone_name'])['count'].sum().reset_index()

                    # Add chart type selector
                    ped_chart_type = st.radio(
                        "Select chart type:",
                        options=["Line Chart", "Bar Chart", "Area Chart"],
                        horizontal=True,
                        key="pedestrian_volume_chart_type"
                    )

                    if ped_chart_type == "Line Chart":
                        fig = px.line(
                            ped_time_series,
                            x="timestamp",
                            y="count",
                            color="zone_name",
                            title="Pedestrian Count Over Time by Zone",
                            labels={"timestamp": "Time", "count": "Pedestrian Count", "zone_name": "Zone"}
                        )
                    elif ped_chart_type == "Bar Chart":
                        fig = px.bar(
                            ped_time_series,
                            x="timestamp",
                            y="count",
                            color="zone_name",
                            title="Pedestrian Count Over Time by Zone",
                            labels={"timestamp": "Time", "count": "Pedestrian Count", "zone_name": "Zone"}
                        )
                    else:  # Area Chart
                        fig = px.area(
                            ped_time_series,
                            x="timestamp",
                            y="count",
                            color="zone_name",
                            title="Pedestrian Count Over Time by Zone",
                            labels={"timestamp": "Time", "count": "Pedestrian Count", "zone_name": "Zone"}
                        )
                    st.plotly_chart(fig, use_container_width=True)

            # Compare vehicles vs pedestrians
            if not vehicle_counts_df.empty and not pedestrian_counts_df.empty:
                st.subheader("Vehicles vs Pedestrians Over Time")

                # Prepare data
                veh_time = vehicle_counts_df.groupby('timestamp')['total'].sum().reset_index()
                veh_time['type'] = 'Vehicles'
                veh_time = veh_time.rename(columns={'total': 'count'})

                ped_time = pedestrian_counts_df.groupby('timestamp')['count'].sum().reset_index()
                ped_time['type'] = 'Pedestrians'

                combined_df = pd.concat([veh_time, ped_time])

                # Add chart type selector
                compare_chart_type = st.radio(
                    "Select chart type:",
                    options=["Line Chart", "Bar Chart", "Area Chart", "Scatter Plot"],
                    horizontal=True,
                    key="compare_chart_type"
                )

                if compare_chart_type == "Line Chart":
                    fig = px.line(
                        combined_df,
                        x="timestamp",
                        y="count",
                        color="type",
                        title="Vehicles vs Pedestrians Over Time",
                        labels={"timestamp": "Time", "count": "Count", "type": "Type"}
                    )
                elif compare_chart_type == "Bar Chart":
                    fig = px.bar(
                        combined_df,
                        x="timestamp",
                        y="count",
                        color="type",
                        title="Vehicles vs Pedestrians Over Time",
                        labels={"timestamp": "Time", "count": "Count", "type": "Type"}
                    )
                elif compare_chart_type == "Area Chart":
                    fig = px.area(
                        combined_df,
                        x="timestamp",
                        y="count",
                        color="type",
                        title="Vehicles vs Pedestrians Over Time",
                        labels={"timestamp": "Time", "count": "Count", "type": "Type"}
                    )
                else:  # Scatter Plot
                    fig = px.scatter(
                        combined_df,
                        x="timestamp",
                        y="count",
                        color="type",
                        size="count",
                        title="Vehicles vs Pedestrians Over Time",
                        labels={"timestamp": "Time", "count": "Count", "type": "Type"}
                    )
                st.plotly_chart(fig, use_container_width=True)

        # Tab 2: Vehicle Speeds
        with tab2:
            st.header("Vehicle Speed Analysis")

            if not vehicle_speeds_df.empty:
                # Distribution of vehicle speeds
                st.subheader("Speed Distribution")

                # Filter by vehicle type
                vehicle_types = vehicle_speeds_df['vehicle_type'].unique()
                selected_types = st.multiselect(
                    "Select Vehicle Types",
                    options=vehicle_types,
                    default=vehicle_types,
                    key="speed_vehicle_types"
                )

                if selected_types:
                    # Create the filtered dataframe properly to avoid SettingWithCopyWarning
                    mask = vehicle_speeds_df['vehicle_type'].isin(selected_types)
                    filtered_speed_df = vehicle_speeds_df.loc[mask].copy()
                    # Now add the minute column
                    filtered_speed_df.loc[:, 'minute'] = filtered_speed_df['timestamp'].dt.floor('min')

                    # Add chart type selector
                    speed_dist_chart_type = st.radio(
                        "Select chart type:",
                        options=["Histogram", "Box Plot", "Violin Plot"],
                        horizontal=True,
                        key="speed_dist_chart_type"
                    )

                    if speed_dist_chart_type == "Histogram":
                        fig = px.histogram(
                            filtered_speed_df,
                            x="speed",
                            color="vehicle_type",
                            title="Distribution of Vehicle Speeds",
                            labels={"speed": "Speed (km/h)", "count": "Count", "vehicle_type": "Vehicle Type"},
                            nbins=30
                        )
                    elif speed_dist_chart_type == "Box Plot":
                        fig = px.box(
                            filtered_speed_df,
                            x="vehicle_type",
                            y="speed",
                            color="vehicle_type",
                            title="Distribution of Vehicle Speeds",
                            labels={"speed": "Speed (km/h)", "vehicle_type": "Vehicle Type"}
                        )
                    else:  # Violin Plot
                        fig = px.violin(
                            filtered_speed_df,
                            x="vehicle_type",
                            y="speed",
                            color="vehicle_type",
                            title="Distribution of Vehicle Speeds",
                            box=True,
                            points="all",
                            labels={"speed": "Speed (km/h)", "vehicle_type": "Vehicle Type"}
                        )

                    st.plotly_chart(fig, use_container_width=True)

                    # Average speed over time
                    st.subheader("Average Speed Over Time")

                    # Resample by minute
                    avg_speed = filtered_speed_df.groupby(['minute', 'vehicle_type'])['speed'].mean().reset_index()

                    # Add chart type selector
                    avg_speed_chart_type = st.radio(
                        "Select chart type:",
                        options=["Line Chart", "Bar Chart", "Scatter Plot"],
                        horizontal=True,
                        key="avg_speed_chart_type"
                    )

                    if avg_speed_chart_type == "Line Chart":
                        fig = px.line(
                            avg_speed,
                            x="minute",
                            y="speed",
                            color="vehicle_type",
                            title="Average Speed Over Time by Vehicle Type",
                            labels={"minute": "Time", "speed": "Average Speed (km/h)", "vehicle_type": "Vehicle Type"}
                        )
                    elif avg_speed_chart_type == "Bar Chart":
                        fig = px.bar(
                            avg_speed,
                            x="minute",
                            y="speed",
                            color="vehicle_type",
                            title="Average Speed Over Time by Vehicle Type",
                            labels={"minute": "Time", "speed": "Average Speed (km/h)", "vehicle_type": "Vehicle Type"}
                        )
                    else:  # Scatter Plot
                        fig = px.scatter(
                            avg_speed,
                            x="minute",
                            y="speed",
                            color="vehicle_type",
                            size="speed",
                            title="Average Speed Over Time by Vehicle Type",
                            labels={"minute": "Time", "speed": "Average Speed (km/h)", "vehicle_type": "Vehicle Type"}
                        )
                    st.plotly_chart(fig, use_container_width=True)

                    # Box plot for speed by vehicle type
                    st.subheader("Speed Statistics by Vehicle Type")

                    # Add chart type selector
                    speed_stats_chart_type = st.radio(
                        "Select chart type:",
                        options=["Box Plot", "Violin Plot", "Bar Chart"],
                        horizontal=True,
                        key="speed_stats_chart_type"
                    )

                    if speed_stats_chart_type == "Box Plot":
                        fig = px.box(
                            filtered_speed_df,
                            x="vehicle_type",
                            y="speed",
                            color="vehicle_type",
                            title="Speed Distribution by Vehicle Type",
                            labels={"vehicle_type": "Vehicle Type", "speed": "Speed (km/h)"}
                        )
                    elif speed_stats_chart_type == "Violin Plot":
                        fig = px.violin(
                            filtered_speed_df,
                            x="vehicle_type",
                            y="speed",
                            color="vehicle_type",
                            title="Speed Distribution by Vehicle Type",
                            box=True,
                            points="all",
                            labels={"vehicle_type": "Vehicle Type", "speed": "Speed (km/h)"}
                        )
                    else:  # Bar Chart
                        # Calculate mean, min, max for each vehicle type
                        stats_df = filtered_speed_df.groupby('vehicle_type')['speed'].agg(['mean', 'min', 'max']).reset_index()
                        stats_df = pd.melt(stats_df, id_vars=['vehicle_type'],
                                          value_vars=['mean', 'min', 'max'],
                                          var_name='Statistic', value_name='Speed')

                        fig = px.bar(
                            stats_df,
                            x="vehicle_type",
                            y="Speed",
                            color="Statistic",
                            barmode="group",
                            title="Speed Statistics by Vehicle Type",
                            labels={"vehicle_type": "Vehicle Type", "Speed": "Speed (km/h)"}
                        )
                    st.plotly_chart(fig, use_container_width=True)

                    # If zone information is available
                    if 'zone_name' in filtered_speed_df.columns and filtered_speed_df['zone_name'].notna().any():
                        st.subheader("Average Speed by Zone")
                        zone_speed = filtered_speed_df.groupby('zone_name')['speed'].mean().reset_index()

                        # Add chart type selector
                        zone_speed_chart_type = st.radio(
                            "Select chart type:",
                            options=["Bar Chart", "Horizontal Bar", "Scatter Plot"],
                            horizontal=True,
                            key="zone_speed_chart_type"
                        )

                        if zone_speed_chart_type == "Bar Chart":
                            fig = px.bar(
                                zone_speed,
                                x="zone_name",
                                y="speed",
                                title="Average Speed by Zone",
                                labels={"zone_name": "Zone", "speed": "Average Speed (km/h)"},
                                color="speed",
                                color_continuous_scale="Viridis"
                            )
                        elif zone_speed_chart_type == "Horizontal Bar":
                            fig = px.bar(
                                zone_speed,
                                y="zone_name",
                                x="speed",
                                title="Average Speed by Zone",
                                labels={"zone_name": "Zone", "speed": "Average Speed (km/h)"},
                                color="speed",
                                color_continuous_scale="Viridis",
                                orientation='h'
                            )
                        else:  # Scatter Plot
                            fig = px.scatter(
                                zone_speed,
                                x="zone_name",
                                y="speed",
                                title="Average Speed by Zone",
                                labels={"zone_name": "Zone", "speed": "Average Speed (km/h)"},
                                size="speed",
                                color="speed",
                                color_continuous_scale="Viridis"
                            )
                        st.plotly_chart(fig, use_container_width=True)

        # Tab 3: Traffic Light Analysis
        with tab3:
            st.header("Traffic Light Analysis")

            if not traffic_lights_df.empty:
                # Get unique intersections
                intersections = traffic_lights_df['intersection_id'].unique()
                selected_intersection = st.selectbox("Select Intersection", options=intersections)

                # Filter by selected intersection using .loc
                mask = traffic_lights_df['intersection_id'] == selected_intersection
                intersection_df = traffic_lights_df.loc[mask].copy()

                # Get unique traffic lights in this intersection
                lights = intersection_df['light_id'].unique()

                # Display state changes over time
                st.subheader("Traffic Light State Timeline")

                # Add chart type selector
                tl_timeline_chart_type = st.radio(
                    "Select chart type:",
                    options=["Line Chart", "Scatter Plot", "Heatmap"],
                    horizontal=True,
                    key="tl_timeline_chart_type"
                )

                if tl_timeline_chart_type in ["Line Chart", "Scatter Plot"]:
                    # Create a figure for traffic light states
                    fig = go.Figure()

                    for light in lights:
                        # Filter light data using .loc
                        mask = intersection_df['light_id'] == light
                        light_data = intersection_df.loc[mask].copy()

                        # Map states to numeric values for visualization
                        state_map = {'RED': 0, 'YELLOW': 1, 'GREEN': 2}
                        light_data.loc[:, 'state_value'] = light_data['state'].map(state_map)

                        if tl_timeline_chart_type == "Line Chart":
                            fig.add_trace(go.Scatter(
                                x=light_data['timestamp'],
                                y=light_data['state_value'],
                                mode='lines+markers',
                                name=light,
                                text=light_data['state'],
                                hovertemplate='%{text}<br>Time: %{x}<extra></extra>'
                            ))
                        else:  # Scatter Plot
                            fig.add_trace(go.Scatter(
                                x=light_data['timestamp'],
                                y=light_data['state_value'],
                                mode='markers',
                                name=light,
                                text=light_data['state'],
                                marker=dict(
                                    size=10,
                                    opacity=0.8
                                ),
                                hovertemplate='%{text}<br>Time: %{x}<extra></extra>'
                            ))

                    fig.update_layout(
                        title=f"Traffic Light States - {selected_intersection}",
                        xaxis_title="Time",
                        yaxis=dict(
                            tickmode='array',
                            tickvals=[0, 1, 2],
                            ticktext=['RED', 'YELLOW', 'GREEN']
                        ),
                        legend_title="Traffic Lights"
                    )
                else:  # Heatmap
                    # Prepare data for heatmap
                    pivot_data = []
                    for light in lights:
                        mask = intersection_df['light_id'] == light
                        light_data = intersection_df.loc[mask].copy()

                        # Map states to numeric values
                        state_map = {'RED': 0, 'YELLOW': 1, 'GREEN': 2}
                        for _, row in light_data.iterrows():
                            pivot_data.append({
                                'timestamp': row['timestamp'],
                                'light_id': row['light_id'],
                                'state_value': state_map.get(row['state'], 0)
                            })

                    pivot_df = pd.DataFrame(pivot_data)
                    # If timestamps are too granular, resample
                    pivot_df['timestamp'] = pd.to_datetime(pivot_df['timestamp'])
                    pivot_df['minute'] = pivot_df['timestamp'].dt.floor('min')

                    # Create pivot table
                    heat_pivot = pivot_df.pivot_table(
                        index='minute',
                        columns='light_id',
                        values='state_value',
                        aggfunc='max'
                    ).fillna(0)

                    # Create heatmap
                    fig = px.imshow(
                        heat_pivot,
                        labels=dict(x="Traffic Light", y="Time", color="State"),
                        title=f"Traffic Light States Heatmap - {selected_intersection}",
                        color_continuous_scale=["red", "gold", "green"],
                        aspect="auto"
                    )

                    # Customize appearance
                    fig.update_layout(
                        coloraxis=dict(
                            cmin=0,
                            cmax=2,
                            colorbar=dict(
                                tickvals=[0, 1, 2],
                                ticktext=['RED', 'YELLOW', 'GREEN']
                            )
                        )
                    )

                st.plotly_chart(fig, use_container_width=True)

                # State duration analysis
                st.subheader("State Duration Analysis")

                # Add chart type selector
                duration_chart_type = st.radio(
                    "Select chart type:",
                    options=["Bar Chart", "Horizontal Bar", "Box Plot"],
                    horizontal=True,
                    key="duration_chart_type"
                )

                # Group by light_id and state, get average duration
                duration_df = intersection_df.groupby(['light_id', 'state'])['duration'].mean().reset_index()

                if duration_chart_type == "Bar Chart":
                    fig = px.bar(
                        duration_df,
                        x="light_id",
                        y="duration",
                        color="state",
                        barmode="group",
                        title="Average Duration by Light and State",
                        labels={"light_id": "Traffic Light", "duration": "Average Duration (s)", "state": "State"}
                    )
                elif duration_chart_type == "Horizontal Bar":
                    fig = px.bar(
                        duration_df,
                        y="light_id",
                        x="duration",
                        color="state",
                        barmode="group",
                        title="Average Duration by Light and State",
                        labels={"light_id": "Traffic Light", "duration": "Average Duration (s)", "state": "State"},
                        orientation='h'
                    )
                else:  # Box Plot
                    fig = px.box(
                        intersection_df,
                        x="light_id",
                        y="duration",
                        color="state",
                        title="Duration Distribution by Light and State",
                        labels={"light_id": "Traffic Light", "duration": "Duration (s)", "state": "State"}
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Adaptive vs Fixed timing
                st.subheader("Adaptive vs Fixed Timing")

                # Convert boolean is_adaptive_mode to human-readable strings
                intersection_df['mode_type'] = intersection_df['is_adaptive_mode'].map({1: "Adaptive Mode", 0: "Fixed Mode"})

                # Count records by mode and time period
                # First convert timestamp to a proper datetime if it's not already
                if not pd.api.types.is_datetime64_any_dtype(intersection_df['timestamp']):
                    intersection_df['timestamp'] = pd.to_datetime(intersection_df['timestamp'])

                # Group by timestamp (rounded to minute for aggregation) and mode type
                adaptive_counts = intersection_df.groupby([
                    pd.Grouper(key='timestamp', freq='1min'),
                    'mode_type'
                ]).size().reset_index(name='count')

                # Check if we have both adaptive and fixed timing data
                mode_types = adaptive_counts['mode_type'].unique()

                if len(mode_types) > 0:
                    # Add chart type selector
                    adaptive_chart_type = st.radio(
                        "Select chart type:",
                        options=["Line Chart", "Bar Chart", "Area Chart", "Stacked Area"],
                        horizontal=True,
                        key="adaptive_chart_type"
                    )

                    if adaptive_chart_type == "Line Chart":
                        fig = px.line(
                            adaptive_counts,
                            x="timestamp",
                            y="count",
                            color="mode_type",
                            title="Traffic Light Mode Over Time",
                            labels={
                                "timestamp": "Time",
                                "count": "Number of Signals",
                                "mode_type": "Mode"
                            }
                        )
                    elif adaptive_chart_type == "Bar Chart":
                        fig = px.bar(
                            adaptive_counts,
                            x="timestamp",
                            y="count",
                            color="mode_type",
                            title="Traffic Light Mode Over Time",
                            labels={
                                "timestamp": "Time",
                                "count": "Number of Signals",
                                "mode_type": "Mode"
                            }
                        )
                    elif adaptive_chart_type == "Area Chart":
                        fig = px.area(
                            adaptive_counts,
                            x="timestamp",
                            y="count",
                            color="mode_type",
                            title="Traffic Light Mode Over Time",
                            labels={
                                "timestamp": "Time",
                                "count": "Number of Signals",
                                "mode_type": "Mode"
                            }
                        )
                    else:  # Stacked Area
                        fig = px.area(
                            adaptive_counts,
                            x="timestamp",
                            y="count",
                            color="mode_type",
                            title="Traffic Light Mode Over Time",
                            labels={
                                "timestamp": "Time",
                                "count": "Number of Signals",
                                "mode_type": "Mode"
                            },
                            groupnorm="fraction"
                        )

                    # Ensure y-axis starts from zero to avoid misleading visualization
                    fig.update_yaxes(rangemode="tozero")

                    # Add a hover template to show more details
                    fig.update_traces(
                        hovertemplate="<b>%{y}</b> signals in %{customdata} at %{x}<extra></extra>",
                        customdata=adaptive_counts['mode_type']
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No timing mode changes detected in this session.")

                # Also show a summary pie chart of adaptive vs fixed
                mode_summary = intersection_df['mode_type'].value_counts().reset_index()
                mode_summary.columns = ['Mode', 'Count']

                if not mode_summary.empty:
                    # Add chart type selector
                    mode_summary_chart_type = st.radio(
                        "Select chart type:",
                        options=["Pie Chart", "Bar Chart", "Donut Chart"],
                        horizontal=True,
                        key="mode_summary_chart_type"
                    )

                    if mode_summary_chart_type == "Pie Chart":
                        fig = px.pie(
                            mode_summary,
                            values='Count',
                            names='Mode',
                            title='Distribution of Traffic Light Modes'
                        )
                    elif mode_summary_chart_type == "Bar Chart":
                        fig = px.bar(
                            mode_summary,
                            x='Mode',
                            y='Count',
                            color='Mode',
                            title='Distribution of Traffic Light Modes'
                        )
                    else:  # Donut Chart
                        fig = px.pie(
                            mode_summary,
                            values='Count',
                            names='Mode',
                            title='Distribution of Traffic Light Modes',
                            hole=0.4
                        )
                    st.plotly_chart(fig, use_container_width=True)

        # Tab 4: Events & Incidents
        with tab4:
            st.header("Events & Incidents Analysis")

            if not events_df.empty:
                # Display events on a timeline
                st.subheader("Events Timeline")

                # Convert event_type to a category
                events_df.loc[:, 'event_type'] = events_df['event_type'].astype('category')

                # Add chart type selector
                events_timeline_chart_type = st.radio(
                    "Select chart type:",
                    options=["Scatter Plot", "Gantt Chart"],
                    horizontal=True,
                    key="events_timeline_chart_type"
                )

                if events_timeline_chart_type == "Scatter Plot":
                    fig = px.scatter(
                        events_df,
                        x="timestamp",
                        y="event_type",
                        color="event_type",
                        hover_data=["details"],
                        title="Events Timeline",
                        labels={"timestamp": "Time", "event_type": "Event Type", "details": "Details"},
                        size=[10] * len(events_df)
                    )
                else:  # Gantt Chart-like visualization
                    # Create a figure
                    fig = go.Figure()

                    # Get unique event types and assign them y-coordinates
                    event_types = events_df['event_type'].unique()
                    event_y = {event: i for i, event in enumerate(event_types)}

                    # Add line segments for events
                    for idx, event in events_df.iterrows():
                        y_pos = event_y[event['event_type']]
                        fig.add_trace(go.Scatter(
                            x=[event['timestamp']],
                            y=[y_pos],
                            mode="markers+text",
                            text=[event['event_type']],
                            textposition="middle right",
                            name=event['event_type'],
                            hoverinfo="text",
                            hovertext=f"{event['event_type']}<br>{event['timestamp']}<br>{event['details']}",
                            marker=dict(size=15, symbol="diamond")
                        ))

                    # Update layout
                    fig.update_layout(
                        title="Events Timeline (Gantt-style)",
                        xaxis_title="Time",
                        yaxis=dict(
                            tickmode='array',
                            tickvals=list(event_y.values()),
                            ticktext=list(event_y.keys()),
                            title="Event Type"
                        ),
                        showlegend=False
                    )

                # Apply common layout updates for all chart types
                if events_timeline_chart_type != "Gantt Chart":
                    fig.update_layout(yaxis=dict(categoryorder="category descending"))

                st.plotly_chart(fig, use_container_width=True)

                # Add a dedicated emergency vehicle analysis section
                if 'emergency' in events_df['event_type'].values:
                    st.subheader("Emergency Vehicle Analysis")

                    # Extract emergency vehicle types from details
                    emergency_events = events_df[events_df['event_type'] == 'emergency'].copy()

                    # Extract vehicle types from details column
                    def extract_vehicle_type(detail_text):
                        if 'Ambulance' in detail_text:
                            return 'Ambulance'
                        elif 'Firetruck' in detail_text:
                            return 'Firetruck'
                        else:
                            return 'Unknown Emergency'

                    emergency_events.loc[:, 'vehicle_type'] = emergency_events['details'].apply(extract_vehicle_type)

                    # Count by vehicle type
                    vehicle_type_counts = emergency_events['vehicle_type'].value_counts().reset_index()
                    vehicle_type_counts.columns = ['Vehicle Type', 'Count']

                    # Vehicle type distribution
                    fig = px.pie(
                        vehicle_type_counts,
                        values="Count",
                        names="Vehicle Type",
                        title="Emergency Vehicle Types",
                        color_discrete_map={
                            'Ambulance': '#ff9999',
                            'Firetruck': '#ff5555',
                            'Unknown Emergency': '#aaaaaa'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Timeline of emergency vehicles
                    fig = px.scatter(
                        emergency_events,
                        x="timestamp",
                        y="vehicle_type",
                        color="vehicle_type",
                        size=[15] * len(emergency_events),
                        title="Emergency Vehicles Timeline",
                        labels={"timestamp": "Time", "vehicle_type": "Vehicle Type"}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Display events in a table
                st.subheader("Events Log")

                # Format timestamp for display
                events_display = events_df.copy()
                events_display.loc[:, 'timestamp'] = events_display['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

                st.dataframe(
                    events_display[['timestamp', 'event_type', 'details']],
                    use_container_width=True
                )

                # Count events by type
                st.subheader("Events by Type")
                event_counts = events_df['event_type'].value_counts().reset_index()
                event_counts.columns = ['Event Type', 'Count']

                # Add chart type selector
                events_count_chart_type = st.radio(
                    "Select chart type:",
                    options=["Bar Chart", "Horizontal Bar", "Pie Chart", "Treemap"],
                    horizontal=True,
                    key="events_count_chart_type"
                )

                if events_count_chart_type == "Bar Chart":
                    fig = px.bar(
                        event_counts,
                        x="Event Type",
                        y="Count",
                        title="Number of Events by Type",
                        color="Event Type"
                    )
                elif events_count_chart_type == "Horizontal Bar":
                    fig = px.bar(
                        event_counts,
                        y="Event Type",
                        x="Count",
                        title="Number of Events by Type",
                        color="Event Type",
                        orientation='h'
                    )
                elif events_count_chart_type == "Pie Chart":
                    fig = px.pie(
                        event_counts,
                        values="Count",
                        names="Event Type",
                        title="Distribution of Events by Type"
                    )
                else:  # Treemap
                    fig = px.treemap(
                        event_counts,
                        path=["Event Type"],
                        values="Count",
                        title="Distribution of Events by Type",
                        color="Count",
                        color_continuous_scale="Viridis"
                    )
                st.plotly_chart(fig, use_container_width=True)

        # Tab 5: Heatmap Analysis
        with tab5:
            st.header("Traffic Density Heatmap Analysis")

            if not heatmap_df.empty:
                # Get unique zones
                heatmap_zones = heatmap_df['zone_name'].unique()
                selected_hm_zone = st.selectbox("Select Zone", options=heatmap_zones, key="heatmap_zone")

                # Filter by selected zone using .loc
                mask = heatmap_df['zone_name'] == selected_hm_zone
                zone_heatmap_df = heatmap_df.loc[mask].copy()

                # Display average intensity over time
                st.subheader("Traffic Density Over Time")

                # Add chart type selector
                density_time_chart_type = st.radio(
                    "Select chart type:",
                    options=["Line Chart", "Area Chart", "Bar Chart", "Scatter Plot"],
                    horizontal=True,
                    key="density_time_chart_type"
                )

                if density_time_chart_type == "Line Chart":
                    fig = px.line(
                        zone_heatmap_df,
                        x="timestamp",
                        y="average_intensity",
                        title=f"Average Traffic Density - {selected_hm_zone}",
                        labels={"timestamp": "Time", "average_intensity": "Average Density"}
                    )
                    # Add max intensity line
                    fig.add_scatter(
                        x=zone_heatmap_df["timestamp"],
                        y=zone_heatmap_df["max_intensity"],
                        mode="lines",
                        name="Max Density",
                        line=dict(dash="dash")
                    )
                elif density_time_chart_type == "Area Chart":
                    fig = px.area(
                        zone_heatmap_df,
                        x="timestamp",
                        y="average_intensity",
                        title=f"Average Traffic Density - {selected_hm_zone}",
                        labels={"timestamp": "Time", "average_intensity": "Average Density"}
                    )
                    # Add max intensity line on top of area chart
                    fig.add_scatter(
                        x=zone_heatmap_df["timestamp"],
                        y=zone_heatmap_df["max_intensity"],
                        mode="lines",
                        name="Max Density",
                        line=dict(dash="dash")
                    )
                elif density_time_chart_type == "Bar Chart":
                    # Prepare data with both metrics
                    density_df = pd.melt(
                        zone_heatmap_df,
                        id_vars=['timestamp', 'zone_name'],
                        value_vars=['average_intensity', 'max_intensity'],
                        var_name='Metric',
                        value_name='Value'
                    )
                    density_df['Metric'] = density_df['Metric'].map({
                        'average_intensity': 'Average Density',
                        'max_intensity': 'Maximum Density'
                    })

                    fig = px.bar(
                        density_df,
                        x="timestamp",
                        y="Value",
                        color="Metric",
                        title=f"Traffic Density - {selected_hm_zone}",
                        labels={"timestamp": "Time", "Value": "Density", "Metric": "Measurement"}
                    )
                else:  # Scatter Plot
                    fig = px.scatter(
                        zone_heatmap_df,
                        x="timestamp",
                        y="average_intensity",
                        title=f"Average Traffic Density - {selected_hm_zone}",
                        labels={"timestamp": "Time", "average_intensity": "Average Density"},
                        size="average_intensity",
                        color="average_intensity",
                        color_continuous_scale="Viridis"
                    )
                    # Add max intensity trend
                    fig.add_scatter(
                        x=zone_heatmap_df["timestamp"],
                        y=zone_heatmap_df["max_intensity"],
                        mode="markers+lines",
                        name="Max Density",
                        marker=dict(size=8)
                    )

                st.plotly_chart(fig, use_container_width=True)

                # Zone comparison
                st.subheader("Zone Density Comparison")

                # Calculate average density per zone
                zone_avg = heatmap_df.groupby('zone_name')['average_intensity'].mean().reset_index()
                zone_avg = zone_avg.sort_values('average_intensity', ascending=False)

                # Add chart type selector
                zone_comparison_chart_type = st.radio(
                    "Select chart type:",
                    options=["Bar Chart", "Horizontal Bar", "Scatter Plot", "Pie Chart"],
                    horizontal=True,
                    key="zone_comparison_chart_type"
                )

                if zone_comparison_chart_type == "Bar Chart":
                    fig = px.bar(
                        zone_avg,
                        x="zone_name",
                        y="average_intensity",
                        title="Average Traffic Density by Zone",
                        labels={"zone_name": "Zone", "average_intensity": "Average Density"},
                        color="average_intensity",
                        color_continuous_scale="Viridis"
                    )
                elif zone_comparison_chart_type == "Horizontal Bar":
                    fig = px.bar(
                        zone_avg,
                        y="zone_name",
                        x="average_intensity",
                        title="Average Traffic Density by Zone",
                        labels={"zone_name": "Zone", "average_intensity": "Average Density"},
                        color="average_intensity",
                        color_continuous_scale="Viridis",
                        orientation='h'
                    )
                elif zone_comparison_chart_type == "Scatter Plot":
                    fig = px.scatter(
                        zone_avg,
                        x="zone_name",
                        y="average_intensity",
                        title="Average Traffic Density by Zone",
                        labels={"zone_name": "Zone", "average_intensity": "Average Density"},
                        size="average_intensity",
                        color="average_intensity",
                        color_continuous_scale="Viridis",
                        size_max=30
                    )
                else:  # Pie Chart
                    fig = px.pie(
                        zone_avg,
                        values="average_intensity",
                        names="zone_name",
                        title="Relative Traffic Density by Zone"
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Traffic density heatmap over time
                st.subheader("Density Heatmap Over Time")

                # Add chart type selector
                time_density_chart_type = st.radio(
                    "Select chart type:",
                    options=["Heatmap", "3D Surface"],
                    horizontal=True,
                    key="time_density_chart_type"
                )

                # Create a pivot table with timestamps as rows and zones as columns
                pivot_df = heatmap_df.pivot_table(
                    index='timestamp',
                    columns='zone_name',
                    values='average_intensity',
                    aggfunc='mean'
                )

                # Resample to reduce number of rows if necessary
                if len(pivot_df) > 50:
                    pivot_df = pivot_df.resample('5min').mean()

                if time_density_chart_type == "Heatmap":
                    fig = px.imshow(
                        pivot_df,
                        aspect="auto",
                        title="Traffic Density Over Time and Zones",
                        labels=dict(x="Zone", y="Time", color="Density"),
                        color_continuous_scale="Viridis"
                    )
                else:  # 3D Surface
                    # Prepare data for surface plot
                    # Convert to numpy arrays for surface plot
                    z_data = pivot_df.values

                    # Create the figure with a Surface trace
                    fig = go.Figure(data=[go.Surface(
                        z=z_data,
                        x=list(pivot_df.columns),
                        y=[str(idx)[:16] for idx in pivot_df.index],
                        colorscale='Viridis',
                        colorbar=dict(title="Density")
                    )])

                    fig.update_layout(
                        title="3D Traffic Density Surface Plot",
                        scene=dict(
                            xaxis_title="Zone",
                            yaxis_title="Time",
                            zaxis_title="Density"
                        ),
                        margin=dict(l=65, r=50, b=65, t=90)
                    )

                st.plotly_chart(fig, use_container_width=True)

        # Footer
        st.markdown("---")
        st.markdown("<div style='text-align: center'>Traffic Analytics Dashboard</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        import traceback
        st.exception(traceback.format_exc())

if __name__ == "__main__":
    main()
