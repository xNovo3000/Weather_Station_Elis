# encoding: UTF-8

"""
Version: 0.2
Updated: 29/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json
import os


# LOAD FUNCTION
def load(file_name=None, adjust=None):
    result = {}
    if file_name:
        with open(os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Configurations", file_name)) as file:
            result = json.load(file)
        if adjust:
            result = adjust(result)
    return result
