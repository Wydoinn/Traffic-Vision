import json
import os
from typing import Dict, Any

from logger import logger

class ConfigManager:
    """
    Manages application configuration with validation and recovery capabilities.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.default_config = None
        self.current_config = None

        # Create config directory if it doesn't exist
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError as e:
                logger.error(f"Error creating config directory: {e}")

    def set_default_config(self, default_config: Dict[str, Any]):
        """Set the default configuration to use when no file exists or recovery is needed."""
        self.default_config = default_config

    def load_config(self) -> Dict[str, Any]:
        """Load configuration with validation functionality."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)

                # Verify config is valid
                if self._validate_config(config):
                    self.current_config = config
                    logger.info(f"Configuration loaded successfully from {self.config_path}")
                    return self.current_config
                else:
                    logger.warning("Invalid configuration detected, using default config")
                    return self._use_default_config()

            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading configuration: {e}")
                return self._use_default_config()
        else:
            logger.info(f"Configuration file not found at {self.config_path}, using defaults")
            return self._use_default_config()

    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save configuration with validation."""
        # Validate config before saving
        if not self._validate_config(config):
            logger.error("Cannot save invalid configuration")
            return False

        # Create directory if it doesn't exist
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except OSError as e:
                logger.error(f"Error creating config directory: {e}")
                return False

        try:
            # Save config atomically
            temp_path = f"{self.config_path}.temp"
            with open(temp_path, 'w') as f:
                json.dump(config, f, indent=4)

            # Rename the temp file to the actual config file
            if os.path.exists(self.config_path):
                os.replace(temp_path, self.config_path)
            else:
                os.rename(temp_path, self.config_path)

            self.current_config = config
            logger.info(f"Configuration saved successfully to {self.config_path}")
            return True
        except IOError as e:
            logger.error(f"Error saving configuration: {e}")
            if os.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False

    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration structure to ensure it contains all required fields.
        """
        if not isinstance(config, dict):
            return False

        # Check for required top-level sections
        required_sections = ["model_paths", "inference_settings", "heatmap_settings", "display_settings"]
        for section in required_sections:
            if section not in config:
                return False

        # If we have a default config to compare against, do deeper validation
        if self.default_config:
            try:
                self._validate_structure_match(config, self.default_config)
                return True
            except ValueError:
                return False

        return True

    def _validate_structure_match(self, config: Dict[str, Any], default: Dict[str, Any], path: str = ""):
        """Recursively validate that config has all the required keys from default."""
        for key, value in default.items():
            if key not in config:
                raise ValueError(f"Missing required key: {path}.{key}")

            # If the value is a dictionary, validate its structure too
            if isinstance(value, dict) and isinstance(config[key], dict):
                self._validate_structure_match(config[key], value, f"{path}.{key}" if path else key)

    def _use_default_config(self) -> Dict[str, Any]:
        """Use and save the default configuration."""
        if not self.default_config:
            logger.critical("No default configuration available")
            raise ValueError("Default configuration not set")

        self.current_config = self.default_config.copy()

        # Try to save the default config
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.current_config, f, indent=4)
            logger.info("Default configuration saved")
        except IOError as e:
            logger.error(f"Error saving default configuration: {e}")

        return self.current_config
