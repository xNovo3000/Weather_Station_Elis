# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

from .logger import Logger

loggers = {}


def get_logger(name):
    if name not in loggers:
        loggers[name] = Logger(name=name)
        loggers[name].start()
    return loggers[name]


def destroy_logger(name):
    if name in loggers:
        loggers[name].join()
        loggers.pop(name)
