import time
import threading
import psutil
import platform
from typing import Dict, Any, Callable
import torch

from logger import logger

class HealthMonitor:
    """
    Monitors system health metrics like CPU usage, memory usage, GPU utilization,
    and disk space. Can trigger alerts when thresholds are exceeded.
    """
    def __init__(self, check_interval: float = 60.0):
        self.check_interval = check_interval
        self.monitoring_thread = None
        self.is_monitoring = False
        self.stop_event = threading.Event()

        # Alert thresholds
        self.thresholds = {
            "cpu": 90.0,            # CPU usage percentage
            "memory": 90.0,         # Memory usage percentage
            "disk": 90.0,           # Disk usage percentage
            "gpu_memory": 90.0,     # GPU memory usage percentage
            "temperature": 85.0,    # Temperature (celsius)
        }

        # Alert callback
        self.alert_callback = None

        # Initialize counters
        self.alert_count = 0
        self.check_count = 0
        self.last_metrics = None

    def set_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Set a callback function to be called when alerts are triggered."""
        self.alert_callback = callback

    def set_threshold(self, metric: str, value: float):
        """Set a threshold for a specific metric."""
        if metric in self.thresholds:
            self.thresholds[metric] = value

    def start_monitoring(self):
        """Start the health monitoring thread."""
        if self.is_monitoring:
            return False

        self.is_monitoring = True
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info("Health monitoring started")
        return True

    def stop_monitoring(self):
        """Stop the health monitoring thread."""
        if not self.is_monitoring:
            return False

        self.is_monitoring = False
        self.stop_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
            self.monitoring_thread = None
        logger.info("Health monitoring stopped")
        return True

    def _monitoring_loop(self):
        """Main monitoring loop that runs in the background thread."""
        while not self.stop_event.is_set():
            try:
                # Get current metrics
                metrics = self.get_system_metrics()
                self.last_metrics = metrics
                self.check_count += 1

                # Check for threshold violations and trigger alerts
                self._check_thresholds(metrics)

                # Sleep until next check, but allow for early termination
                for _ in range(int(self.check_interval / 0.1)):
                    if self.stop_event.is_set():
                        break
                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                time.sleep(5.0)  # Wait a bit before retrying

    def _check_thresholds(self, metrics: Dict[str, Any]):
        """Check if any metrics have exceeded their thresholds."""
        alerts = []

        # CPU usage
        if metrics["cpu_percent"] > self.thresholds["cpu"]:
            alerts.append(f"High CPU usage: {metrics['cpu_percent']:.1f}% (threshold: {self.thresholds['cpu']}%)")

        # Memory usage
        if metrics["memory_percent"] > self.thresholds["memory"]:
            alerts.append(f"High memory usage: {metrics['memory_percent']:.1f}% (threshold: {self.thresholds['memory']}%)")

        # Disk usage
        if metrics["disk_percent"] > self.thresholds["disk"]:
            alerts.append(f"High disk usage: {metrics['disk_percent']:.1f}% (threshold: {self.thresholds['disk']}%)")

        # GPU memory usage
        if metrics.get("gpu_memory_percent") and metrics["gpu_memory_percent"] > self.thresholds["gpu_memory"]:
            alerts.append(f"High GPU memory usage: {metrics['gpu_memory_percent']:.1f}% (threshold: {self.thresholds['gpu_memory']}%)")

        # GPU temperature
        if metrics.get("gpu_temperature") and metrics["gpu_temperature"] > self.thresholds["temperature"]:
            alerts.append(f"High GPU temperature: {metrics['gpu_temperature']:.1f}°C (threshold: {self.thresholds['temperature']}°C)")

        # Trigger alerts if necessary
        if alerts and self.alert_callback:
            self.alert_count += 1
            alert_message = "\n".join(alerts)
            logger.warning(f"Health alert: {alert_message}")
            try:
                self.alert_callback("System Health Alert", {
                    "message": alert_message,
                    "metrics": metrics,
                    "timestamp": time.time()
                })
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        metrics = {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_used": psutil.virtual_memory().used,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_total": psutil.disk_usage('/').total,
            "disk_used": psutil.disk_usage('/').used,
            "disk_free": psutil.disk_usage('/').free,
            "disk_percent": psutil.disk_usage('/').percent,
            "system": platform.system(),
            "architecture": platform.machine(),
            "python_version": platform.python_version()
        }

        # Get GPU metrics if available
        if torch.cuda.is_available():
            try:
                gpu_count = torch.cuda.device_count()
                metrics["gpu_count"] = gpu_count
                metrics["gpu_name"] = torch.cuda.get_device_name(0) if gpu_count > 0 else None

                # Get GPU memory stats
                if gpu_count > 0:
                    reserved = torch.cuda.memory_reserved(0)
                    allocated = torch.cuda.memory_allocated(0)
                    total = torch.cuda.get_device_properties(0).total_memory
                    metrics["gpu_memory_total"] = total
                    metrics["gpu_memory_reserved"] = reserved
                    metrics["gpu_memory_allocated"] = allocated
                    metrics["gpu_memory_percent"] = (allocated / total) * 100

                    # Try to get temperature on Linux with nvidia-smi
                    if platform.system() == "Linux":
                        try:
                            import subprocess
                            result = subprocess.run(
                                ['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader'],
                                capture_output=True, text=True, check=True
                            )
                            temp = float(result.stdout.strip())
                            metrics["gpu_temperature"] = temp
                        except (subprocess.SubprocessError, ValueError) as e:
                            logger.debug(f"Could not get GPU temperature: {e}")
            except Exception as e:
                logger.debug(f"Error getting GPU metrics: {e}")

        return metrics

    def get_report(self) -> Dict[str, Any]:
        """Get a report of system health and monitoring statistics."""
        report = {
            "is_monitoring": self.is_monitoring,
            "check_count": self.check_count,
            "alert_count": self.alert_count,
            "thresholds": self.thresholds.copy(),
            "current_metrics": self.get_system_metrics() if self.is_monitoring else self.last_metrics
        }
        return report
