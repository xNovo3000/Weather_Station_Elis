# encoding: UTF-8

"""
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import logging


# QUESTA CLASSE GESTISCE LA FORMATTAZIONE DEL LOG
class CustomFormatter(logging.Formatter):

    __COLOR_DEBUG = "\033[2m"
    __COLOR_INFO = "\033[94m"
    __COLOR_WARNING = "\033[93m"
    __COLOR_ERROR = "\033[91m"
    __COLOR_RESET = "\033[0m"

    def __init__(self, fmt, datefmt, is_terminal=False):
        logging.Formatter.__init__(self)
        if is_terminal:
            self.formatters = {
                logging.DEBUG: logging.Formatter(
                    fmt=CustomFormatter.__COLOR_DEBUG + fmt + CustomFormatter.__COLOR_RESET,
                    datefmt=datefmt
                ),
                logging.INFO: logging.Formatter(
                    fmt=CustomFormatter.__COLOR_INFO + fmt + CustomFormatter.__COLOR_RESET,
                    datefmt=datefmt
                ),
                logging.WARNING: logging.Formatter(
                    fmt=CustomFormatter.__COLOR_WARNING + fmt + CustomFormatter.__COLOR_RESET,
                    datefmt=datefmt
                ),
                logging.ERROR: logging.Formatter(
                    fmt=CustomFormatter.__COLOR_ERROR + fmt + CustomFormatter.__COLOR_RESET,
                    datefmt=datefmt
                ),
            }
        else:
            self.formatters = {
                logging.DEBUG: logging.Formatter(
                    fmt=fmt,
                    datefmt=datefmt
                ),
                logging.INFO: logging.Formatter(
                    fmt=fmt,
                    datefmt=datefmt
                ),
                logging.WARNING: logging.Formatter(
                    fmt=fmt,
                    datefmt=datefmt
                ),
                logging.ERROR: logging.Formatter(
                    fmt=fmt,
                    datefmt=datefmt
                ),
            }

    def format(self, record):
        return self.formatters[record.levelno].format(record)
