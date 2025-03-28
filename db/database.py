import sqlite3
import threading
import os
from datetime import datetime, timezone
from typing import Dict, List, Any
from logger import logger


class TrafficDatabase:
    """
    Handles SQLite database operations for traffic data collection.
    Stores various traffic metrics for later analysis and visualization.
    """
    def __init__(self, db_path: str = "data/traffic_data.db"):
        """Initialize database connection and ensure tables exist."""
        self.db_path = db_path
        self.local = threading.local()
        self.local.conn = None
        self.local.cursor = None
        self.connect()
        self.create_tables()

    def ensure_db_directory(self):
        """Make sure the directory for the database file exists."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir)
                logger.info(f"Created directory: {db_dir}")
            except OSError as e:
                logger.error(f"Error creating directory {db_dir}: {e}")
                raise

    def connect(self):
        """Establish connection to the SQLite database - creates a thread-local connection."""
        try:
            # Ensure directory exists before connecting
            self.ensure_db_directory()

            # Create a new connection for this thread if one doesn't exist
            if not hasattr(self.local, 'conn') or self.local.conn is None:
                self.local.conn = sqlite3.connect(self.db_path)
                self.local.conn.row_factory = sqlite3.Row
                self.local.cursor = self.local.conn.cursor()
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def ensure_connection(self):
        """Ensure this thread has an active connection before performing operations."""
        if not hasattr(self.local, 'conn') or self.local.conn is None:
            self.connect()

    def create_tables(self):
        """Create all necessary tables if they don't exist."""
        self.ensure_connection()
        try:
            # Sessions table to group data collection periods
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                video_path TEXT,
                notes TEXT
            )
            ''')

            # Vehicle counts per zone
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS zone_vehicle_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                zone_name TEXT NOT NULL,
                car INTEGER DEFAULT 0,
                truck INTEGER DEFAULT 0,
                bus INTEGER DEFAULT 0,
                motorcycle INTEGER DEFAULT 0,
                bicycle INTEGER DEFAULT 0,
                total INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')

            # Pedestrian counts per zone
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS zone_pedestrian_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                zone_name TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')

            # Vehicle speeds data
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_speeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                vehicle_type TEXT NOT NULL,
                speed REAL NOT NULL,
                tracker_id INTEGER NOT NULL,
                zone_name TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')

            # Traffic light states
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS traffic_light_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                intersection_id TEXT NOT NULL,
                light_id TEXT NOT NULL,
                state TEXT NOT NULL,
                duration INTEGER,
                is_adaptive_mode BOOLEAN DEFAULT 1,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')

            # Emergency and accident events
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                event_type TEXT NOT NULL,
                details TEXT,
                duration INTEGER,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')

            # Heatmap intensity data
            self.local.cursor.execute('''
            CREATE TABLE IF NOT EXISTS heatmap_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TIMESTAMP NOT NULL,
                zone_name TEXT NOT NULL,
                average_intensity REAL NOT NULL,
                max_intensity REAL NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
            ''')

            # Creating indices for faster querying
            self.local.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_zone_vehicle_timestamp
            ON zone_vehicle_counts(timestamp)
            ''')

            self.local.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_zone_pedestrian_timestamp
            ON zone_pedestrian_counts(timestamp)
            ''')

            self.local.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_vehicle_speeds_timestamp
            ON vehicle_speeds(timestamp)
            ''')

            self.local.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_traffic_lights_timestamp
            ON traffic_light_states(timestamp)
            ''')

            self.local.conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            self.local.conn.rollback()
            raise

    def get_current_time(self):
        """Return timezone-aware current datetime."""
        return datetime.now(timezone.utc)

    def start_new_session(self, video_path: str = None, notes: str = None) -> int:
        """Start a new data collection session and return its ID."""
        self.ensure_connection()
        try:
            current_time = self.get_current_time()
            self.local.cursor.execute(
                "INSERT INTO sessions (start_time, video_path, notes) VALUES (?, ?, ?)",
                (current_time, video_path, notes)
            )
            self.local.conn.commit()
            return self.local.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Error starting session: {e}")
            self.local.conn.rollback()
            return -1

    def end_session(self, session_id: int) -> bool:
        """End a data collection session."""
        self.ensure_connection()
        try:
            current_time = self.get_current_time()
            self.local.cursor.execute(
                "UPDATE sessions SET end_time = ? WHERE session_id = ?",
                (current_time, session_id)
            )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error ending session: {e}")
            self.local.conn.rollback()
            return False

    def record_vehicle_counts(self, session_id: int, zone_counts: Dict[str, Dict[str, int]]) -> bool:
        """Record vehicle counts for all zones."""
        self.ensure_connection()
        current_time = self.get_current_time()
        try:
            for zone_name, counts in zone_counts.items():
                total = sum(counts.values())
                self.local.cursor.execute(
                    """
                    INSERT INTO zone_vehicle_counts
                    (session_id, timestamp, zone_name, car, truck, bus, motorcycle, bicycle, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        current_time,
                        zone_name,
                        counts.get("car", 0),
                        counts.get("truck", 0),
                        counts.get("bus", 0),
                        counts.get("motorcycle", 0),
                        counts.get("bicycle", 0),
                        total
                    )
                )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error recording vehicle counts: {e}")
            try:
                self.local.conn.rollback()
            except:
                self.connect()
            return False

    def record_pedestrian_counts(self, session_id: int, zone_counts: Dict[str, int]) -> bool:
        """Record pedestrian counts for all zones."""
        self.ensure_connection()
        current_time = self.get_current_time()
        try:
            for zone_name, count in zone_counts.items():
                self.local.cursor.execute(
                    "INSERT INTO zone_pedestrian_counts (session_id, timestamp, zone_name, count) VALUES (?, ?, ?, ?)",
                    (session_id, current_time, zone_name, count)
                )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error recording pedestrian counts: {e}")
            try:
                self.local.conn.rollback()
            except:
                self.connect()
            return False

    def record_vehicle_speeds(self, session_id: int, speeds_data: List[Dict[str, Any]]) -> bool:
        """
        Record individual vehicle speeds.
        """
        self.ensure_connection()
        if not speeds_data:
            return True

        current_time = self.get_current_time()
        try:
            for data in speeds_data:
                self.local.cursor.execute(
                    """
                    INSERT INTO vehicle_speeds
                    (session_id, timestamp, vehicle_type, speed, tracker_id, zone_name)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        current_time,
                        data.get("vehicle_type", "unknown"),
                        data.get("speed", 0.0),
                        data.get("tracker_id", -1),
                        data.get("zone_name")
                    )
                )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error recording vehicle speeds: {e}")
            try:
                self.local.conn.rollback()
            except:
                self.connect()
            return False

    def record_traffic_light_states(self, session_id: int, light_states: Dict[str, Any]) -> bool:
        """Record traffic light states for all intersections."""
        self.ensure_connection()
        current_time = self.get_current_time()
        try:
            for intersection_id, data in light_states.items():
                is_adaptive = data.get("is_adaptive_mode", True)
                for light in data.get("lights", []):
                    self.local.cursor.execute(
                        """
                        INSERT INTO traffic_light_states
                        (session_id, timestamp, intersection_id, light_id, state, duration, is_adaptive_mode)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            session_id,
                            current_time,
                            intersection_id,
                            light.get("id", "unknown"),
                            light.get("state", "UNKNOWN"),
                            light.get("remaining", 0),
                            is_adaptive
                        )
                    )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error recording traffic light states: {e}")
            try:
                self.local.conn.rollback()
            except:
                self.connect()
            return False

    def record_event(self, session_id: int, event_type: str, details: str = None, duration: int = None) -> bool:
        """Record emergency or accident events."""
        self.ensure_connection()
        current_time = self.get_current_time()
        try:
            self.local.cursor.execute(
                "INSERT INTO events (session_id, timestamp, event_type, details, duration) VALUES (?, ?, ?, ?, ?)",
                (session_id, current_time, event_type, details, duration)
            )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error recording event: {e}")
            try:
                self.local.conn.rollback()
            except:
                self.connect()
            return False

    def record_heatmap_data(self, session_id: int, zone_name: str, avg_intensity: float, max_intensity: float) -> bool:
        """Record heatmap intensity data for traffic density analysis."""
        self.ensure_connection()
        current_time = self.get_current_time()
        try:
            self.local.cursor.execute(
                """
                INSERT INTO heatmap_data
                (session_id, timestamp, zone_name, average_intensity, max_intensity)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, current_time, zone_name, avg_intensity, max_intensity)
            )
            self.local.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error recording heatmap data: {e}")
            try:
                self.local.conn.rollback()
            except:
                self.connect()
            return False

    def close(self):
        """Close database connection."""
        if hasattr(self.local, 'conn') and self.local.conn:
            self.local.conn.close()
            self.local.conn = None
            self.local.cursor = None

    def __del__(self):
        """Ensure database connection is closed when object is destroyed."""
        self.close()

    def get_available_sessions(self) -> List[Dict[str, Any]]:
        """Get list of all recording sessions."""
        self.ensure_connection()
        try:
            self.local.cursor.execute(
                """
                SELECT session_id, start_time, end_time, video_path, notes
                FROM sessions
                ORDER BY start_time DESC
                """
            )
            return [dict(row) for row in self.local.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Error fetching sessions: {e}")
            return []

    def get_session_stats(self, session_id: int) -> Dict[str, Any]:
        """Get statistics for a specific session."""
        self.ensure_connection()
        stats = {}
        try:
            # Get duration
            self.local.cursor.execute(
                """
                SELECT start_time, end_time FROM sessions
                WHERE session_id = ?
                """,
                (session_id,)
            )
            session_data = self.local.cursor.fetchone()
            if session_data:
                stats["start_time"] = session_data["start_time"]
                stats["end_time"] = session_data["end_time"]

            # Count vehicles
            self.local.cursor.execute(
                """
                SELECT SUM(total) as total_vehicles FROM zone_vehicle_counts
                WHERE session_id = ?
                """,
                (session_id,)
            )
            vehicle_data = self.local.cursor.fetchone()
            stats["total_vehicles"] = vehicle_data["total_vehicles"] if vehicle_data and vehicle_data["total_vehicles"] else 0

            # Count pedestrians
            self.local.cursor.execute(
                """
                SELECT SUM(count) as total_pedestrians FROM zone_pedestrian_counts
                WHERE session_id = ?
                """,
                (session_id,)
            )
            pedestrian_data = self.local.cursor.fetchone()
            stats["total_pedestrians"] = pedestrian_data["total_pedestrians"] if pedestrian_data and pedestrian_data["total_pedestrians"] else 0

            # Count events
            self.local.cursor.execute(
                """
                SELECT COUNT(*) as event_count FROM events
                WHERE session_id = ?
                """,
                (session_id,)
            )
            event_data = self.local.cursor.fetchone()
            stats["event_count"] = event_data["event_count"] if event_data else 0

            return stats
        except sqlite3.Error as e:
            logger.error(f"Error getting session stats: {e}")
            return stats
