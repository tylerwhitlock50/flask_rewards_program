import os
import logging
from logging.handlers import RotatingFileHandler

# Ensure the logs directory exists
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Create a logger instance
logger = logging.getLogger("supercomp")
logger.setLevel(logging.DEBUG)

# File handler for logging
file_handler = RotatingFileHandler(
    os.path.join(log_directory, "app.log"), maxBytes=1000000, backupCount=3
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Stream handler (console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
