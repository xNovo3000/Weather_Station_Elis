# encoding: UTF-8

"""
Version: 0.2
Updated: 20/04/2021
Author: NetcomGroup Innovation Team
"""

from .logger import Logger

loggers: dict[str, Logger] = {}


def get_logger(name):
    if name not in loggers:
        loggers[name] = Logger(file_name=name)
    return loggers[name]
