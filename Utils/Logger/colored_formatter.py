# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON LIB IMPORT
from logging import DEBUG, INFO, WARNING, ERROR, Formatter


class ColoredFormatter(Formatter):

    def __init__(self, fmt, datefmt):
        Formatter.__init__(self)
        self.formatters = {
            DEBUG: Formatter(fmt="\033[2m" + fmt + "\033[0m", datefmt=datefmt),
            INFO: Formatter(fmt="\033[94m" + fmt + "\033[0m", datefmt=datefmt),
            WARNING: Formatter(fmt="\033[93m" + fmt + "\033[0m", datefmt=datefmt),
            ERROR: Formatter(fmt="\033[91m" + fmt + "\033[0m", datefmt=datefmt),
        }

    def format(self, record):
        return self.formatters[record.levelno].format(record)
