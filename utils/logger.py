import logging
import os
from datetime import datetime
from app_config.config_loader import config_loader

class AppLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        app_config = config_loader.get_app_config()
        log_level_str = app_config.get("LOG_LEVEL", "INFO").upper()
        log_file_path = app_config.get("LOG_FILE", "logs/app.log")

        # Ensure the logs directory exists
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('ForgejoAutoSnapshotDashboard')
        self.logger.setLevel(getattr(logging, log_level_str))

        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(log_file_path)

        # Set level for handlers
        c_handler.setLevel(getattr(logging, log_level_str))
        f_handler.setLevel(getattr(logging, log_level_str))

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        if not self.logger.handlers: # Avoid adding duplicate handlers if called multiple times
            self.logger.addHandler(c_handler)
            self.logger.addHandler(f_handler)

    def get_logger(self):
        return self.logger

# Initialize the logger
app_logger = AppLogger().get_logger()