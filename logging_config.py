# cryptosentinator/logging_config.py
import logging
import sys

def setup_logging():
    """Configures structured logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        stream=sys.stdout,
    )