import logging
import sys

# Create a custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)  # Console handler should log DEBUG and above

# Create a filter to only allow DEBUG messages to the console
class DebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG

console_handler.addFilter(DebugFilter())

# Create a file handler
OUTPUT_FILE = './output.txt'
file_handler = logging.FileHandler(OUTPUT_FILE, mode='w')
file_handler.setLevel(logging.INFO)  # File handler should log INFO and above

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# DEBUG INFO WARNIGN ERROR