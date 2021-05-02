# encoding: UTF-8

"""
Version: 1.0 Alpha
Updated: 02/05/2021
Author: NetcomGroup Innovation Team
"""

# PYTHON IMPORT
import json
import os

# THE ROOT
__root = os.path.join(os.path.dirname(__file__), "..", "..", "Files", "Configurations")


# LOAD FUNCTION
def load(file_name=None):
    result = {}
    if file_name:
        # TODO: ADD TRY CATCH TO CHECK IF THE FILE EXISTS
        with open(os.path.join(__root, "{}.json".format(file_name))) as file:
            result = json.load(file)
    return result
