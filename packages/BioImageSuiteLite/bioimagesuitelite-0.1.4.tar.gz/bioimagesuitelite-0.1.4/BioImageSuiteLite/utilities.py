# BioImageSuiteLite/utilities.py
import logging
import sys

def setup_logging(level=logging.INFO):
    """Configures basic logging for the application."""
    # Prevent multiple handlers if called multiple times (e.g. in interactive sessions)
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[
                logging.StreamHandler(sys.stdout)
                # You could add a FileHandler here as well:
                # logging.FileHandler("bioimagesuitelite.log")
            ]
        )
    logger = logging.getLogger("BioImageSuiteLite") # Get a specific logger for the app
    logger.info("Logging initialized.")
    return logger

# You can add other common utility functions here, e.g.,
# - Data conversion helpers
# - Parameter validation functions
# - etc.