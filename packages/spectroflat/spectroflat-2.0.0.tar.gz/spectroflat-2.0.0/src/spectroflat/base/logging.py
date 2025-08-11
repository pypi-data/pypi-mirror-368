"""
Logging module provides an interface to initialize
and use the python logger.
"""

import os
import logging


class Logging:
    """
    Facade for python logging.
    Provides easy setup and configuration methods.
    """
    LOG_NAME = 'SPFF'
    #: Default Log Format
    FORMAT = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def init_console(level: int = logging.INFO) -> None:
        """
        Init console logging.
        """
        # Create root logger with minimum supported log level
        logger = logging.getLogger(Logging.LOG_NAME)
        logger.setLevel(level)

        # create console logging handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(Logging.FORMAT)
        logger.addHandler(ch)

    @staticmethod
    def init_file(file_name: str, level: int = logging.INFO) -> None:
        """
        Init logging to a log file.
        """
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        logger = Logging.get_logger()
        fh = logging.FileHandler(file_name)
        fh.setLevel(level)
        fh.setFormatter(Logging.FORMAT)
        logger.addHandler(fh)

    @staticmethod
    def get_logger() -> logging.Logger:
        """
        Retrieve the SUSI default logger
        """
        return logging.getLogger(Logging.LOG_NAME)

    @staticmethod
    def set_log_level(level: int) -> None:
        """
        Set the logging level of the application. Per default the level is set to INFO (1).

        ### Params
         - level: (int) The level to set, where
            - 0: DEBUG
            - 1: INFO
            - 2: WARNING
            - 3: ERROR
            - 4: CRITICAL
        """
        log = Logging.get_logger()
        if level < 1:
            log.setLevel(logging.DEBUG)
        elif level < 2:
            log.setLevel(logging.INFO)
        elif level < 3:
            log.setLevel(logging.WARNING)
        elif level < 4:
            log.setLevel(logging.ERROR)
        else:
            log.setLevel(logging.CRITICAL)
