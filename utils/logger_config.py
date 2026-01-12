import logging
import sys

OUTPUT_FILE = './output.txt'
SUMMARY_LEVEL = 25


class LoggerConfig:
    """
    Logger configuration class. Creates a logger and has methods that add different handlers to it.

    Attributes:
        logger - the created logger.
        formatter - defines the format for the different handlers.
    """
    def __init__(self):
        # Create a custom logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Create a formatter and add it to the handlers
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # Add a new logger level
        logging.addLevelName(SUMMARY_LEVEL, "SUMMARY")
        logging.Logger.summary = self.summary

    def output_to_file(self, logging_type):
        """
        Create and add logger handler that outputs to a .txt file.
        Args:
            logging_type: long/short
        Returns: void
        """
        if logging_type == "Short":
            level = SUMMARY_LEVEL
        else:
            level = logging.INFO
        # Create a file handler
        file_handler = logging.FileHandler(OUTPUT_FILE, mode='w')
        file_handler.setLevel(level)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def summary(self, message, *args, **kws):
        """
        defines new logger level - summary.
        """
        if self.logger.isEnabledFor(SUMMARY_LEVEL):
            self.logger._log(SUMMARY_LEVEL, message, args, **kws)

    def output_debug(self):
        """
        Create and add logger handler that outputs to the console.
        Returns: void
        """
        # Create a console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)  # Console handler should log DEBUG and above
        console_handler.addFilter(DebugFilter())
        console_handler.setFormatter(self.formatter)
        # Add the handlers to the logger
        self.logger.addHandler(console_handler)


# Create a filter to only allow DEBUG messages to the console
class DebugFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


# Creates the sole instance of class LoggerConfig
loggerConfig = LoggerConfig()
logger = loggerConfig.logger

# DEBUG INFO WARNIGN ERROR