# encoding: UTF-8

"""
Version: 0.2
Updated: 29/04/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json
import os

# THE ROOT
__root = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Configurations")


# LOAD FUNCTION
def load(file_name=None, adjust=None):
    result = {}
    if file_name:
        # TODO: ADD TRY CATCH TO CHECK IF THE FILE EXISTS
        with open(os.path.join(__root, "{}.json".format(file_name))) as file:
            result = json.load(file)
        if adjust:
            result = adjust(result)
    return result
